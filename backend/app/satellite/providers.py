from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import os
import httpx
import asyncio
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
    """Sentinel-2 satellite data provider using STAC API"""
    
    def __init__(self):
        self.name = "sentinel-2"
        self.base_dir = os.path.join(settings.SATELLITE_DIR, "sentinel-2")
        os.makedirs(self.base_dir, exist_ok=True)
        self.stac_endpoint = settings.STAC_ENDPOINT
        self.collection = settings.SENTINEL_COLLECTION
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover: Optional[float] = None
    ) -> List[Dict]:
        """
        Search for Sentinel-2 images using STAC API.
        
        Args:
            bounds: Dict with min_x, min_y, max_x, max_y (longitude, latitude)
            start_date: Optional start date for search
            end_date: Optional end date for search
            max_cloud_cover: Maximum cloud cover percentage
        
        Returns:
            List of matching satellite images
        """
        try:
            # Build STAC search query
            bbox = [
                bounds["min_x"],
                bounds["min_y"],
                bounds["max_x"],
                bounds["max_y"]
            ]
            
            params = {
                "bbox": ",".join(map(str, bbox)),
                "collections": self.collection,
                "limit": 20
            }
            
            # Add date range if provided
            if start_date or end_date:
                date_range = ""
                if start_date:
                    date_range += start_date.strftime("%Y-%m-%d")
                date_range += "/"
                if end_date:
                    date_range += end_date.strftime("%Y-%m-%d")
                else:
                    date_range += datetime.utcnow().strftime("%Y-%m-%d")
                params["datetime"] = date_range
            
            # Add cloud cover filter
            if max_cloud_cover is not None:
                params["query"] = f"eo:cloud_cover<={max_cloud_cover}"
            
            # Query STAC API
            response = await self.client.get(
                f"{self.stac_endpoint}/search",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            images = []
            
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                assets = feature.get("assets", {})
                
                # Extract cloud cover
                cloud_cover = props.get("eo:cloud_cover", 0)
                
                # Extract acquisition date
                acquisition_date = datetime.fromisoformat(
                    props.get("datetime", "").replace("Z", "+00:00")
                )
                
                # Extract bounds from geometry
                coords = geometry.get("coordinates", [[]])
                if coords:
                    lons = [c[0] for c in coords[0]]
                    lats = [c[1] for c in coords[0]]
                    img_bounds = {
                        "min_x": min(lons),
                        "max_x": max(lons),
                        "min_y": min(lats),
                        "max_y": max(lats)
                    }
                else:
                    img_bounds = bounds
                
                # Check if required bands are available
                required_bands = ["B02", "B03", "B04", "B08", "B11", "B12"]
                available_bands = [k for k in assets.keys() if k in required_bands]
                
                if len(available_bands) < len(required_bands):
                    continue
                
                images.append({
                    "id": feature.get("id"),
                    "stac_id": feature.get("id"),
                    "acquisition_date": acquisition_date,
                    "cloud_cover": cloud_cover,
                    "bounds": img_bounds,
                    "geometry": geometry,
                    "metadata": {
                        "satellite": "Sentinel-2",
                        "platform": props.get("platform", "sentinel-2a"),
                        "constellation": props.get("constellation", "sentinel-2"),
                        "instrument": props.get("instruments", ["msi"]),
                        "resolution": 10,
                        "bands": available_bands,
                        "stac_links": feature.get("links", []),
                        "assets": {k: v.get("href") for k, v in assets.items() if k in required_bands}
                    },
                    "file_path": None,
                    "preview_path": assets.get("visual", {}).get("href") if "visual" in assets else None
                })
            
            return images
            
        except httpx.HTTPError as e:
            print(f"STAC API error: {e}")
            return []
        except Exception as e:
            print(f"Error searching Sentinel-2 images: {e}")
            return []
    
    async def download_image(self, image_id: str, output_path: str) -> str:
        """Download Sentinel-2 image bands"""
        try:
            # This is a placeholder - actual download would be done during processing
            # The processing pipeline will download individual bands as needed
            return output_path
        except Exception as e:
            print(f"Error downloading image: {e}")
            raise
    
    async def get_preview(self, image_id: str) -> str:
        """Get preview image"""
        # Preview would be downloaded during processing
        return None
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


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
        # TODO: Integrate with USGS EarthExplorer or STAC
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
