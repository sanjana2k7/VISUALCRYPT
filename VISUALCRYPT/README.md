# VISUALCRYPT

A simple image encryption and two-share recovery demonstration.

## Features
- Upload a PNG/JPG/JPEG image
- Encrypt the original file using AES-256-GCM
- Derive the encryption key from a user password with PBKDF2-HMAC-SHA256
- Generate two visual share PNG files
- Upload both shares and the password to reconstruct and decrypt the original image

## Run on Windows

1. Install Python 3.10 or newer.
2. Extract this ZIP.
3. Open Command Prompt in the `VISUALCRYPT` folder.
4. Run:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

## Important
- Both matching share images and the correct password are required.
- Keep your password and both shares safe.
- This is an educational prototype, not a substitute for a professionally audited secure file-sharing product.
