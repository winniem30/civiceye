from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import os
from app.db.session import get_db
from app.db.models import SatelliteImage
from app.satellite.providers import get_satellite_provider
from pydantic import BaseModel

router = APIRouter()


class SatelliteImageResponse(BaseModel):
    id: int
    satellite_name: str
    acquisition_date: datetime
    cloud_cover: Optional[float]
    bounds: dict
    metadata: Optional[dict]
    file_path: Optional[str]
    preview_path: Optional[str]

    class Config:
        from_attributes = True


class ImageSearchRequest(BaseModel):
    bounds: dict  # {min_x, min_y, max_x, max_y}
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_cloud_cover: Optional[float] = 20.0
    satellite: Optional[str] = "sentinel-2"


def load_synthetic_data():
    """Load synthetic data for testing"""
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "synthetic_change_events.json")
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                return json.load(f)
    except:
        pass
    return None


@router.post("/search", response_model=List[SatelliteImageResponse])
async def search_satellite_images(
    request: ImageSearchRequest,
    db: Session = Depends(get_db)
):
    # Try to use synthetic data for testing
    synthetic_data = load_synthetic_data()
    if synthetic_data:
        # Return synthetic satellite images
        images = []
        for i, event in enumerate(synthetic_data[:5]):  # Return first 5
            images.append(SatelliteImageResponse(
                id=i + 1,
                satellite_name="synthetic-sentinel-2",
                acquisition_date=datetime.fromisoformat(event["timestamp"]),
                cloud_cover=5.0,
                bounds=event["bounds"],
                metadata={"change_type": event["change_type"]},
                file_path=None,
                preview_path=None
            ))
        return images
    
    # Fall back to actual satellite provider
    provider = get_satellite_provider(request.satellite)
    
    try:
        images = await provider.search_images(
            bounds=request.bounds,
            start_date=request.start_date,
            end_date=request.end_date,
            max_cloud_cover=request.max_cloud_cover
        )
        
        # Store in database
        db_images = []
        for img in images:
            db_img = SatelliteImage(
                satellite_name=request.satellite,
                acquisition_date=img["acquisition_date"],
                cloud_cover=img.get("cloud_cover"),
                bounds=request.bounds,
                metadata=img.get("metadata"),
                file_path=img.get("file_path"),
                preview_path=img.get("preview_path")
            )
            db.add(db_img)
            db.commit()
            db.refresh(db_img)
            db_images.append(db_img)
        
        return db_images
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search images: {str(e)}")


@router.get("/images", response_model=List[SatelliteImageResponse])
async def list_images(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Try synthetic data first
    synthetic_data = load_synthetic_data()
    if synthetic_data:
        images = []
        for i, event in enumerate(synthetic_data[skip:skip+limit]):
            images.append(SatelliteImageResponse(
                id=i + 1,
                satellite_name="synthetic-sentinel-2",
                acquisition_date=datetime.fromisoformat(event["timestamp"]),
                cloud_cover=5.0,
                bounds=event["bounds"],
                metadata={"change_type": event["change_type"]},
                file_path=None,
                preview_path=None
            ))
        return images
    
    # Fall back to database
    images = db.query(SatelliteImage).offset(skip).limit(limit).all()
    return images


@router.get("/images/{image_id}", response_model=SatelliteImageResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    # Try synthetic data first
    synthetic_data = load_synthetic_data()
    if synthetic_data and image_id <= len(synthetic_data):
        event = synthetic_data[image_id - 1]
        return SatelliteImageResponse(
            id=image_id,
            satellite_name="synthetic-sentinel-2",
            acquisition_date=datetime.fromisoformat(event["timestamp"]),
            cloud_cover=5.0,
            bounds=event["bounds"],
            metadata={"change_type": event["change_type"]},
            file_path=None,
            preview_path=None
        )
    
    # Fall back to database
    image = db.query(SatelliteImage).filter(SatelliteImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image
