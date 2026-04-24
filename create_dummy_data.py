
"""
Generates fake bid documents as images for testing.
Run: python3 create_dummy_data.py
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import os

def make_text_image(text_lines, filename, blur=False, noise=False, rotate=0):
    img = Image.new("RGB", (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y = 40
    for line in text_lines:
        draw.text((40, y), line, fill=(0, 0, 0))
        y += 32

    # Convert to OpenCV format
    img_cv = np.array(img)

    # Simulate bad scan: blur
    if blur:
        img_cv = cv2.GaussianBlur(img_cv, (7, 7), 0)
        # Add noise
        noise_arr = np.random.randint(0, 60, img_cv.shape, dtype=np.uint8)
        img_cv = cv2.add(img_cv, noise_arr)

    # Simulate rotation (crooked scan)
    if rotate != 0:
        h, w = img_cv.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), rotate, 1.0)
        img_cv = cv2.warpAffine(img_cv, M, (w, h), borderValue=(255, 255, 255))

    cv2.imwrite(filename, img_cv)
    print(f"  Created: {filename}")

# --- Perfect Bid ---
make_text_image([
    "COMPANY: Sharma Construction Pvt. Ltd.",
    "GST Number: 27AABCS1429B1Z1",
    "Annual Turnover: Rs. 8.5 Crore (FY 2023-24)",
    "ISO Certification: ISO 9001:2015 (Valid till Dec 2025)",
    "Projects Completed (Last 5 Years): 5",
    "Project 1: CRPF Barracks, Delhi - Rs. 3.2 Cr",
    "Project 2: PWD Road, UP - Rs. 2.1 Cr",
    "PAN: AABCS1429B",
    "Registered Address: 12, Industrial Area, Mumbai",
], "data/perfect_bids/sharma_construction.png")

# --- Blurry/Scanned Bid ---
make_text_image([
    "COMPANY: Gupta Infra Works",
    "GST Number: 09AACFG2310C1ZK",
    "Annual Turnover: Rs. 6.0 Crore",
    "ISO Certification: ISO 9001 (Attached separately)",
    "Projects Completed: 3",
    "Project 1: State Highway, Lucknow",
    "PAN: AACFG2310C",
], "data/blurry_bids/gupta_infra.png", blur=True, rotate=4)

# --- Missing Data Bid ---
make_text_image([
    "COMPANY: Verma Builders",
    "GST Number: NOT PROVIDED",
    "Annual Turnover: Rs. 3.8 Crore",   # Below threshold
    "ISO Certification: Applied for",    # Not yet valid
    "Projects Completed: 1",             # Below threshold
    "PAN: AABCV1234D",
], "data/missing_data_bids/verma_builders.png")

print("\nDummy data created successfully!")