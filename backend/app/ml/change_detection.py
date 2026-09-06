import numpy as np
from typing import Dict, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
from abc import ABC, abstractmethod
import os


class ChangeDetector(ABC):
    """Abstract base class for change detection models"""
    
    @abstractmethod
    async def detect_change(
        self,
        image_t1: Dict,
        image_t2: Dict
    ) -> Dict:
        """Detect changes between two images"""
        pass


class BaselineChangeDetector(ChangeDetector):
    """Baseline change detection using image differencing"""
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
    
    async def detect_change(
        self,
        image_t1: Dict,
        image_t2: Dict
    ) -> Dict:
        """
        Detect changes using simple image differencing.
        
        Args:
            image_t1: Preprocessed image at time 1
            image_t2: Preprocessed image at time 2
        
        Returns:
            Dict containing:
            - change_mask: binary mask of changes
            - change_area: area of change in pixels
            - change_percentage: percentage of changed pixels
            - confidence: confidence score
            - bounding_geometry: bounding box of changes
        """
        img1 = image_t1["image"]
        img2 = image_t2["image"]
        
        # Ensure same shape
        if img1.shape != img2.shape:
            # Resize to match
            min_h = min(img1.shape[1], img2.shape[1])
            min_w = min(img1.shape[2], img2.shape[2])
            img1 = img1[:, :min_h, :min_w]
            img2 = img2[:, :min_h, :min_w]
        
        # Calculate difference using multiple methods
        # 1. Simple difference
        diff = np.abs(img1 - img2)
        
        # 2. NDVI difference if available
        ndvi_diff = None
        if "ndvi" in image_t1["indices"] and "ndvi" in image_t2["indices"]:
            ndvi_diff = np.abs(image_t1["indices"]["ndvi"] - image_t2["indices"]["ndvi"])
        
        # Combine differences
        combined_diff = np.mean(diff, axis=0)
        if ndvi_diff is not None:
            combined_diff = (combined_diff + ndvi_diff) / 2
        
        # Threshold to get change mask
        change_mask = (combined_diff > self.threshold).astype(np.uint8)
        
        # Calculate change statistics
        total_pixels = change_mask.size
        changed_pixels = np.sum(change_mask)
        change_percentage = (changed_pixels / total_pixels) * 100 if total_pixels > 0 else 0
        
        # Calculate confidence based on magnitude of differences
        mean_diff = np.mean(combined_diff[change_mask > 0]) if changed_pixels > 0 else 0
        confidence = min(1.0, mean_diff * 2)  # Scale to 0-1
        
        # Get bounding box of changes
        bounding_geometry = self._get_bounding_box(change_mask)
        
        return {
            "change_mask": change_mask,
            "change_area": float(changed_pixels),  # In pixels, convert to meters using resolution
            "change_percentage": float(change_percentage),
            "confidence": float(confidence),
            "bounding_geometry": bounding_geometry,
            "method": "baseline"
        }
    
    def _get_bounding_box(self, mask: np.ndarray) -> Dict:
        """Get bounding box of non-zero regions in mask"""
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            return None
        
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        return {
            "type": "Polygon",
            "coordinates": [[
                [cmin, rmin],
                [cmax, rmin],
                [cmax, rmax],
                [cmin, rmax],
                [cmin, rmin]
            ]]
        }


class SiameseCNNChangeDetector(ChangeDetector):
    """Siamese CNN for change detection"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.input_size = (256, 256)  # Standard input size
        
        if model_path and os.path.exists(model_path):
            self._load_model()
        else:
            self._create_model()
    
    def _load_model(self):
        """Load pre-trained Siamese CNN model"""
        try:
            self.model = SiameseNetwork().to(self.device)
            checkpoint = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
            print(f"Loaded Siamese CNN model from {self.model_path}")
        except Exception as e:
            print(f"Failed to load model: {e}. Creating new model.")
            self._create_model()
    
    def _create_model(self):
        """Create Siamese CNN architecture"""
        self.model = SiameseNetwork().to(self.device)
        self.model.eval()
    
    def _preprocess_image(self, image_data: np.ndarray) -> torch.Tensor:
        """Preprocess image for model input"""
        # Normalize to [0, 1]
        if image_data.max() > 1:
            image_data = image_data / 255.0
        
        # Ensure 6 channels (RGB + 3 spectral indices if available, or pad)
        if image_data.shape[0] < 6:
            # Pad with zeros
            padding = np.zeros((6 - image_data.shape[0], *image_data.shape[1:]))
            image_data = np.concatenate([image_data, padding], axis=0)
        elif image_data.shape[0] > 6:
            # Take first 6 channels
            image_data = image_data[:6]
        
        # Resize to input size
        from skimage.transform import resize
        resized = []
        for i in range(image_data.shape[0]):
            resized.append(resize(image_data[i], self.input_size, preserve_range=True))
        image_data = np.stack(resized, axis=0)
        
        # Convert to tensor
        tensor = torch.from_numpy(image_data).float().unsqueeze(0)
        return tensor.to(self.device)
    
    async def detect_change(
        self,
        image_t1: Dict,
        image_t2: Dict
    ) -> Dict:
        """Detect changes using Siamese CNN"""
        try:
            img1 = image_t1["image"]
            img2 = image_t2["image"]
            
            # Preprocess images
            tensor1 = self._preprocess_image(img1)
            tensor2 = self._preprocess_image(img2)
            
            # Run inference
            with torch.no_grad():
                change_prob = self.model(tensor1, tensor2)
                change_prob = change_prob.squeeze().cpu().numpy()
            
            # Threshold to get binary mask
            threshold = 0.5
            change_mask = (change_prob > threshold).astype(np.uint8)
            
            # Calculate statistics
            total_pixels = change_mask.size
            changed_pixels = np.sum(change_mask)
            change_percentage = (changed_pixels / total_pixels) * 100 if total_pixels > 0 else 0
            
            # Calculate confidence based on prediction certainty
            confidence = float(np.mean(change_prob[change_mask > 0])) if changed_pixels > 0 else 0.0
            
            # Get bounding box
            bounding_geometry = self._get_bounding_box(change_mask)
            
            return {
                "change_mask": change_mask,
                "change_area": float(changed_pixels),
                "change_percentage": float(change_percentage),
                "confidence": float(confidence),
                "bounding_geometry": bounding_geometry,
                "method": "siamese_cnn"
            }
        except Exception as e:
            print(f"Siamese CNN inference failed: {e}. Falling back to baseline.")
            baseline = BaselineChangeDetector()
            result = await baseline.detect_change(image_t1, image_t2)
            result["method"] = "siamese_cnn_fallback"
            return result
    
    def train(
        self,
        train_data: list,
        epochs: int = 10,
        batch_size: int = 8,
        learning_rate: float = 0.001
    ) -> Dict:
        """Train the Siamese CNN model"""
        # TODO: Implement training logic
        # This would require a proper dataset loader and training loop
        return {
            "status": "training_not_implemented",
            "message": "Training logic requires dataset implementation"
        }
    
    def save_model(self, path: str):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'input_size': self.input_size,
        }, path)
        print(f"Model saved to {path}")
    
    def _get_bounding_box(self, mask: np.ndarray) -> Dict:
        """Get bounding box of non-zero regions in mask"""
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            return None
        
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        return {
            "type": "Polygon",
            "coordinates": [[
                [cmin, rmin],
                [cmax, rmin],
                [cmax, rmax],
                [cmin, rmax],
                [cmin, rmin]
            ]]
        }


class SiameseNetwork(nn.Module):
    """Siamese CNN architecture for change detection"""
    
    def __init__(self):
        super(SiameseNetwork, self).__init__()
        
        # Encoder - shared weights for both images
        self.encoder = nn.Sequential(
            # Block 1
            nn.Conv2d(6, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            # Block 2
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            # Block 3
            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            # Block 4
            nn.Conv2d(256, 512, 3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
        )
        
        # Decoder - combines features from both images
        self.decoder = nn.Sequential(
            nn.Conv2d(1024, 512, 3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(512, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
            
            nn.Conv2d(256, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
            
            nn.Conv2d(128, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
            
            nn.Conv2d(64, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(32, 1, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """Forward pass through Siamese network"""
        # Encode both images with shared weights
        f1 = self.encoder(x1)
        f2 = self.encoder(x2)
        
        # Concatenate features
        combined = torch.cat([f1, f2], dim=1)
        
        # Decode to change probability map
        output = self.decoder(combined)
        
        return output


def get_change_detector(method: str = "baseline") -> ChangeDetector:
    """Factory function to get change detector"""
    detectors = {
        "baseline": BaselineChangeDetector,
        "siamese_cnn": SiameseCNNChangeDetector
    }
    
    detector_class = detectors.get(method, BaselineChangeDetector)
    return detector_class()
