import os
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter
import pikepdf
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'Uploaded: {filename}')
            return redirect(url_for('index'))
        else:
            flash('Only PDF files are allowed')
    return render_template('upload.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt_pdf():
    if request.method == 'POST':
        filename = request.form.get('filename')
        password = request.form.get('password')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
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
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            
            with open(output_path, "wb") as f:
                writer.write(f)
                
            flash(f'Encrypted successfully: {output_filename}')
            uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
            return render_template('encrypt.html', download_file=output_filename, uploaded_files=uploaded_files)
        except Exception as e:
            flash(f'Error: {str(e)}')
            
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('encrypt.html', uploaded_files=uploaded_files)

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_pdf():
    if request.method == 'POST':
        filename = request.form.get('filename')
        password = request.form.get('password')
        
        filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(filepath):
                flash('File not found')
                return redirect(request.url)

        try:
            with pikepdf.open(filepath, password=password) as pdf:
                flash(f'Success! Password is correct.')
                processed_files = os.listdir(app.config['PROCESSED_FOLDER'])
                uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
                return render_template('decrypt.html', success=True, password=password, processed_files=processed_files, uploaded_files=uploaded_files)
        except pikepdf.PasswordError:
            flash('Incorrect password')
        except Exception as e:
            flash(f'Error: {str(e)}')

    processed_files = os.listdir(app.config['PROCESSED_FOLDER'])
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('decrypt.html', processed_files=processed_files, uploaded_files=uploaded_files)

@app.route('/metadata', methods=['GET', 'POST'])
def extract_metadata():
    metadata = None
    if request.method == 'POST':
        filename = request.form.get('filename')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
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
            
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('metadata.html', metadata=metadata, uploaded_files=uploaded_files)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    from flask import session
    
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
    
    uploads = os.listdir(app.config['UPLOAD_FOLDER'])
    processed = os.listdir(app.config['PROCESSED_FOLDER'])
    return render_template('admin.html', uploads=uploads, processed=processed)

@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    if folder == 'uploads':
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    elif folder == 'processed':
        return send_from_directory(app.config['PROCESSED_FOLDER'], filename)
    return "Invalid", 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
