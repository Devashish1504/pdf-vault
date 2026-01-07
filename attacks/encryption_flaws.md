# Encryption Vulnerabilities in PDFVault

## The Flaw
The PDFVault application uses weak default settings when encrypting PDFs. In many older or default implementations (like PyPDF2's legacy defaults or when specifically downgraded), the encryption might use RC4 (40-bit or 128-bit) or have weak key derivation functions.

Even if stronger algorithms like AES are used, the *implementation* here allows for:
1. **Short, Predictable Passwords**: The application does not enforce password complexity. Users often choose "123456" or "password".
2. **No Salt or Publicly Known Salt**: While not explicitly visible in the UI, weak implementations often lack proper salting, making rainbow table attacks feasible if the algorithm is weak enough.

## Exploitation
An attacker getting access to the `enc_filename.pdf` (which causes `enc_` to appear in the filename, revealing it's encrypted) can attempt to crack the password.

### Tools
- `pdfcrack`
- `hashcat`
- `john the ripper`

### Example Command (John the Ripper)
First, extract the hash:
```bash
./pdf2john.pl enc_document.pdf > hash.txt
```

Then crack it:
```bash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

## Remediation
- Use **AES-256** encryption.
- Enforce **strong passwords** (min 12 chars, mixed case, special chars).
- Use **PBKDF2** or **Argon2** for key derivation with a unique, random salt for every file.
