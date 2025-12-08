"""
YOLO IC Detector
Detects IC components in images using YOLOv8
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

import cv2
import numpy as np
from ultralytics import YOLO

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging

from .config import detector_config

# Setup logging for Saif's debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YOLODetector:
    """
    YOLOv8-based IC Component Detector
    Saif will train a custom model in Google Colab for IC detection
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to YOLO model weights (local path or URL)
                       If None, uses config default
        
        Note for Saif:
            - For now, this uses a dummy YOLOv8n model
            - After training in Colab, update MODEL_PATH in .env
            - Can be local path or Google Drive/S3 URL
        """
        self.model_path = model_path or detector_config.MODEL_PATH
        self.confidence_threshold = detector_config.CONFIDENCE_THRESHOLD
        self.iou_threshold = detector_config.IOU_THRESHOLD
        self.max_detections = detector_config.MAX_DETECTIONS
        self.device = detector_config.DEVICE
        
        # Ensure model cache directory exists
        detector_config.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load YOLO model
        self.model = self._load_model()
        
        logger.info(f"✅ Saif, YOLO detector initialized successfully!")
        logger.info(f"📦 Model: {self.model_path}")
        logger.info(f"🖥️  Device: {self.device}")
    
    def _load_model(self) -> YOLO:
        """
        Load YOLO model from path or URL with dynamic handling
        
        Returns:
            Loaded YOLO model instance
        
        Note for Saif:
            This handles both local paths and remote URLs automatically
        """
        try:
            logger.info(f"🔄 Loading YOLO model for Saif from: {self.model_path}")
            
            # YOLO handles both local paths and URLs dynamically
            model = YOLO(self.model_path)
            
            # Move model to specified device
            model.to(self.device)
            
            logger.info(f"✅ Model loaded successfully for Saif!")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load YOLO model for Saif: {str(e)}")
            raise RuntimeError(f"YOLO model loading failed: {str(e)}")
    
    def detect(
        self, 
        image: Union[np.ndarray, str, Path],
        conf_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect IC components in image
        
        Args:
            image: Input image (numpy array, file path, or Path object)
            conf_threshold: Override confidence threshold for this detection
            iou_threshold: Override IOU threshold for this detection
        
        Returns:
            List of detection dictionaries containing:
                - bbox: [x1, y1, x2, y2] bounding box coordinates
                - confidence: Detection confidence score
                - class_id: Detected class ID
                - class_name: Detected class name
        
        Note for Saif:
            This will return IC component bounding boxes for OCR cropping
        """
        try:
            # Use custom thresholds or fall back to config
            conf = conf_threshold or self.confidence_threshold
            iou = iou_threshold or self.iou_threshold
            
            # Run YOLO inference
            results = self.model.predict(
                source=image,
                conf=conf,
                iou=iou,
                max_det=self.max_detections,
                verbose=False  # Suppress YOLO logging
            )
            
            # Parse detection results for Saif
            detections = []
            
            for result in results:
                boxes = result.boxes
                
                for i in range(len(boxes)):  # type: ignore
                    # Extract bounding box coordinates
                    bbox = boxes.xyxy[i].cpu().numpy().tolist()  # type: ignore  # [x1, y1, x2, y2]
                    
                    # Extract confidence and class info
                    confidence = float(boxes.conf[i].cpu().numpy())
                    class_id = int(boxes.cls[i].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    detection = {
                        "bbox": bbox,
                        "confidence": confidence,
                        "class_id": class_id,
                        "class_name": class_name
                    }
                    
                    detections.append(detection)
            
            logger.info(f"✅ Saif, detected {len(detections)} IC component(s)")
            return detections
            
        except Exception as e:
            logger.error(f"❌ Detection failed for Saif: {str(e)}")
            raise RuntimeError(f"YOLO detection failed: {str(e)}")
    
    def detect_and_crop(
        self, 
        image: Union[np.ndarray, str, Path],
        conf_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None,
        padding: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Detect IC components and return cropped images for OCR
        
        Args:
            image: Input image (numpy array, file path, or Path object)
            conf_threshold: Override confidence threshold
            iou_threshold: Override IOU threshold
            padding: Padding pixels around detected bbox (default: 10)
        
        Returns:
            List of detection dictionaries with added 'cropped_image' field
        
        Note for Saif:
            This is the main function you'll use in the pipeline
            Returns cropped IC regions ready for Tesseract OCR
        """
        try:
            # Load image if path provided
            if isinstance(image, (str, Path)):
                img = cv2.imread(str(image))
                if img is None:
                    raise ValueError(f"Failed to load image: {image}")
            else:
                img = image
            
            # Get detections
            detections = self.detect(
                image=img,
                conf_threshold=conf_threshold,
                iou_threshold=iou_threshold
            )
            
            # Crop each detection with padding
            h, w = img.shape[:2]
            
            for detection in detections:
                x1, y1, x2, y2 = detection["bbox"]
                
                # Apply padding and ensure within image bounds
                x1 = max(0, int(x1) - padding)
                y1 = max(0, int(y1) - padding)
                x2 = min(w, int(x2) + padding)
                y2 = min(h, int(y2) + padding)
                
                # Crop the IC region
                cropped = img[y1:y2, x1:x2]
                
                # Add cropped image to detection
                detection["cropped_image"] = cropped
                detection["cropped_bbox"] = [x1, y1, x2, y2]  # Updated bbox with padding
            
            logger.info(f"✅ Saif, cropped {len(detections)} IC region(s) for OCR")
            return detections
            
        except Exception as e:
            logger.error(f"❌ Crop operation failed for Saif: {str(e)}")
            raise RuntimeError(f"YOLO crop failed: {str(e)}")
    
    def visualize_detections(
        self, 
        image: Union[np.ndarray, str, Path],
        detections: List[Dict[str, Any]],
        output_path: Optional[Union[str, Path]] = None
    ) -> np.ndarray:
        """
        Draw bounding boxes on image for visualization
        
        Args:
            image: Input image
            detections: List of detection dictionaries from detect()
            output_path: Optional path to save visualized image
        
        Returns:
            Image with drawn bounding boxes
        
        Note for Saif:
            Useful for debugging and frontend display
        """
        try:
            # Load image if path provided
            if isinstance(image, (str, Path)):
                img = cv2.imread(str(image))
            else:
                img = image.copy()
            
            # Draw each detection
            for detection in detections:
                x1, y1, x2, y2 = [int(coord) for coord in detection["bbox"]]
                confidence = detection["confidence"]
                class_name = detection["class_name"]
                
                # Draw bounding box (green)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(
                    img, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )
            
            # Save if output path provided
            if output_path:
                cv2.imwrite(str(output_path), img)
                logger.info(f"✅ Saif, visualization saved to: {output_path}")
            
            return img
            
        except Exception as e:
            logger.error(f"❌ Visualization failed for Saif: {str(e)}")
            raise RuntimeError(f"Visualization failed: {str(e)}")