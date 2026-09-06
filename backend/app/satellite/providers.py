from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import os
from app.core.config import settings


class SatelliteProvider(ABC):
    """Abstract base class for satellite data providers"""
    
    @abstractmethod
    async def search_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover: Optional[float] = None
    ) -> List[Dict]:
        """Search for satellite images matching criteria"""
        pass
    
    @abstractmethod
    async def download_image(self, image_id: str, output_path: str) -> str:
        """Download satellite image"""
        pass
    
    @abstractmethod
    async def get_preview(self, image_id: str) -> str:
        """Get preview image path"""
        pass


class Sentinel2Provider(SatelliteProvider):
    """Sentinel-2 satellite data provider"""
    
    def __init__(self):
        self.name = "sentinel-2"
        self.base_dir = os.path.join(settings.SATELLITE_DIR, "sentinel-2")
        os.makedirs(self.base_dir, exist_ok=True)
    
    async def search_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover: Optional[float] = None
    ) -> List[Dict]:
        """
        Search for Sentinel-2 images.
        
        For development, this uses a local dataset or simulated data.
        In production, this would connect to Sentinel Hub or ESA API.
        """
        # TODO: Integrate with Sentinel Hub or ESA API
        # For now, return simulated data structure
        
        images = []
        
        # Check if we have local data
        local_images = self._get_local_images(bounds, start_date, end_date, max_cloud_cover)
        if local_images:
            return local_images
        
        # Return placeholder for development
        images.append({
            "id": "placeholder_sentinel_001",
            "acquisition_date": datetime.utcnow(),
            "cloud_cover": 5.0,
            "bounds": bounds,
            "metadata": {
                "satellite": "Sentinel-2",
                "resolution": 10,
                "bands": ["B02", "B03", "B04", "B08", "B11", "B12"]
            },
            "file_path": None,  # Will be set when image is downloaded
            "preview_path": None
        })
        
        return images
    
    def _get_local_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        max_cloud_cover: Optional[float]
    ) -> List[Dict]:
        """Check for local satellite images"""
        # TODO: Implement local image catalog
        return []
    
    async def download_image(self, image_id: str, output_path: str) -> str:
        """Download Sentinel-2 image"""
        # TODO: Implement actual download from API
        # For development, copy from local dataset
        return output_path
    
    async def get_preview(self, image_id: str) -> str:
        """Get preview image"""
        # TODO: Generate or retrieve preview
        return None


class Landsat8Provider(SatelliteProvider):
    """Landsat-8 satellite data provider"""
    
    def __init__(self):
        self.name = "landsat-8"
        self.base_dir = os.path.join(settings.SATELLITE_DIR, "landsat-8")
        os.makedirs(self.base_dir, exist_ok=True)
    
    async def search_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover: Optional[float] = None
    ) -> List[Dict]:
        """Search for Landsat-8 images"""
        # TODO: Integrate with USGS EarthExplorer API
        return []
    
    async def download_image(self, image_id: str, output_path: str) -> str:
        """Download Landsat-8 image"""
        return output_path
    
    async def get_preview(self, image_id: str) -> str:
        """Get preview image"""
        return None


class LocalDatasetProvider(SatelliteProvider):
    """Provider for local development datasets"""
    
    def __init__(self):
        self.name = "local-dataset"
        self.base_dir = os.path.join(settings.SATELLITE_DIR, "local")
        os.makedirs(self.base_dir, exist_ok=True)
    
    async def search_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover: Optional[float] = None
    ) -> List[Dict]:
        """Search for local dataset images"""
        # TODO: Scan local directory for available images
        return []
    
    async def download_image(self, image_id: str, output_path: str) -> str:
        """Copy from local dataset"""
        return output_path
    
    async def get_preview(self, image_id: str) -> str:
        """Get preview from local dataset"""
        return None


def get_satellite_provider(provider_name: str) -> SatelliteProvider:
    """Factory function to get satellite provider"""
    providers = {
        "sentinel-2": Sentinel2Provider,
        "landsat-8": Landsat8Provider,
        "local": LocalDatasetProvider
    }
    
    provider_class = providers.get(provider_name, Sentinel2Provider)
    return provider_class()
