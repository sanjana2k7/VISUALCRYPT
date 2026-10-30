# 🔐 VISUALCRYPT
### Secure Image Encryption and Two-Share Visual Cryptography System

VISUALCRYPT is a secure image-sharing application developed as a Cryptography Project Based Learning (PBL) project. It combines password-based image encryption with a two-share visual cryptography technique to protect digital images during sharing.

The application encrypts an uploaded image, generates two separate visual shares, and allows the original image to be reconstructed using both shares and the correct password.

## 🚀 Key Features

- **Image Encryption:** Protects uploaded images using AES-256-GCM encryption.
- **Password Protection:** Uses PBKDF2-HMAC-SHA-256 for password-based key derivation.
- **Visual Share Generation:** Creates two separate PNG visual shares.
- **Secure Image Recovery:** Reconstructs and decrypts the original image using both shares.
- **Image Preview:** Displays the selected and recovered images.
- **Download Options:** Allows users to download the generated shares and encrypted image.
- **Interactive Dashboard:** Provides separate interfaces for encryption and image recovery.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application interface |
| Cryptography | Encryption and decryption |
| AES-256-GCM | Authenticated image encryption |
| PBKDF2-HMAC-SHA-256 | Password-based key derivation |
| Pillow (PIL) | Image processing |
| NumPy | Image and array operations |

## ⚙️ How It Works

### 1. Encrypt
- Upload an image.
- Enter and confirm a password.
- Encrypt the image using AES-256-GCM.

### 2. Split
- Generate two separate visual shares.
- Download both PNG share files.
- Keep both shares safely.

### 3. Recover
- Upload Share 01 and Share 02.
- Enter the original password.
- Reconstruct and decrypt the image.
- View the recovered original image.

## 📥 Installation and Execution

### Prerequisites
- Python 3.10 or later
- pip package manager

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### Step 2: Navigate to the Project Directory

```bash
cd VISUALCRYPT
```

### Step 3: Install Dependencies

```bash
pip install streamlit cryptography pillow numpy
```

Alternatively, if a requirements.txt file is provided:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal to access VISUALCRYPT.

*Note: Replace app.py with the actual Streamlit entry-point filename if it differs.*

## 🔒 Security Notes

- Both visual shares are required for image recovery.
- The correct password is necessary for successful decryption.
- Keep the password separate from the share files.
- Avoid modifying or recompressing the generated share images.
- This project is an academic prototype and should undergo independent security testing before production use.

## 🎯 Project Objective

The primary objective of VISUALCRYPT is to demonstrate how cryptographic encryption and visual cryptography can be combined to provide an additional layer of protection for digital image sharing.

## 👩‍💻 Project Information

**Project Name:** VISUALCRYPT  
**Domain:** Cryptography and Cyber Security  
**Project Type:** Project Based Learning (PBL)  
**Department:** CSE – Cyber Security  
**Institution:** Geethanjali College of Engineering and Technology

## 📌 Future Enhancements

- Support for additional image formats.
- Improved recovery and error handling.
- Enhanced user authentication.
- Secure deployment and accessibility improvements.

---

**VISUALCRYPT — Simple. Secure. Shareable.** 🔐
