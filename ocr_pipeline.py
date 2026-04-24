
"""
ocr_pipeline.py — Core OCR function.

Takes an image path or pre-processed numpy array.
Returns:
  - clean_text: str  (full page text)
  - bounding_boxes: list of dicts with text + X/Y coordinates

Usage:
    python3 ocr_pipeline.py path/to/image.png
    python3 ocr_pipeline.py path/to/document.pdf
"""
import sys
import os
import json
import numpy as np
import easyocr
from pdf2image import convert_from_path
from vision import preprocess_image


# Initialise EasyOCR once (downloads model on first run ~300MB)
print("[OCR] Loading EasyOCR model (first run downloads ~300MB)...")
READER = easyocr.Reader(['en'], gpu=False)
print("[OCR] Model ready.")


def ocr_from_array(img_array: np.ndarray) -> tuple[str, list[dict]]:
    """
    Run EasyOCR on a pre-processed numpy image array.

    Returns
    -------
    clean_text : str
        All detected text joined into readable lines.
    bounding_boxes : list[dict]
        Each dict has:
          text       — the recognised string
          confidence — float 0–1
          x_min, y_min, x_max, y_max — pixel coordinates (top-left / bottom-right)
          bbox_raw   — original EasyOCR polygon [[x,y], [x,y], [x,y], [x,y]]
    """
    results = READER.readtext(img_array)

    bounding_boxes = []
    lines = []

    for (bbox, text, confidence) in results:
        # bbox = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] (polygon corners)
        xs = [pt[0] for pt in bbox]
        ys = [pt[1] for pt in bbox]

        box = {
            "text":       text,
            "confidence": round(float(confidence), 4),
            "x_min":      int(min(xs)),
            "y_min":      int(min(ys)),
            "x_max":      int(max(xs)),
            "y_max":      int(max(ys)),
            "bbox_raw":   [[int(x), int(y)] for x, y in bbox],
        }
        bounding_boxes.append(box)
        lines.append(text)

    clean_text = "\n".join(lines)
    return clean_text, bounding_boxes


def ocr_from_image(image_path: str) -> tuple[str, list[dict]]:
    """Pre-process then OCR a single image file."""
    processed = preprocess_image(image_path)
    return ocr_from_array(processed)


def ocr_from_pdf(pdf_path: str, dpi: int = 200) -> tuple[str, list[dict]]:
    """
    Convert each PDF page to an image, pre-process, then OCR.
    Returns combined text and bounding boxes across all pages.
    """
    print(f"[OCR] Converting PDF to images: {pdf_path}")
    pages = convert_from_path(pdf_path, dpi=dpi)
    print(f"  Found {len(pages)} page(s)")

    all_text = []
    all_boxes = []
    y_offset = 0  # stack pages vertically for coordinate tracking

    for i, page in enumerate(pages):
        print(f"  Processing page {i+1}/{len(pages)}")
        img_array = np.array(page.convert("RGB"))

        # Pre-process the page image
        import cv2
        gray     = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)
        _, binary = cv2.threshold(enhanced, 0, 255,
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        text, boxes = ocr_from_array(binary)
        all_text.append(f"--- Page {i+1} ---\n{text}")

        # Offset Y coordinates so pages don't overlap in the coordinate space
        for box in boxes:
            box["y_min"] += y_offset
            box["y_max"] += y_offset
            box["page"]   = i + 1
            all_boxes.append(box)

        y_offset += binary.shape[0]

    return "\n\n".join(all_text), all_boxes


def extract_text_and_boxes(path: str) -> tuple[str, list[dict]]:
    """
    Master function — auto-detects file type.
    Accepts: .png, .jpg, .jpeg, .tiff, .bmp, .pdf

    Returns:
        clean_text (str), bounding_boxes (list of dict)
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return ocr_from_pdf(path)
    elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
        return ocr_from_image(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ── Run standalone ────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ocr_pipeline.py <image_or_pdf_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    print(f"\n{'='*60}")
    print(f" OCR Pipeline — {input_path}")
    print(f"{'='*60}")

    text, boxes = extract_text_and_boxes(input_path)

    print("\n── EXTRACTED TEXT ──────────────────────────────────────")
    print(text)

    print("\n── BOUNDING BOXES (first 10) ───────────────────────────")
    for b in boxes[:10]:
        print(f"  [{b['x_min']:4d},{b['y_min']:4d}] → [{b['x_max']:4d},{b['y_max']:4d}]"
              f"  conf={b['confidence']:.2f}  text={b['text']!r}")

    # Save full output to JSON
    out_json = input_path + "_ocr_output.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"text": text, "bounding_boxes": boxes}, f,
                  ensure_ascii=False, indent=2)
    print(f"\n✓ Full output saved to: {out_json}")
