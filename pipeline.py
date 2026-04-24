"""
pipeline.py — Batch OCR runner across all bid folders.
Hands off structured data to the Architect.

Run: python3 pipeline.py
"""
import os
import json
from ocr_pipeline import extract_text_and_boxes

FOLDERS = {
    "perfect_bids":      "data/perfect_bids",
    "blurry_bids":       "data/blurry_bids",
    "missing_data_bids": "data/missing_data_bids",
}

SUPPORTED = {".png", ".jpg", ".jpeg", ".pdf", ".tiff", ".bmp"}
OUTPUT_FILE = "all_bids_extracted.json"


def run_batch():
    all_results = {}

    for category, folder in FOLDERS.items():
        print(f"\n{'='*60}")
        print(f" Category: {category.upper()}")
        print(f"{'='*60}")

        if not os.path.exists(folder):
            print(f"  ⚠ Folder not found: {folder}")
            continue

        category_results = {}

        for fname in sorted(os.listdir(folder)):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in SUPPORTED:
                continue

            fpath = os.path.join(folder, fname)
            print(f"\n→ Processing: {fname}")

            try:
                text, boxes = extract_text_and_boxes(fpath)
                category_results[fname] = {
                    "status":        "success",
                    "text":          text,
                    "bounding_boxes": boxes,
                    "word_count":    len(text.split()),
                    "box_count":     len(boxes),
                }
                print(f"  ✓ Extracted {len(boxes)} text regions, "
                      f"{len(text.split())} words")

            except Exception as e:
                category_results[fname] = {
                    "status": "error",
                    "error":  str(e),
                }
                print(f"  ✗ Error: {e}")

        all_results[category] = category_results

    # Save consolidated output for the Architect
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f" ✓ All results saved to: {OUTPUT_FILE}")
    print(f"{'='*60}")

    # Print summary
    print("\n── SUMMARY ─────────────────────────────────────────────")
    for cat, results in all_results.items():
        success = sum(1 for r in results.values() if r["status"] == "success")
        total   = len(results)
        print(f"  {cat}: {success}/{total} files processed successfully")

    return all_results


if __name__ == "__main__":
    run_batch()