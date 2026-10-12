import numpy as np
from typing import Dict, Optional, Tuple
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


def get_change_detector(method: str = "baseline") -> ChangeDetector:
    """Factory function to get change detector"""
    # For MVP, only baseline is supported
    if method != "baseline":
        print(f"Method '{method}' not supported in MVP. Using baseline.")
    return BaselineChangeDetector()
