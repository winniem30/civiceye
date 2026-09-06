"""
Synthetic Data Generator for CIVIC-EYE Testing
Generates mock satellite imagery and change detection data for UI testing
"""
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SyntheticDataGenerator:
    """Generate synthetic satellite imagery and change data"""
    
    def __init__(self, output_dir: str = "./data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_satellite_image(
        self,
        width: int = 256,
        height: int = 256,
        has_vegetation: bool = True,
        has_water: bool = False,
        has_urban: bool = False,
        seed: Optional[int] = None
    ) -> np.ndarray:
        """Generate synthetic multispectral satellite image"""
        if seed is not None:
            np.random.seed(seed)
        
        # Generate 6 bands: Blue, Green, Red, NIR, SWIR1, SWIR2
        image = np.zeros((6, height, width))
        
        # Base values
        image[0] = np.random.uniform(0.1, 0.3, (height, width))  # Blue
        image[1] = np.random.uniform(0.2, 0.5, (height, width))  # Green
        image[2] = np.random.uniform(0.1, 0.4, (height, width))  # Red
        image[3] = np.random.uniform(0.3, 0.6, (height, width))  # NIR
        image[4] = np.random.uniform(0.2, 0.5, (height, width))  # SWIR1
        image[5] = np.random.uniform(0.1, 0.4, (height, width))  # SWIR2
        
        # Add vegetation (high NIR, low Red)
        if has_vegetation:
            vegetation_mask = np.random.random((height, width)) > 0.5
            image[3][vegetation_mask] = np.random.uniform(0.6, 0.9, np.sum(vegetation_mask))
            image[2][vegetation_mask] = np.random.uniform(0.05, 0.15, np.sum(vegetation_mask))
        
        # Add water (low NIR, low SWIR)
        if has_water:
            water_mask = np.random.random((height, width)) > 0.7
            for band in [3, 4, 5]:  # NIR, SWIR1, SWIR2
                image[band][water_mask] = np.random.uniform(0.05, 0.15, np.sum(water_mask))
        
        # Add urban (high reflectance across bands)
        if has_urban:
            urban_mask = np.random.random((height, width)) > 0.8
            for band in range(6):
                image[band][urban_mask] = np.random.uniform(0.4, 0.7, np.sum(urban_mask))
        
        return image
    
    def calculate_indices(self, image: np.ndarray) -> Dict:
        """Calculate spectral indices from image"""
        # NDVI = (NIR - Red) / (NIR + Red)
        nir = image[3]
        red = image[2]
        ndvi = (nir - red) / (nir + red + 1e-6)
        
        # NDWI = (Green - NIR) / (Green + NIR)
        green = image[1]
        ndwi = (green - nir) / (green + nir + 1e-6)
        
        return {
            "ndvi": ndvi,
            "ndwi": ndwi
        }
    
    def generate_change_mask(
        self,
        width: int = 256,
        height: int = 256,
        change_type: str = "deforestation",
        intensity: float = 0.5
    ) -> np.ndarray:
        """Generate synthetic change mask"""
        mask = np.zeros((height, width))
        
        if change_type == "deforestation":
            # Random patches of vegetation loss
            num_patches = int(5 * intensity)
            for _ in range(num_patches):
                cx, cy = np.random.randint(0, width), np.random.randint(0, height)
                radius = np.random.randint(10, 30)
                y, x = np.ogrid[:height, :width]
                patch = (x - cx)**2 + (y - cy)**2 <= radius**2
                mask[patch] = 1
        
        elif change_type == "construction":
            # Rectangular construction areas
            num_rects = int(3 * intensity)
            for _ in range(num_rects):
                x1, y1 = np.random.randint(0, width-50), np.random.randint(0, height-50)
                x2, y2 = x1 + np.random.randint(20, 50), y1 + np.random.randint(20, 50)
                mask[y1:y2, x1:x2] = 1
        
        elif change_type == "agriculture":
            # Agricultural expansion patterns
            mask = np.random.random((height, width)) > (1 - intensity * 0.3)
        
        return mask.astype(np.uint8)
    
    def apply_change_to_image(
        self,
        image: np.ndarray,
        change_mask: np.ndarray,
        change_type: str = "deforestation"
    ) -> np.ndarray:
        """Apply change to image based on mask"""
        changed_image = image.copy()
        
        if change_type == "deforestation":
            # Reduce NIR, increase Red in changed areas
            changed_image[3][change_mask > 0] *= 0.4  # NIR reduction
            changed_image[2][change_mask > 0] *= 1.5  # Red increase
        
        elif change_type == "construction":
            # Increase reflectance across bands
            for band in range(6):
                changed_image[band][change_mask > 0] *= 1.3
        
        elif change_type == "agriculture":
            # Moderate NIR, moderate Red
            changed_image[3][change_mask > 0] = np.random.uniform(0.4, 0.6, np.sum(change_mask))
            changed_image[2][change_mask > 0] = np.random.uniform(0.2, 0.3, np.sum(change_mask))
        
        return changed_image
    
    def generate_change_event(
        self,
        area_id: int,
        change_type: str = "deforestation"
    ) -> Dict:
        """Generate a complete change event"""
        # Generate before image
        before_image = self.generate_satellite_image(
            has_vegetation=True,
            seed=area_id
        )
        
        # Generate change mask
        change_mask = self.generate_change_mask(
            change_type=change_type,
            intensity=0.5
        )
        
        # Generate after image with change applied
        after_image = self.apply_change_to_image(
            before_image,
            change_mask,
            change_type
        )
        
        # Calculate indices
        before_indices = self.calculate_indices(before_image)
        after_indices = self.calculate_indices(after_image)
        
        # Calculate change statistics
        change_area = np.sum(change_mask)
        total_pixels = change_mask.size
        change_percentage = (change_area / total_pixels) * 100
        
        return {
            "area_id": area_id,
            "change_event_id": area_id * 100 + 1,
            "change_type": change_type,
            "before_image": before_image,
            "after_image": after_image,
            "change_mask": change_mask,
            "before_indices": before_indices,
            "after_indices": after_indices,
            "change_area": float(change_area),
            "change_percentage": float(change_percentage),
            "confidence": float(np.random.uniform(0.7, 0.95)),
            "detection_method": "baseline",
            "timestamp": (datetime.utcnow() - timedelta(days=np.random.randint(1, 30))).isoformat(),
            "bounds": {
                "min_x": np.random.uniform(-180, 180),
                "max_x": np.random.uniform(-180, 180),
                "min_y": np.random.uniform(-90, 90),
                "max_y": np.random.uniform(-90, 90)
            }
        }
    
    def generate_mock_database_data(self, num_areas: int = 10) -> Dict:
        """Generate mock data for database"""
        change_types = ["deforestation", "construction", "agriculture", "mining", "urban_expansion"]
        
        areas = []
        change_events = []
        
        for i in range(num_areas):
            area_id = i + 1
            change_type = np.random.choice(change_types)
            
            # Generate area
            area = {
                "id": area_id,
                "name": f"Test Area {area_id}",
                "description": f"Synthetic test area for {change_type}",
                "bounds": {
                    "min_x": np.random.uniform(-180, 180),
                    "max_x": np.random.uniform(-180, 180),
                    "min_y": np.random.uniform(-90, 90),
                    "max_y": np.random.uniform(-90, 90)
                },
                "created_at": (datetime.utcnow() - timedelta(days=np.random.randint(30, 365))).isoformat()
            }
            areas.append(area)
            
            # Generate change event
            change_event = self.generate_change_event(area_id, change_type)
            change_events.append(change_event)
        
        return {
            "areas": areas,
            "change_events": change_events
        }
    
    def save_synthetic_data(self, data: Dict):
        """Save synthetic data to files"""
        # Save areas
        with open(os.path.join(self.output_dir, "synthetic_areas.json"), "w") as f:
            json.dump(data["areas"], f, indent=2)
        
        # Save change events (without image arrays for JSON)
        change_events_serializable = []
        for ce in data["change_events"]:
            ce_copy = ce.copy()
            # Convert numpy arrays to lists for JSON serialization
            ce_copy["change_mask"] = ce["change_mask"].tolist()
            ce_copy["before_indices"] = {
                k: v.tolist() if isinstance(v, np.ndarray) else v
                for k, v in ce["before_indices"].items()
            }
            ce_copy["after_indices"] = {
                k: v.tolist() if isinstance(v, np.ndarray) else v
                for k, v in ce["after_indices"].items()
            }
            # Remove large image arrays
            del ce_copy["before_image"]
            del ce_copy["after_image"]
            change_events_serializable.append(ce_copy)
        
        with open(os.path.join(self.output_dir, "synthetic_change_events.json"), "w") as f:
            json.dump(change_events_serializable, f, indent=2)
        
        print(f"Synthetic data saved to {self.output_dir}")
        print(f"- {len(data['areas'])} areas")
        print(f"- {len(data['change_events'])} change events")


def main():
    """Main function to generate synthetic data"""
    generator = SyntheticDataGenerator()
    
    print("Generating synthetic data for CIVIC-EYE testing...")
    
    # Generate mock database data
    data = generator.generate_mock_database_data(num_areas=10)
    
    # Save to files
    generator.save_synthetic_data(data)
    
    print("\nSynthetic data generation complete!")
    print("You can now use this data to test the UI.")


if __name__ == "__main__":
    main()
