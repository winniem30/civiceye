import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from enum import Enum


class ChangeType(Enum):
    """Types of changes"""
    CONSTRUCTION = "construction"
    DEFORESTATION = "deforestation"
    AGRICULTURE = "agriculture"
    WATER_CHANGE = "water_change"
    URBAN_EXPANSION = "urban_expansion"
    MINING = "mining"
    UNKNOWN = "unknown"


@dataclass
class ChangeDNA:
    """DNA fingerprint of a change event"""
    
    # Spatial characteristics
    change_area: float
    change_percentage: float
    aspect_ratio: float
    compactness: float
    centroid_x: float
    centroid_y: float
    
    # Spectral characteristics
    mean_ndvi_change: float
    mean_ndwi_change: float
    mean_nir_change: float
    mean_red_change: float
    spectral_variance: float
    
    # Temporal characteristics
    duration_days: float
    seasonality: int  # 0-11 for month
    
    # Classification characteristics
    is_human_induced: bool
    human_confidence: float
    activity_type: str
    activity_confidence: float
    
    # Context characteristics
    proximity_to_water: float
    proximity_to_urban: float
    proximity_to_roads: float
    elevation_change: float
    slope: float
    
    # Metadata
    detection_method: str
    confidence: float
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_fingerprint(self) -> str:
        """Generate a unique fingerprint string"""
        values = [
            self.change_area,
            self.change_percentage,
            self.aspect_ratio,
            self.compactness,
            self.mean_ndvi_change,
            self.mean_ndwi_change,
            self.is_human_induced,
            self.activity_type,
            self.detection_method
        ]
        fingerprint = "_".join(str(v) for v in values)
        return fingerprint
    
    def to_vector(self) -> np.ndarray:
        """Convert to feature vector for ML"""
        return np.array([
            self.change_area,
            self.change_percentage,
            self.aspect_ratio,
            self.compactness,
            self.mean_ndvi_change,
            self.mean_ndwi_change,
            self.mean_nir_change,
            self.mean_red_change,
            self.spectral_variance,
            self.duration_days,
            float(self.is_human_induced),
            self.human_confidence,
            self.activity_confidence,
            self.proximity_to_water,
            self.proximity_to_urban,
            self.proximity_to_roads,
            self.elevation_change,
            self.slope,
            self.confidence
        ])


class ChangeDNAGenerator:
    """Generate Change DNA from change detection results"""
    
    def __init__(self):
        self.dna_database = {}
    
    def generate_dna(
        self,
        change_mask: np.ndarray,
        image_t1: Dict,
        image_t2: Dict,
        classification: Optional[Dict] = None,
        gis_context: Optional[Dict] = None,
        detection_method: str = "baseline"
    ) -> ChangeDNA:
        """
        Generate Change DNA from change detection results.
        
        Args:
            change_mask: Binary mask of changes
            image_t1: Preprocessed image at time 1
            image_t2: Preprocessed image at time 2
            classification: Classification results (human/natural, activity type)
            gis_context: GIS context data (proximity, elevation, slope)
            detection_method: Method used for detection
        
        Returns:
            ChangeDNA object
        """
        # Spatial characteristics
        spatial = self._extract_spatial_features(change_mask)
        
        # Spectral characteristics
        spectral = self._extract_spectral_features(image_t1, image_t2, change_mask)
        
        # Temporal characteristics
        temporal = self._extract_temporal_features(image_t1, image_t2)
        
        # Classification characteristics
        class_features = self._extract_classification_features(classification)
        
        # Context characteristics
        context = self._extract_context_features(gis_context, spatial)
        
        return ChangeDNA(
            change_area=spatial["change_area"],
            change_percentage=spatial["change_percentage"],
            aspect_ratio=spatial["aspect_ratio"],
            compactness=spatial["compactness"],
            centroid_x=spatial["centroid_x"],
            centroid_y=spatial["centroid_y"],
            mean_ndvi_change=spectral["mean_ndvi_change"],
            mean_ndwi_change=spectral["mean_ndwi_change"],
            mean_nir_change=spectral["mean_nir_change"],
            mean_red_change=spectral["mean_red_change"],
            spectral_variance=spectral["spectral_variance"],
            duration_days=temporal["duration_days"],
            seasonality=temporal["seasonality"],
            is_human_induced=class_features["is_human_induced"],
            human_confidence=class_features["human_confidence"],
            activity_type=class_features["activity_type"],
            activity_confidence=class_features["activity_confidence"],
            proximity_to_water=context["proximity_to_water"],
            proximity_to_urban=context["proximity_to_urban"],
            proximity_to_roads=context["proximity_to_roads"],
            elevation_change=context["elevation_change"],
            slope=context["slope"],
            detection_method=detection_method,
            confidence=class_features.get("confidence", 0.5),
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _extract_spatial_features(self, change_mask: np.ndarray) -> Dict:
        """Extract spatial features from change mask"""
        from skimage.measure import regionprops, label
        
        # Label connected components
        labeled = label(change_mask)
        regions = regionprops(labeled)
        
        if not regions:
            return {
                "change_area": 0.0,
                "change_percentage": 0.0,
                "aspect_ratio": 1.0,
                "compactness": 0.0,
                "centroid_x": 0.0,
                "centroid_y": 0.0
            }
        
        # Get largest region
        largest_region = max(regions, key=lambda r: r.area)
        
        # Calculate features
        total_pixels = change_mask.size
        change_pixels = np.sum(change_mask)
        change_percentage = (change_pixels / total_pixels) * 100 if total_pixels > 0 else 0
        
        # Aspect ratio (width/height)
        minr, minc, maxr, maxc = largest_region.bbox
        width = maxc - minc
        height = maxr - minr
        aspect_ratio = width / height if height > 0 else 1.0
        
        # Compactness (perimeter^2 / area)
        perimeter = largest_region.perimeter
        area = largest_region.area
        compactness = (perimeter ** 2) / area if area > 0 else 0.0
        
        # Centroid
        centroid = largest_region.centroid
        centroid_y, centroid_x = centroid
        
        return {
            "change_area": float(change_pixels),
            "change_percentage": float(change_percentage),
            "aspect_ratio": float(aspect_ratio),
            "compactness": float(compactness),
            "centroid_x": float(centroid_x),
            "centroid_y": float(centroid_y)
        }
    
    def _extract_spectral_features(
        self,
        image_t1: Dict,
        image_t2: Dict,
        change_mask: np.ndarray
    ) -> Dict:
        """Extract spectral change features"""
        img1 = image_t1.get("image", np.zeros((3, 256, 256)))
        img2 = image_t2.get("image", np.zeros((3, 256, 256)))
        
        # Calculate difference
        diff = img2 - img1
        
        # Extract indices if available
        indices_t1 = image_t1.get("indices", {})
        indices_t2 = image_t2.get("indices", {})
        
        # NDVI change
        ndvi_change = 0.0
        if "ndvi" in indices_t1 and "ndvi" in indices_t2:
            ndvi_diff = indices_t2["ndvi"] - indices_t1["ndvi"]
            ndvi_change = float(np.mean(ndvi_diff[change_mask > 0])) if np.any(change_mask > 0) else 0.0
        
        # NDWI change
        ndwi_change = 0.0
        if "ndwi" in indices_t1 and "ndwi" in indices_t2:
            ndwi_diff = indices_t2["ndwi"] - indices_t1["ndwi"]
            ndwi_change = float(np.mean(ndwi_diff[change_mask > 0])) if np.any(change_mask > 0) else 0.0
        
        # NIR change (assuming NIR is index 3 if available)
        nir_change = 0.0
        if diff.shape[0] > 3:
            nir_diff = diff[3]
            nir_change = float(np.mean(nir_diff[change_mask > 0])) if np.any(change_mask > 0) else 0.0
        
        # Red change (assuming Red is index 2)
        red_change = 0.0
        if diff.shape[0] > 2:
            red_diff = diff[2]
            red_change = float(np.mean(red_diff[change_mask > 0])) if np.any(change_mask > 0) else 0.0
        
        # Spectral variance
        spectral_variance = float(np.var(diff[:, change_mask > 0])) if np.any(change_mask > 0) else 0.0
        
        return {
            "mean_ndvi_change": ndvi_change,
            "mean_ndwi_change": ndwi_change,
            "mean_nir_change": nir_change,
            "mean_red_change": red_change,
            "spectral_variance": spectral_variance
        }
    
    def _extract_temporal_features(
        self,
        image_t1: Dict,
        image_t2: Dict
    ) -> Dict:
        """Extract temporal features"""
        # Get acquisition dates
        date1 = image_t1.get("acquisition_date")
        date2 = image_t2.get("acquisition_date")
        
        if date1 and date2:
            if isinstance(date1, str):
                date1 = datetime.fromisoformat(date1)
            if isinstance(date2, str):
                date2 = datetime.fromisoformat(date2)
            
            duration = (date2 - date1).total_seconds() / 86400  # Convert to days
            seasonality = date2.month - 1  # 0-11 for months
        else:
            duration = 0.0
            seasonality = 0
        
        return {
            "duration_days": duration,
            "seasonality": seasonality
        }
    
    def _extract_classification_features(
        self,
        classification: Optional[Dict]
    ) -> Dict:
        """Extract classification features"""
        if not classification:
            return {
                "is_human_induced": False,
                "human_confidence": 0.0,
                "activity_type": "unknown",
                "activity_confidence": 0.0,
                "confidence": 0.0
            }
        
        return {
            "is_human_induced": classification.get("is_human_induced", False),
            "human_confidence": classification.get("human_confidence", 0.0),
            "activity_type": classification.get("activity_type", "unknown"),
            "activity_confidence": classification.get("activity_confidence", 0.0),
            "confidence": classification.get("confidence", 0.5)
        }
    
    def _extract_context_features(
        self,
        gis_context: Optional[Dict],
        spatial_features: Dict
    ) -> Dict:
        """Extract GIS context features"""
        if not gis_context:
            return {
                "proximity_to_water": 0.0,
                "proximity_to_urban": 0.0,
                "proximity_to_roads": 0.0,
                "elevation_change": 0.0,
                "slope": 0.0
            }
        
        return {
            "proximity_to_water": gis_context.get("proximity_to_water", 0.0),
            "proximity_to_urban": gis_context.get("proximity_to_urban", 0.0),
            "proximity_to_roads": gis_context.get("proximity_to_roads", 0.0),
            "elevation_change": gis_context.get("elevation_change", 0.0),
            "slope": gis_context.get("slope", 0.0)
        }
    
    def compare_dna(
        self,
        dna1: ChangeDNA,
        dna2: ChangeDNA,
        weights: Optional[Dict] = None
    ) -> Dict:
        """
        Compare two Change DNA objects.
        
        Args:
            dna1: First Change DNA
            dna2: Second Change DNA
            weights: Optional weights for different features
        
        Returns:
            Dict with similarity scores
        """
        if weights is None:
            weights = {
                "spatial": 0.3,
                "spectral": 0.3,
                "classification": 0.2,
                "context": 0.2
            }
        
        # Spatial similarity
        spatial_sim = self._calculate_spatial_similarity(dna1, dna2)
        
        # Spectral similarity
        spectral_sim = self._calculate_spectral_similarity(dna1, dna2)
        
        # Classification similarity
        class_sim = self._calculate_classification_similarity(dna1, dna2)
        
        # Context similarity
        context_sim = self._calculate_context_similarity(dna1, dna2)
        
        # Weighted overall similarity
        overall_similarity = (
            weights["spatial"] * spatial_sim +
            weights["spectral"] * spectral_sim +
            weights["classification"] * class_sim +
            weights["context"] * context_sim
        )
        
        return {
            "overall_similarity": float(overall_similarity),
            "spatial_similarity": float(spatial_sim),
            "spectral_similarity": float(spectral_sim),
            "classification_similarity": float(class_sim),
            "context_similarity": float(context_sim)
        }
    
    def _calculate_spatial_similarity(self, dna1: ChangeDNA, dna2: ChangeDNA) -> float:
        """Calculate spatial similarity"""
        # Normalize features
        area_sim = 1.0 - min(1.0, abs(dna1.change_area - dna2.change_area) / max(dna1.change_area, dna2.change_area + 1))
        aspect_sim = 1.0 - min(1.0, abs(dna1.aspect_ratio - dna2.aspect_ratio) / max(dna1.aspect_ratio, dna2.aspect_ratio + 1))
        compact_sim = 1.0 - min(1.0, abs(dna1.compactness - dna2.compactness) / max(dna1.compactness, dna2.compactness + 1))
        
        return (area_sim + aspect_sim + compact_sim) / 3
    
    def _calculate_spectral_similarity(self, dna1: ChangeDNA, dna2: ChangeDNA) -> float:
        """Calculate spectral similarity"""
        ndvi_sim = 1.0 - min(1.0, abs(dna1.mean_ndvi_change - dna2.mean_ndvi_change))
        ndwi_sim = 1.0 - min(1.0, abs(dna1.mean_ndwi_change - dna2.mean_ndwi_change))
        variance_sim = 1.0 - min(1.0, abs(dna1.spectral_variance - dna2.spectral_variance) / max(dna1.spectral_variance, dna2.spectral_variance + 1))
        
        return (ndvi_sim + ndwi_sim + variance_sim) / 3
    
    def _calculate_classification_similarity(self, dna1: ChangeDNA, dna2: ChangeDNA) -> float:
        """Calculate classification similarity"""
        human_match = 1.0 if dna1.is_human_induced == dna2.is_human_induced else 0.0
        activity_match = 1.0 if dna1.activity_type == dna2.activity_type else 0.0
        
        return (human_match + activity_match) / 2
    
    def _calculate_context_similarity(self, dna1: ChangeDNA, dna2: ChangeDNA) -> float:
        """Calculate context similarity"""
        water_sim = 1.0 - min(1.0, abs(dna1.proximity_to_water - dna2.proximity_to_water) / 1000)
        urban_sim = 1.0 - min(1.0, abs(dna1.proximity_to_urban - dna2.proximity_to_urban) / 1000)
        road_sim = 1.0 - min(1.0, abs(dna1.proximity_to_roads - dna2.proximity_to_roads) / 1000)
        
        return (water_sim + urban_sim + road_sim) / 3
    
    def find_similar_changes(
        self,
        query_dna: ChangeDNA,
        threshold: float = 0.7,
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Find similar changes in the database.
        
        Args:
            query_dna: Change DNA to compare against
            threshold: Minimum similarity threshold
            top_k: Maximum number of results to return
        
        Returns:
            List of (change_id, similarity) tuples
        """
        similarities = []
        
        for change_id, stored_dna in self.dna_database.items():
            comparison = self.compare_dna(query_dna, stored_dna)
            similarity = comparison["overall_similarity"]
            
            if similarity >= threshold:
                similarities.append((change_id, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def store_dna(self, change_id: str, dna: ChangeDNA):
        """Store Change DNA in database"""
        self.dna_database[change_id] = dna
    
    def get_dna(self, change_id: str) -> Optional[ChangeDNA]:
        """Retrieve Change DNA from database"""
        return self.dna_database.get(change_id)
    
    def export_dna_database(self) -> str:
        """Export DNA database as JSON"""
        export_data = {
            change_id: dna.to_dict()
            for change_id, dna in self.dna_database.items()
        }
        return json.dumps(export_data, indent=2)
    
    def import_dna_database(self, json_data: str):
        """Import DNA database from JSON"""
        data = json.loads(json_data)
        self.dna_database = {
            change_id: ChangeDNA(**dna_data)
            for change_id, dna_data in data.items()
        }
