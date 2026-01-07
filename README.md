# PDFVault – Insecure PDF Encryption & Security Testing Lab

**WARNING: FOR EDUCATIONAL PURPOSES ONLY.**
**DO NOT DEPLOY THIS APPLICATION IN A PRODUCTION ENVIRONMENT.**

## Project Overview
PDFVault is a deliberately vulnerable web application designed to demonstrate common security flaws in document handling systems. It serves as an offensive cybersecurity lab for learning about:
- Weak Encryption Implementations
- Metadata Information Leakage
- Insecure Direct Object References (IDOR)
- Broken Access Control
- Insecure File Uploads

## Threat Model & Vulnerabilities

### 1. Weak Encryption
- **Vulnerability**: The application uses insecure default settings or weak algorithms (simulated or real depending on library versions) and allows short, weak passwords.
- **Attack Vector**: An attacker can use brute-force or dictionary attacks to recover the password.
- **Learning Outcome**: Understanding the importance of strong algorithms (AES-256), salting, and key stretching (PBKDF2, Argon2).

### 2. Metadata Leakage
- **Vulnerability**: The application extracts and displays all PDF metadata without sanitization.
- **Attack Vector**: Attackers can harvest usernames, software versions, email addresses, and internal path information from the metadata.
- **Learning Outcome**: The importance of scrubbing metadata before public release of documents.

### 3. Insecure Direct Object References (IDOR) / Broken Access Control
- **Vulnerability**: The `/admin` page is publicly accessible.
- **Attack Vector**: Anyone can view the list of all uploaded files and their paths.
- **Learning Outcome**: Implementing proper authentication and authorization checks for sensitive routes.

### 4. Insecure File Upload
- **Vulnerability**: The upload validation checks only the file extension, which can be easily bypassed (e.g., `malware.php.pdf` or MIME type spoofing).
- **Attack Vector**: While this lab focuses on PDF logic, in a real scenario this could lead to Remote Code Execution (RCE).
- **Learning Outcome**: Validating file content (magic bytes) and re-encoding uploaded files.

## Setup & Usage

### Prerequisites
- Python 3.x

### Installation
1. Clone the repository or extract the files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Lab
1. Start the Flask application:
   ```bash
   python app.py
   ```
2. Navigate to `http://127.0.0.1:5000` in your browser.

## Attack Scenarios (Edu)
Check the `attacks/` directory for detailed guides on how to exploit these vulnerabilities:
- `attacks/encryption_flaws.md`
- `attacks/brute_force_attack.md`
- `attacks/metadata_leak.md`

## Ethical Disclaimer
This software is provided "as is" for educational purposes only. The author takes no responsibility for the misuse of this code. Do not use these techniques on systems you do not have explicit permission to test.
