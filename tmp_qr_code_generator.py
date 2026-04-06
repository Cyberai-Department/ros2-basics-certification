"""
generate_qr_codes.py
─────────────────────────────────────────────────────────────────────
Generates a simple QR code PNG for every student in certificates.json.

Requirements (install once):
    pip install qrcode[pil] pillow

Usage:
    python generate_qr_codes.py

    ► Place this script in the same folder as certificates.json
    ► A qr_codes/ folder will be created automatically
─────────────────────────────────────────────────────────────────────
"""

import json
import os
import re
import qrcode
from PIL import Image, ImageDraw, ImageFont

BASE_URL      = "https://cyberai-department.github.io/ros2-basics-certification/index.html"
JSON_FILE     = "certificates.json"
OUTPUT_FOLDER = "qr_codes"


def safe_filename(text):
    return re.sub(r'[^A-Za-z0-9_\-]', '_', text)


def try_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make_qr(cert):
    url = f"{BASE_URL}?certificate_id={cert['certificate_id']}"
    name    = cert.get("student_name", "Unknown")
    cert_id = cert.get("certificate_id", "")

    # Generate QR
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    QR_W, QR_H = qr_img.size

    # Text area below QR
    f_name = try_font(22)
    f_id   = try_font(16)
    TEXT_H = 70  # space for name + id + padding

    # Final image
    final_w = QR_W
    final_h = QR_H + TEXT_H
    img = Image.new("RGB", (final_w, final_h), "white")
    img.paste(qr_img, (0, 0))

    d = ImageDraw.Draw(img)

    # Student name
    tw = d.textlength(name, font=f_name)
    d.text(((final_w - tw) / 2, QR_H + 10), name, font=f_name, fill="black")

    # Certificate ID
    tw = d.textlength(cert_id, font=f_id)
    d.text(((final_w - tw) / 2, QR_H + 40), cert_id, font=f_id, fill="#555555")

    return img


def main():
    if not os.path.exists(JSON_FILE):
        print(f"ERROR: '{JSON_FILE}' not found.")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        certs = json.load(f)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"Found {len(certs)} certificate(s). Generating QR codes...\n")

    for cert in certs:
        cert_id  = cert.get("certificate_id", "UNKNOWN")
        name     = cert.get("student_name", "Unknown")
        filename = f"qr_{safe_filename(cert_id)}_{safe_filename(name)}.png"
        out_path = os.path.join(OUTPUT_FOLDER, filename)

        try:
            img = make_qr(cert)
            img.save(out_path, "PNG")
            print(f"  ✓  {filename}")
        except Exception as e:
            print(f"  ✗  {cert_id} — ERROR: {e}")

    print(f"\nDone! QR codes saved to: ./{OUTPUT_FOLDER}/")


if __name__ == "__main__":
    main()
