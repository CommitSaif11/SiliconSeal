"""
YOLO Detector Test
SIH 25162 - Testing IC Detection
Author: Saif (CommitSaif11) | Mentor: Zoe 💙
"""

import cv2
from src.pipeline.detector import YOLODetector

def test_yolo():
    print("=" * 60)
    print("YOLO IC DETECTOR TEST")
    print("SIH 25162 - AOI IC Verification")
    print("Author: Saif (CommitSaif11) | Mentor: Zoe 💙")
    print("=" * 60)
    # Initialize detector
    print("\n🔄 Initializing YOLO detector...")
    detector = YOLODetector()

    # Load test image
    img_path = r"C:\Users\hp\Desktop\SIH25162 Final Project\backend\generated.png"
    print(f"\n📸 Loading image: {img_path}")
    img = cv2.imread(img_path)
    
    if img is None:
        print("❌ Failed to load image!")
        return
    
    print(f"✅ Image loaded: {img.shape}")
    
    # Test 1: Simple detection
    print("\n" + "=" * 60)
    print("TEST 1: Simple Detection")
    print("=" * 60)
    detections = detector.detect(img)
    
    print(f"\n📦 Detected {len(detections)} object(s):\n")
    for i, det in enumerate(detections):
        print(f"  [{i}] Class: {det['class_name']}")
        print(f"      Confidence: {det['confidence']:.3f}")
        print(f"      BBox: {det['bbox']}\n")
    
    # Test 2: Detection with cropping
    print("=" * 60)
    print("TEST 2: Detection + Cropping for OCR")
    print("=" * 60)
    cropped_detections = detector.detect_and_crop(img, padding=20)
    
    print(f"\n✂️  Cropped {len(cropped_detections)} region(s):\n")
    for i, det in enumerate(cropped_detections):
        crop = det['cropped_image']
        print(f"  [{i}] Cropped size: {crop.shape}")
        print(f"      Padded BBox: {det['cropped_bbox']}\n")
    
    # Test 3: Visualization
    print("=" * 60)
    print("TEST 3: Visualization")
    print("=" * 60)
    output_path = "yolo_detection_result.png"
    visualized = detector.visualize_detections(img, detections, output_path)
    print(f"\n🎨 Visualization saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("✅ YOLO Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_yolo()