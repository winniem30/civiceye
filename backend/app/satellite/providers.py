
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os

from app.core.config import settings
from sentinelhub import (
    SHConfig,
    SentinelHubCatalog,
    DataCollection,
    BBox,
    CRS,
)


class SatelliteProvider(ABC):
    """Abstract base class for satellite data providers."""

    @abstractmethod
    async def search_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover: Optional[float] = None,
    ) -> List[Dict]:
        """Search for satellite images matching criteria."""
        pass

    @abstractmethod
    async def download_image(
        self, image_id: str, output_path: str
    ) -> str:
        """Download satellite image."""
        pass

    @abstractmethod
    async def get_preview(
        self, image_id: str
    ) -> Optional[str]:
        """Get preview image path."""
        pass


class Sentinel2Provider(SatelliteProvider):
    """Sentinel-2 satellite data provider."""

    def __init__(self):
        self.name = "sentinel-2"

        self.base_dir = os.path.join(
            settings.SATELLITE_DIR,
            "sentinel-2",
        )
        os.makedirs(self.base_dir, exist_ok=True)

        # Copernicus Data Space configuration
        config = SHConfig()
        config.sh_client_id = settings.SENTINEL_CLIENT_ID
        config.sh_client_secret = settings.SENTINEL_CLIENT_SECRET
        config.sh_token_url = (
            "https://identity.dataspace.copernicus.eu/"
            "auth/realms/CDSE/protocol/openid-connect/token"
        )
        config.sh_base_url = (
            "https://sh.dataspace.copernicus.eu"
        )

        self.config = config
        self.catalog = SentinelHubCatalog(
            config=self.config
        )

    async def search_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover: Optional[float] = None,
    ) -> List[Dict]:
        """Search Copernicus for Sentinel-2 L2A images."""

        bbox = BBox(
            [
                bounds["min_lon"],
                bounds["min_lat"],
                bounds["max_lon"],
                bounds["max_lat"],
            ],
            crs=CRS.WGS84,
        )

        # Default to searching the last 30 days.
        if end_date is None:
            end_date = datetime.utcnow()

        if start_date is None:
            start_date = end_date - timedelta(days=30)

        search = self.catalog.search(
            collection=DataCollection.SENTINEL2_L2A,
            bbox=bbox,
            datetime=(start_date, end_date),
            limit=20,
        )

        images = []

        # Catalog search returns an iterator.
        for item in search:
            properties = item.properties

            cloud_cover = properties.get(
                "eo:cloud_cover", 0
            )

            if (
                max_cloud_cover is not None
                and cloud_cover > max_cloud_cover
            ):
                continue

            images.append(
                {
                    "id": item.id,
                    "acquisition_date": properties.get(
                        "datetime",
                        item.datetime,
                    ),
                    "cloud_cover": cloud_cover,
                    "bounds": bounds,
                    "metadata": {
                        "satellite": "Sentinel-2",
                        "resolution": 10,
                        "bands": [
                            "B02",
                            "B03",
                            "B04",
                            "B08",
                            "B11",
                            "B12",
                        ],
                    },
                    "file_path": None,
                    "preview_path": None,
                }
            )

        return images

    def _get_local_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        max_cloud_cover: Optional[float],
    ) -> List[Dict]:
        """Check for locally stored satellite images."""
        return []

    async def download_image(
        self,
        image_id: str,
        output_path: str,
    ) -> str:
        """Placeholder until image downloading is implemented."""
        return output_path

    async def get_preview(
        self,
        image_id: str,
    ) -> Optional[str]:
        """Preview generation is not implemented yet."""
        return None


class Landsat8Provider(SatelliteProvider):
    """Landsat-8 satellite data provider."""

    def __init__(self):
        self.name = "landsat-8"
        self.base_dir = os.path.join(
            settings.SATELLITE_DIR,
            "landsat-8",
        )
        os.makedirs(self.base_dir, exist_ok=True)

    async def search_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover: Optional[float] = None,
    ) -> List[Dict]:
        """Landsat search is not implemented yet."""
        return []

    async def download_image(
        self,
        image_id: str,
        output_path: str,
    ) -> str:
        """Landsat downloading is not implemented yet."""
        return output_path

    async def get_preview(
        self,
        image_id: str,
    ) -> Optional[str]:
        """Landsat preview is not implemented yet."""
        return None


class LocalDatasetProvider(SatelliteProvider):
    """Provider for local development datasets."""

    def __init__(self):
        self.name = "local-dataset"
        self.base_dir = os.path.join(
            settings.SATELLITE_DIR,
            "local",
        )
        os.makedirs(self.base_dir, exist_ok=True)

    async def search_images(
        self,
        bounds: Dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_cloud_cover: Optional[float] = None,
    ) -> List[Dict]:
        """Local dataset search is not implemented yet."""
        return []

    async def download_image(
        self,
        image_id: str,
        output_path: str,
    ) -> str:
        """Local dataset copying is not implemented yet."""
        return output_path

    async def get_preview(
        self,
        image_id: str,
    ) -> Optional[str]:
        """Local preview generation is not implemented yet."""
        return None


def get_satellite_provider(
    provider_name: str,
) -> SatelliteProvider:
    """Create the requested satellite provider."""

    providers = {
        "sentinel-2": Sentinel2Provider,
        "landsat-8": Landsat8Provider,
        "local": LocalDatasetProvider,
    }

    provider_class = providers.get(
        provider_name,
        Sentinel2Provider,
    )

    return provider_class()
