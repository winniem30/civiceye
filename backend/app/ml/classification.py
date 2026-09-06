import numpy as np
from typing import Dict, Optional
import torch
import torch.nn as nn
from abc import ABC, abstractmethod


class HumanNaturalClassifier(ABC):
    """Classify changes as human-induced or natural"""
    
    @abstractmethod
    async def classify(self, change_data: Dict) -> Dict:
        """Classify change"""
        pass


class BaselineHumanClassifier(HumanNaturalClassifier):
    """Rule-based human vs natural classification"""
    
    def __init__(self):
        pass
    
    async def classify(self, change_data: Dict) -> Dict:
        """
        Classify change based on heuristics.
        
        Uses features like:
        - Change shape (regular vs irregular)
        - Change area
        - Spectral indices changes
        - Location context
        """
        change_mask = change_data.get("change_mask")
        change_percentage = change_data.get("change_percentage", 0)
        indices_t1 = change_data.get("indices_t1", {})
        indices_t2 = change_data.get("indices_t2", {})
        
        # Calculate features
        features = self._extract_features(change_mask, indices_t1, indices_t2)
        
        # Rule-based classification
        human_score = 0.0
        
        # Regular shapes suggest human activity
        if features["shape_regularity"] > 0.7:
            human_score += 0.3
        
        # Large contiguous changes suggest human activity
        if features["contiguity"] > 0.6:
            human_score += 0.2
        
        # Built-up area increase (NDBI)
        if features["ndbi_change"] > 0.2:
            human_score += 0.3
        
        # Vegetation loss (NDVI decrease)
        if features["ndvi_change"] < -0.2:
            human_score += 0.2
        
        # Normalize to 0-1
        human_score = min(1.0, human_score)
        
        is_human = human_score > 0.5
        confidence = abs(human_score - 0.5) * 2  # Higher confidence when score is far from 0.5
        
        return {
            "is_human_induced": is_human,
            "confidence": float(confidence),
            "human_score": float(human_score),
            "features": features,
            "method": "baseline"
        }
    
    def _extract_features(
        self,
        change_mask: Optional[np.ndarray],
        indices_t1: Dict,
        indices_t2: Dict
    ) -> Dict:
        """Extract features for classification"""
        features = {
            "shape_regularity": 0.5,
            "contiguity": 0.5,
            "ndvi_change": 0.0,
            "ndbi_change": 0.0,
            "ndwi_change": 0.0
        }
        
        if change_mask is not None:
            # Calculate shape regularity (aspect ratio of bounding box)
            rows = np.any(change_mask, axis=1)
            cols = np.any(change_mask, axis=0)
            if np.any(rows) and np.any(cols):
                rmin, rmax = np.where(rows)[0][[0, -1]]
                cmin, cmax = np.where(cols)[0][[0, -1]]
                height = rmax - rmin + 1
                width = cmax - cmin + 1
                aspect_ratio = min(height, width) / max(height, width)
                features["shape_regularity"] = aspect_ratio
                
                # Calculate contiguity (ratio of largest connected component)
                from scipy import ndimage
                labeled, num_features = ndimage.label(change_mask)
                if num_features > 0:
                    sizes = [np.sum(labeled == i) for i in range(1, num_features + 1)]
                    if sizes:
                        features["contiguity"] = max(sizes) / sum(sizes)
        
        # Calculate index changes
        if "ndvi" in indices_t1 and "ndvi" in indices_t2:
            features["ndvi_change"] = float(np.mean(indices_t2["ndvi"]) - np.mean(indices_t1["ndvi"]))
        
        if "ndbi" in indices_t1 and "ndbi" in indices_t2:
            features["ndbi_change"] = float(np.mean(indices_t2["ndbi"]) - np.mean(indices_t1["ndbi"]))
        
        if "ndwi" in indices_t1 and "ndwi" in indices_t2:
            features["ndwi_change"] = float(np.mean(indices_t2["ndwi"]) - np.mean(indices_t1["ndwi"]))
        
        return features


class ActivityClassifier(ABC):
    """Classify type of human activity"""
    
    @abstractmethod
    async def classify(self, change_data: Dict) -> Dict:
        """Classify activity type"""
        pass


class BaselineActivityClassifier(ActivityClassifier):
    """Rule-based activity classification"""
    
    ACTIVITY_TYPES = [
        "building",
        "road",
        "construction",
        "land_clearing",
        "mining",
        "agriculture",
        "water_alteration",
        "other"
    ]
    
    def __init__(self):
        pass
    
    async def classify(self, change_data: Dict) -> Dict:
        """
        Classify activity type based on spectral signatures and patterns.
        """
        indices_t1 = change_data.get("indices_t1", {})
        indices_t2 = change_data.get("indices_t2", {})
        change_mask = change_data.get("change_mask")
        
        # Calculate features
        ndvi_change = 0.0
        ndbi_change = 0.0
        ndwi_change = 0.0
        
        if "ndvi" in indices_t1 and "ndvi" in indices_t2:
            ndvi_change = np.mean(indices_t2["ndvi"]) - np.mean(indices_t1["ndvi"])
        
        if "ndbi" in indices_t1 and "ndbi" in indices_t2:
            ndbi_change = np.mean(indices_t2["ndbi"]) - np.mean(indices_t1["ndbi"])
        
        if "ndwi" in indices_t1 and "ndwi" in indices_t2:
            ndwi_change = np.mean(indices_t2["ndwi"]) - np.mean(indices_t1["ndwi"])
        
        # Rule-based classification
        scores = {
            "building": 0.0,
            "road": 0.0,
            "construction": 0.0,
            "land_clearing": 0.0,
            "mining": 0.0,
            "agriculture": 0.0,
            "water_alteration": 0.0,
            "other": 0.0
        }
        
        # Building: High NDBI increase, moderate NDVI decrease
        if ndbi_change > 0.15 and ndvi_change < -0.1:
            scores["building"] += 0.8
            scores["construction"] += 0.6
        
        # Road: Linear shape, high NDBI
        if ndbi_change > 0.1:
            scores["road"] += 0.5
        
        # Land clearing: Significant NDVI decrease, no NDBI increase
        if ndvi_change < -0.3 and ndbi_change < 0.05:
            scores["land_clearing"] += 0.9
        
        # Mining: Large area, significant vegetation loss
        if ndvi_change < -0.4:
            scores["mining"] += 0.7
        
        # Agriculture: NDVI fluctuation, seasonal patterns
        if -0.2 < ndvi_change < 0.2:
            scores["agriculture"] += 0.5
        
        # Water alteration: Significant NDWI change
        if abs(ndwi_change) > 0.2:
            scores["water_alteration"] += 0.8
        
        # Default to other if no strong signal
        if max(scores.values()) < 0.3:
            scores["other"] = 0.5
        
        # Get best match
        activity_type = max(scores, key=scores.get)
        confidence = scores[activity_type]
        
        return {
            "activity_type": activity_type,
            "confidence": float(confidence),
            "scores": scores,
            "method": "baseline"
        }
