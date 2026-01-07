import os
import base64
import requests
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter
import pikepdf
from dotenv import load_dotenv
from functools import wraps
import io

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'pdf'}
CONVEX_URL = os.getenv('CONVEX_URL', '')
CLERK_PUBLISHABLE_KEY = os.getenv('CLERK_PUBLISHABLE_KEY', '')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    """Get current user from session"""
    return session.get('user')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            flash('Please login to access this feature')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_folder(user_id):
    """Get or create user-specific folder"""
    if user_id:
        folder = os.path.join(UPLOAD_FOLDER, user_id)
    else:
        folder = os.path.join(UPLOAD_FOLDER, 'guest')
    os.makedirs(folder, exist_ok=True)
    return folder

def get_user_processed_folder(user_id):
    """Get or create user-specific processed folder"""
    if user_id:
        folder = os.path.join(PROCESSED_FOLDER, user_id)
    else:
        folder = os.path.join(PROCESSED_FOLDER, 'guest')
    os.makedirs(folder, exist_ok=True)
    return folder

@app.context_processor
def inject_user():
    return {'current_user': get_current_user(), 'clerk_key': CLERK_PUBLISHABLE_KEY}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/auth/callback', methods=['POST'])
def auth_callback():
    """Handle Clerk authentication callback"""
    data = request.json
    if data and data.get('userId'):
        session['user'] = {
            'id': data.get('userId'),
            'email': data.get('email', ''),
            'name': data.get('name', 'User')
        }
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    user = get_current_user()
    user_id = user['id'] if user else None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            if user_id:
                # Logged in user - save to user folder
                user_folder = get_user_folder(user_id)
                file.save(os.path.join(user_folder, filename))
                flash(f'Uploaded: {filename}')
            else:
                # Guest user - save temporarily
                guest_folder = get_user_folder(None)
                file.save(os.path.join(guest_folder, filename))
                flash(f'Uploaded (Guest): {filename} - Login to save permanently')
            
            return redirect(url_for('index'))
        else:
            flash('Only PDF files are allowed')
    return render_template('upload.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt_pdf():
    user = get_current_user()
    user_id = user['id'] if user else None
    user_folder = get_user_folder(user_id)
    processed_folder = get_user_processed_folder(user_id)
    
    if request.method == 'POST':
        filename = request.form.get('filename')
        password = request.form.get('password')
        filepath = os.path.join(user_folder, filename)
        
        if not os.path.exists(filepath):
            flash('File not found')
            return redirect(request.url)

        try:
            reader = PdfReader(filepath)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            
            output_filename = f"enc_{filename}"
            output_path = os.path.join(processed_folder, output_filename)
            
            with open(output_path, "wb") as f:
                writer.write(f)
                
            flash(f'Encrypted: {output_filename}')
            uploaded_files = os.listdir(user_folder) if os.path.exists(user_folder) else []
            return render_template('encrypt.html', download_file=output_filename, uploaded_files=uploaded_files)
        except Exception as e:
            flash(f'Error: {str(e)}')
            
    uploaded_files = os.listdir(user_folder) if os.path.exists(user_folder) else []
    return render_template('encrypt.html', uploaded_files=uploaded_files)

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_pdf():
    user = get_current_user()
    user_id = user['id'] if user else None
    user_folder = get_user_folder(user_id)
    processed_folder = get_user_processed_folder(user_id)
    
    if request.method == 'POST':
        filename = request.form.get('filename')
        password = request.form.get('password')
        
        filepath = os.path.join(processed_folder, filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(user_folder, filename)
            if not os.path.exists(filepath):
                flash('File not found')
                return redirect(request.url)

        try:
            with pikepdf.open(filepath, password=password) as pdf:
                flash('Success! Password is correct.')
                processed_files = os.listdir(processed_folder) if os.path.exists(processed_folder) else []
                uploaded_files = os.listdir(user_folder) if os.path.exists(user_folder) else []
                return render_template('decrypt.html', success=True, password=password, processed_files=processed_files, uploaded_files=uploaded_files)
        except pikepdf.PasswordError:
            flash('Incorrect password')
        except Exception as e:
            flash(f'Error: {str(e)}')

    processed_files = os.listdir(processed_folder) if os.path.exists(processed_folder) else []
    uploaded_files = os.listdir(user_folder) if os.path.exists(user_folder) else []
    return render_template('decrypt.html', processed_files=processed_files, uploaded_files=uploaded_files)

@app.route('/metadata', methods=['GET', 'POST'])
def extract_metadata():
    user = get_current_user()
    user_id = user['id'] if user else None
    user_folder = get_user_folder(user_id)
    
    metadata = None
    if request.method == 'POST':
        filename = request.form.get('filename')
        filepath = os.path.join(user_folder, filename)
        
        if os.path.exists(filepath):
            try:
                reader = PdfReader(filepath)
                doc_info = reader.metadata
                if doc_info:
                    metadata = {k: v for k, v in doc_info.items()}
                else:
                    flash('No metadata found')
            except Exception as e:
                flash(f'Error: {str(e)}')
        else:
            flash('File not found')
            
    uploaded_files = os.listdir(user_folder) if os.path.exists(user_folder) else []
    return render_template('metadata.html', metadata=metadata, uploaded_files=uploaded_files)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == os.getenv('ADMIN_PASSWORD', 'admin'):
            session['admin_authenticated'] = True
            flash('Admin access granted')
        else:
            flash('Incorrect password')
            return render_template('admin_login.html')
    
    if not session.get('admin_authenticated'):
        return render_template('admin_login.html')
    
    # Show all users' files
    all_uploads = {}
    all_processed = {}
    
    if os.path.exists(UPLOAD_FOLDER):
        for user_folder in os.listdir(UPLOAD_FOLDER):
            folder_path = os.path.join(UPLOAD_FOLDER, user_folder)
            if os.path.isdir(folder_path):
                all_uploads[user_folder] = os.listdir(folder_path)
    
    if os.path.exists(PROCESSED_FOLDER):
        for user_folder in os.listdir(PROCESSED_FOLDER):
            folder_path = os.path.join(PROCESSED_FOLDER, user_folder)
            if os.path.isdir(folder_path):
                all_processed[user_folder] = os.listdir(folder_path)
    
    return render_template('admin.html', all_uploads=all_uploads, all_processed=all_processed)

@app.route('/download/<folder>/<user_id>/<filename>')
def download_file(folder, user_id, filename):
    user = get_current_user()
    current_user_id = user['id'] if user else 'guest'
    
    # Users can only download their own files (or admin)
    if current_user_id != user_id and not session.get('admin_authenticated'):
        flash('Access denied')
        return redirect(url_for('index'))
    
    if folder == 'uploads':
        return send_from_directory(os.path.join(UPLOAD_FOLDER, user_id), filename)
    elif folder == 'processed':
        return send_from_directory(os.path.join(PROCESSED_FOLDER, user_id), filename)
    return "Invalid", 400

@app.route('/my-files')
def my_files():
    user = get_current_user()
    if not user:
        flash('Please login to view your files')
        return redirect(url_for('login'))
    
    user_id = user['id']
    user_folder = get_user_folder(user_id)
    processed_folder = get_user_processed_folder(user_id)
    
    uploads = os.listdir(user_folder) if os.path.exists(user_folder) else []
    processed = os.listdir(processed_folder) if os.path.exists(processed_folder) else []
    
    return render_template('my_files.html', uploads=uploads, processed=processed, user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
