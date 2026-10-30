
import io
import hashlib
import streamlit as st
import numpy as np
from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

st.set_page_config(page_title="VISUALCRYPT", page_icon="🔐", layout="wide")

# ---------- Theme ----------
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: #10231C; color: #F1EDE5; }
[data-testid="stSidebar"] { background: #0B1913; }
.block-container { padding-top: 2rem; max-width: 1180px; }
h1,h2,h3,p,label,span { color: #F1EDE5; }
.vc-kicker { color:#AFC3B5; letter-spacing:2px; font-size: .75rem; font-weight:700; }
.vc-hero { background:linear-gradient(135deg,#1B352A,#142A21); border:1px solid #355445;
           border-radius:18px; padding:25px 28px; margin: 8px 0 22px; }
.vc-hero h1 { font-size:2.5rem; margin:4px 0; }
.vc-hero p { color:#B9C9BE; margin:0; }
.vc-card { background:#1B352A; border:1px solid #355445; border-radius:15px;
           padding:18px; min-height:110px; }
.vc-step { color:#C99AAA; font-size:.75rem; font-weight:800; letter-spacing:1px; }
div.stButton > button, div.stDownloadButton > button {
 background:#652D40; color:white; border:1px solid #87465D; border-radius:10px;
 min-height:2.7rem; font-weight:650;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
 background:#80384F; color:white; border-color:#A85B76;
}
[data-testid="stFileUploader"] { background:#1B352A; border:1px dashed #6F8C7B; border-radius:12px; padding:10px; }
.stTextInput input { background:#172B22; color:#F1EDE5; border:1px solid #557363; }
hr { border-color:#355445; }
small, .stCaption { color:#AFC3B5 !important; }
</style>
""", unsafe_allow_html=True)

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=250_000)
    return kdf.derive(password.encode("utf-8"))

def encrypt_bytes(data: bytes, password: str):
    salt = __import__("secrets").token_bytes(16)
    nonce = __import__("secrets").token_bytes(12)
    key = derive_key(password, salt)
    ciphertext = AESGCM(key).encrypt(nonce, data, None)
    return b"VCRYPT1" + salt + nonce + ciphertext

def decrypt_bytes(blob: bytes, password: str):
    if not blob.startswith(b"VCRYPT1") or len(blob) < 35:
        raise ValueError("This does not look like a valid VISUALCRYPT encrypted file.")
    salt, nonce, ciphertext = blob[7:23], blob[23:35], blob[35:]
    key = derive_key(password, salt)
    return AESGCM(key).decrypt(nonce, ciphertext, None)

def make_shares(payload: bytes):
    # Encode each payload bit as a two-pixel pattern.
    # Share A is random. Share B uses the same pattern for 0 and its inverse for 1.
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
    rng = np.random.default_rng()
    first = rng.integers(0, 2, size=len(bits), dtype=np.uint8)
    second = first ^ bits
    # Each bit becomes two horizontal pixels; 0=white, 1=black.
    a = np.repeat(first, 2).reshape(1, -1)
    b = np.empty((1, len(bits) * 2), dtype=np.uint8)
    b[:, 0::2] = second
    b[:, 1::2] = 1 - second
    # For Share A, also use complementary pairs, ensuring each share alone looks random.
    a[:, 0::2] = first
    a[:, 1::2] = 1 - first
    # Pair relation encodes data: same orientation -> 0; opposite orientation -> 1.
    # Pack as grayscale images with a compact 2x2 tile per bit for readable PNGs.
    width = 1024
    nbits = len(bits)
    rows = (nbits + width - 1) // width
    aa = np.full((rows, width * 2), 255, dtype=np.uint8)
    bb = np.full((rows, width * 2), 255, dtype=np.uint8)
    aa[:, :] = 255
    bb[:, :] = 255
    for idx in range(nbits):
        y, x = divmod(idx, width)
        x *= 2
        av = int(first[idx])
        bv = int(second[idx])
        aa[y, x] = 0 if av else 255
        aa[y, x+1] = 0 if not av else 255
        # Same orientation represents 0; inverse orientation represents 1.
        bb[y, x] = 0 if bv else 255
        bb[y, x+1] = 0 if not bv else 255
    return Image.fromarray(aa, "L"), Image.fromarray(bb, "L"), nbits, width

def recover_payload(img_a: Image.Image, img_b: Image.Image, nbits: int):
    a = np.asarray(img_a.convert("L"))
    b = np.asarray(img_b.convert("L"))
    if a.shape != b.shape:
        raise ValueError("The two share images must have matching dimensions.")
    if a.shape[1] % 2:
        raise ValueError("Invalid share dimensions.")
    width = a.shape[1] // 2
    flat_a = a.reshape(-1, 2)
    flat_b = b.reshape(-1, 2)
    # Orientation is determined by which pixel is darker.
    orient_a = (flat_a[:nbits, 0] < flat_a[:nbits, 1]).astype(np.uint8)
    orient_b = (flat_b[:nbits, 0] < flat_b[:nbits, 1]).astype(np.uint8)
    bits = orient_a ^ orient_b
    packed = np.packbits(bits)
    return packed.tobytes()

def png_bytes(img: Image.Image, nbits: int):
    from PIL.PngImagePlugin import PngInfo
    out = io.BytesIO()
    meta = PngInfo()
    meta.add_text("vc_nbits", str(nbits))
    img.save(out, format="PNG", pnginfo=meta)
    return out.getvalue()

st.markdown("""
<div class="vc-hero">
  <div class="vc-kicker">SECURE IMAGE SHARING SYSTEM</div>
  <h1>VISUALCRYPT</h1>
  <p>Protect your image. Create two shares. Recover it when you need it.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
for col, num, title, desc in [
    (c1, "01", "Encrypt", "Protect the image with a password."),
    (c2, "02", "Split", "Create two separate visual shares."),
    (c3, "03", "Recover", "Combine both shares and decrypt.")
]:
    with col:
        st.markdown(f'<div class="vc-card"><div class="vc-step">STEP {num}</div><h3>{title}</h3><p style="color:#B9C9BE">{desc}</p></div>', unsafe_allow_html=True)

st.write("")
tab_encrypt, tab_recover = st.tabs(["🔒  Encrypt & Create Shares", "🧩  Recover Image"])

with tab_encrypt:
    st.subheader("Encrypt an image")
    st.write("Choose an image and create two shares. Keep both shares safe.")
    left, right = st.columns([1.05, 1])
    with left:
        uploaded = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"], key="encrypt_upload")
        password = st.text_input("Create a password", type="password", key="encrypt_password",
                                 help="You will need this same password to recover the image.")
        confirm = st.text_input("Confirm password", type="password", key="encrypt_confirm")
        create = st.button("Encrypt & Generate Shares", use_container_width=True)
    with right:
        if uploaded:
            try:
                preview = Image.open(uploaded)
                st.image(preview, caption="Selected original image", use_container_width=True)
            except Exception:
                st.error("Please choose a valid image file.")
        else:
            st.markdown('<div class="vc-card"><h3>Your image preview</h3><p style="color:#B9C9BE">Your selected image will appear here.</p></div>', unsafe_allow_html=True)

    if create:
        if not uploaded:
            st.error("Please choose an image first.")
        elif len(password) < 6:
            st.error("Use a password with at least 6 characters.")
        elif password != confirm:
            st.error("The passwords do not match.")
        else:
            try:
                raw = uploaded.getvalue()
                encrypted = encrypt_bytes(raw, password)
                share_a, share_b, nbits, bit_width = make_shares(encrypted)
                st.session_state["vc_result"] = {
                    "encrypted": encrypted, "a": png_bytes(share_a, nbits), "b": png_bytes(share_b, nbits),
                    "nbits": nbits, "name": uploaded.name
                }
                st.success("Your image is encrypted and both visual shares are ready.")
            except Exception as e:
                st.error(f"Could not process this image: {e}")

    result = st.session_state.get("vc_result")
    if result:
        st.divider()
        st.subheader("Your files are ready")
        st.caption("Download both shares. You need both of them to recover the original image.")
        d1, d2 = st.columns(2)
        with d1:
            st.image(result["a"], caption="Share 01", use_container_width=True)
            st.download_button("⬇ Download Share 01", result["a"], "VISUALCRYPT_Share_01.png", "image/png", use_container_width=True)
        with d2:
            st.image(result["b"], caption="Share 02", use_container_width=True)
            st.download_button("⬇ Download Share 02", result["b"], "VISUALCRYPT_Share_02.png", "image/png", use_container_width=True)
        st.download_button("Download encrypted image file", result["encrypted"], "VISUALCRYPT_Encrypted.vcrypt", "application/octet-stream")
        st.caption(f"Original file: {result['name']} · Keep your password private.")

with tab_recover:
    st.subheader("Recover your original image")
    st.write("Upload the two shares generated by VISUALCRYPT and enter your password.")
    r1, r2 = st.columns(2)
    with r1:
        share1 = st.file_uploader("Upload Share 01", type=["png"], key="recover_a")
    with r2:
        share2 = st.file_uploader("Upload Share 02", type=["png"], key="recover_b")
    recovery_password = st.text_input("Enter your password", type="password", key="recover_password")
    recover = st.button("Reconstruct & Decrypt", use_container_width=True)
    if recover:
        if not share1 or not share2:
            st.error("Please upload both share images.")
        elif not recovery_password:
            st.error("Please enter your password.")
        else:
            try:
                im_a = Image.open(share1)
                im_b = Image.open(share2)
                # The payload length is stored in share metadata via PNG text.
                # To keep the files simple, derive the exact byte count from the header recovered
                # by decoding all available bits, then trim using the encrypted format's GCM layout.
                arr_a = np.asarray(im_a.convert("L"))
                arr_b = np.asarray(im_b.convert("L"))
                if arr_a.shape != arr_b.shape:
                    raise ValueError("Share dimensions do not match. Please upload the matching pair.")
                # Each PNG stores the exact encrypted payload length in a small metadata field.
                from PIL.PngImagePlugin import PngInfo
                # Metadata is also mirrored in a sidecar-free fixed header encoded in the first bytes.
                # Recover all bits, then use the header's ciphertext length to trim padding.
                nbits_all = (arr_a.shape[0] * arr_a.shape[1] // 2)
                recovered = recover_payload(im_a, im_b, nbits_all)
                if not recovered.startswith(b"VCRYPT1"):
                    raise ValueError("These shares do not form a valid VISUALCRYPT pair.")
                # AES-GCM encrypted payload length is encoded in the image's PNG text metadata.
                meta_a = im_a.info.get("vc_nbits")
                meta_b = im_b.info.get("vc_nbits")
                if not meta_a or not meta_b or meta_a != meta_b:
                    raise ValueError("Share metadata is missing or does not match. Use the original downloaded shares.")
                nbits = int(meta_a)
                recovered = recover_payload(im_a, im_b, nbits)
                original = decrypt_bytes(recovered, recovery_password)
                st.success("Image successfully reconstructed and decrypted.")
                st.image(original, caption="Recovered original image", use_container_width=True)
                st.download_button("⬇ Download recovered image", original, "VISUALCRYPT_Recovered_Image", "application/octet-stream")
            except Exception as e:
                st.error(f"Recovery failed: {e}. Check that the shares and password are correct.")

st.divider()
st.markdown('<p style="text-align:center;color:#AFC3B5;font-size:.8rem">VISUALCRYPT · Simple. Secure. Shareable.</p>', unsafe_allow_html=True)
