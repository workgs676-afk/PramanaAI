
"""
vision.py — Image pre-processing for scanned/blurry bid documents.
Fixes contrast, deskews, and prepares images for OCR.

Usage:
    python3 vision.py path/to/image.png
"""
import cv2
import numpy as np
import sys
import os


def load_image(path: str) -> np.ndarray:
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {path}")
    return img


def to_grayscale(img: np.ndarray) -> np.ndarray:
    """Convert BGR image to grayscale."""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def enhance_contrast(gray: np.ndarray) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).
    Much better than simple thresholding for uneven lighting.
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def binarize(enhanced: np.ndarray) -> np.ndarray:
    """
    Otsu's binarization: automatically finds the best threshold.
    Produces clean black-on-white image ideal for OCR.
    """
    _, binary = cv2.threshold(
        enhanced, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return binary


def deskew(binary: np.ndarray) -> np.ndarray:
    """
    Detect and correct rotation (crooked scans).
    Uses Hough Line Transform to find the dominant angle.
    """
    # Find edges
    edges = cv2.Canny(binary, 50, 150, apertureSize=3)

    # Detect lines
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

    if lines is None:
        return binary  # No rotation detected, return as-is

    # Calculate dominant angle
    angles = []
    for line in lines[:20]:  # Use top 20 lines only
        rho, theta = line[0]
        angle = (theta * 180 / np.pi) - 90
        if -45 < angle < 45:
            angles.append(angle)

    if not angles:
        return binary

    median_angle = float(np.median(angles))

    if abs(median_angle) < 0.5:
        return binary  # Negligible skew, skip

    print(f"  Deskew: correcting {median_angle:.2f}° rotation")

    h, w = binary.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    deskewed = cv2.warpAffine(
        binary, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )
    return deskewed


def denoise(binary: np.ndarray) -> np.ndarray:
    """Remove small noise specks using morphological opening."""
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    return cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)


def preprocess_image(image_path: str, save_debug: bool = False) -> np.ndarray:
    """
    Full pre-processing pipeline.
    Returns a clean binary numpy array ready for OCR.
    """
    print(f"\n[vision.py] Pre-processing: {image_path}")

    img     = load_image(image_path)
    gray    = to_grayscale(img)
    enhanced = enhance_contrast(gray)
    binary  = binarize(enhanced)
    deskewed = deskew(binary)
    clean   = denoise(deskewed)

    if save_debug:
        debug_path = image_path.replace(".", "_processed.")
        cv2.imwrite(debug_path, clean)
        print(f"  Debug image saved: {debug_path}")

    print("  Pre-processing complete.")
    return clean


# ── Run standalone ────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 vision.py <image_path> [--debug]")
        sys.exit(1)

    path = sys.argv[1]
    debug = "--debug" in sys.argv
    processed = preprocess_image(path, save_debug=debug)
    print(f"  Output shape: {processed.shape} (height x width)")
