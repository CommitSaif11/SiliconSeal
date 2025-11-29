import cv2
import sys
sys.path.insert(0, 'src')

from pipeline.ocr.ocr import run_ocr_multi_pass

# Load your IC image
img = cv2.imread(r"C:\Users\hp\Desktop\SIH25162 Final Project\backend\image_28147.jpg")  # ← Change this

if img is None:
    print("Failed to load image")
    sys. exit(1)

print("Image shape:", img.shape)
print("\n" + "="*60)
print("TESTING NEW OCR")
print("="*60)

result = run_ocr_multi_pass(img, min_score=0.80)

print(f"\n📝 Raw texts: {result['rec_texts']}")
print(f"\n🔢 Scores: {result['rec_scores']}")

print(f"\n📋 Grouped lines:")
for i, line in enumerate(result['grouped_lines']):
    print(f"  Line {i}: {' '.join(line['texts'])}")

print(f"\n✅ Full text: {result['full_text']}")