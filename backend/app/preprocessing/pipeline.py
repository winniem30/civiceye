import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from typing import Dict, Optional, Tuple
import os
from app.core.config import settings


class PreprocessingPipeline:
    """Image preprocessing pipeline for satellite imagery"""
    
    def __init__(self):
        self.cache_dir = settings.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
    
    async def load_and_preprocess(
        self,
        image_path: str,
        bounds: Optional[Dict] = None,
        target_resolution: Optional[float] = None
    ) -> Dict:
        """
        Load and preprocess satellite image.
        
        Returns:
            Dict containing:
            - image: numpy array
            - metadata: image metadata
            - indices: calculated spectral indices
        """
        if not image_path or not os.path.exists(image_path):
            # Return placeholder for development
            return self._get_placeholder_image()
        
        with rasterio.open(image_path) as src:
            # Read image data
            image = src.read()
            metadata = {
                "crs": str(src.crs),
                "transform": src.transform,
                "bounds": src.bounds,
                "width": src.width,
                "height": src.height,
                "count": src.count
            }
            
            # Crop to AOI if bounds provided
            if bounds:
                image, metadata = self._crop_to_bounds(image, metadata, bounds, src)
            
            # Normalize
            image = self._normalize(image)
            
            # Calculate spectral indices
            indices = self._calculate_indices(image, metadata)
            
            return {
                "image": image,
                "metadata": metadata,
                "indices": indices
            }
    
    def _crop_to_bounds(
        self,
        image: np.ndarray,
        metadata: Dict,
        bounds: Dict,
        src: rasterio.DatasetReader
    ) -> Tuple[np.ndarray, Dict]:
        """Crop image to specified bounds"""
        # TODO: Implement AOI cropping
        return image, metadata
    
    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize image values to 0-1 range"""
        # Avoid division by zero
        image = image.astype(np.float32)
        
        for i in range(image.shape[0]):
            band = image[i]
            if band.max() > band.min():
                image[i] = (band - band.min()) / (band.max() - band.min())
        
        return image
    
    def _calculate_indices(self, image: np.ndarray, metadata: Dict) -> Dict:
        """
        Calculate spectral indices.
        
        Assumes band order: [B02, B03, B04, B08, B11, B12] for Sentinel-2
        - B02: Blue (490nm)
        - B03: Green (560nm)
        - B04: Red (665nm)
        - B08: NIR (842nm)
        - B11: SWIR1 (1610nm)
        - B12: SWIR2 (2190nm)
        """
        indices = {}
        
        try:
            if image.shape[0] >= 4:
                # NDVI: (NIR - Red) / (NIR + Red)
                nir = image[3]  # B08
                red = image[2]  # B04
                denominator = nir + red
                ndvi = np.divide(nir - red, denominator, out=np.zeros_like(nir), where=denominator!=0)
                indices["ndvi"] = ndvi
            
            if image.shape[0] >= 4:
                # NDWI: (Green - NIR) / (Green + NIR)
                green = image[1]  # B03
                nir = image[3]  # B08
                denominator = green + nir
                ndwi = np.divide(green - nir, denominator, out=np.zeros_like(green), where=denominator!=0)
                indices["ndwi"] = ndwi
            
            if image.shape[0] >= 5:
                # NDBI: (SWIR1 - NIR) / (SWIR1 + NIR)
                swir1 = image[4]  # B11
                nir = image[3]  # B08
                denominator = swir1 + nir
                ndbi = np.divide(swir1 - nir, denominator, out=np.zeros_like(swir1), where=denominator!=0)
                indices["ndbi"] = ndbi
        except Exception as e:
            print(f"Error calculating indices: {e}")
        
        return indices
    
    def _get_placeholder_image(self) -> Dict:
        """Return placeholder image for development"""
        # Create a dummy 256x256 image with 6 bands
        image = np.random.rand(6, 256, 256).astype(np.float32)
        
        return {
            "image": image,
            "metadata": {
                "width": 256,
                "height": 256,
                "count": 6,
                "crs": "EPSG:4326",
                "placeholder": True
            },
            "indices": {
                "ndvi": np.random.rand(256, 256),
                "ndwi": np.random.rand(256, 256),
                "ndbi": np.random.rand(256, 256)
            }
        }
    
    async def align_images(
        self,
        image1: np.ndarray,
        image2: np.ndarray,
        metadata1: Dict,
        metadata2: Dict
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Align two images to the same grid"""
        # TODO: Implement image registration/alignment
        return image1, image2
    
    async def handle_clouds(
        self,
        image: np.ndarray,
        cloud_mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Handle cloud and shadow masking"""
        # TODO: Implement cloud masking
        return image
