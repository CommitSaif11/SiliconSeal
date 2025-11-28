import argparse
import sys
import json

def safe_len(x):
    try:
        return len(x)
    except Exception:
        return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to image file")
    parser.add_argument("--group-lines", action="store_true", help="Group tokens by line using Y coordinate")
    args = parser.parse_args()

    from paddleocr import PaddleOCR
    import paddle
    import cv2, os

    print("Image:", args.image)
    if not os.path.exists(args.image):
        print("Image does not exist.")
        sys.exit(1)
    img = cv2.imread(args.image)
    if img is None:
        print("Failed to load image.")
        sys.exit(1)
    print("Image shape:", img.shape)

    try:
        paddle.set_device("cpu")
    except Exception as e:
        print("Device selection warning:", e)

    ocr = PaddleOCR(lang="en", use_textline_orientation=True)
    res_list = ocr.predict(args.image)
    if not res_list:
        print("No OCR results.")
        sys.exit(0)

    ocr_result = res_list[0]

    # Show keys present
    keys = list(ocr_result.keys())
    print("Keys:", keys)

    # Extract known fields
    rec_texts = ocr_result.get("rec_texts", [])
    rec_scores = ocr_result.get("rec_scores", [])
    rec_boxes = ocr_result.get("rec_boxes", [])
    rec_polys = ocr_result.get("rec_polys", [])
    dt_polys = ocr_result.get("dt_polys", [])

    n_texts = safe_len(rec_texts)
    n_scores = safe_len(rec_scores)
    n_boxes = safe_len(rec_boxes)
    n_polys = safe_len(rec_polys)

    n = min(n_texts, n_scores) if n_scores > 0 else n_texts
    print(f"Found {n} recognized items")

    def get_box_or_poly(i):
        if n_boxes > i:
            return rec_boxes[i]
        if n_polys > i:
            return rec_polys[i]
        return None

    for i in range(min(10, n)):
        t = rec_texts[i]
        s = rec_scores[i] if n_scores > i else None
        b = get_box_or_poly(i)
        print(f"[{i}] Text: {t} | Score: {None if s is None else f'{s:.3f}'} | Box/Poly: {b}")

    # Optional grouping into lines by Y coordinate of box/poly
    if args.group_lines and n > 0:
        print("\nGrouped lines (approximate):")
        # Build (text, y_center) tuples
        rows = []
        for i in range(n):
            t = rec_texts[i]
            b = get_box_or_poly(i)
            if b is None:
                # Skip if no geometry
                continue
            try:
                # b may be poly [[x1,y1],...]; compute average y
                if hasattr(b, "__len__") and safe_len(b) > 0 and hasattr(b[0], "__len__"):
                    y_vals = [pt[1] for pt in b]
                    y_center = sum(y_vals) / len(y_vals)
                else:
                    # if box is [x,y,w,h] or similar; try second element
                    y_center = float(b[1]) if safe_len(b) > 1 else 0.0
            except Exception:
                y_center = 0.0
            rows.append((y_center, t))
        # Cluster by y using a simple tolerance
        rows.sort(key=lambda r: r[0])
        grouped = []
        tol = 8.0  # pixel tolerance for small images; adjust if needed
        for y, t in rows:
            if not grouped or abs(y - grouped[-1]["y"]) > tol:
                grouped.append({"y": y, "texts": [t]})
            else:
                grouped[-1]["texts"].append(t)
        for i, g in enumerate(grouped):
            print(f"Line {i}: {' '.join(g['texts'])}")

    # Optional summary JSON
    summary = {
        "rec_texts": rec_texts[:10],
        "rec_scores": rec_scores[:10],
        "rec_boxes_sample": rec_boxes[:3],
        "rec_polys_sample": rec_polys[:3],
        "dt_polys_sample": dt_polys[:3],
    }
    print("\nSummary JSON (truncated):")
    try:
        print(json.dumps(summary, ensure_ascii=False, indent=2)[:1000])
    except Exception as e:
        print("JSON summary failed:", e)

if __name__ == "__main__":
    main()