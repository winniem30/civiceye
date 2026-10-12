from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
from app.db.session import get_db
from app.db.models import SatelliteImage, Observation
from app.satellite.providers import get_satellite_provider
from app.preprocessing.pipeline import PreprocessingPipeline
from pydantic import BaseModel, validator

router = APIRouter()


class SatelliteImageResponse(BaseModel):
    id: int
    satellite_name: str
    stac_id: str
    acquisition_date: datetime
    cloud_cover: Optional[float]
    bounds: dict
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class ObservationSearchRequest(BaseModel):
    bounds: dict  # {min_x, min_y, max_x, max_y}
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_cloud_cover: Optional[float] = 20.0
    satellite: Optional[str] = "sentinel-2"
    
    @validator('bounds')
    def validate_bounds(cls, v):
        required_keys = ['min_x', 'min_y', 'max_x', 'max_y']
        if not all(k in v for k in required_keys):
            raise ValueError(f"Bounds must contain {required_keys}")
        if v['min_x'] >= v['max_x'] or v['min_y'] >= v['max_y']:
            raise ValueError("Invalid bounds: min must be less than max")
        return v


class ProcessObservationRequest(BaseModel):
    stac_id: str
    aoi_bounds: Optional[dict] = None  # Optional AOI for clipping
    clip_to_aoi: bool = True


class ObservationResponse(BaseModel):
    id: int
    stac_id: str
    processing_status: str
    aoi_bounds: Optional[dict]
    band_files: Optional[dict]
    index_files: Optional[dict]
    metadata: Optional[dict]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/search", response_model=List[SatelliteImageResponse])
async def search_observations(
    request: ObservationSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for satellite observations using STAC API.
    
    Returns real Sentinel-2 observations matching the criteria.
    """
    # Validate bounds
    try:
        required_keys = ['min_x', 'min_y', 'max_x', 'max_y']
        if not all(k in request.bounds for k in required_keys):
            raise HTTPException(
                status_code=400,
                detail=f"Bounds must contain {required_keys}"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Get satellite provider
    provider = get_satellite_provider(request.satellite)
    
    try:
        # Search for observations
        images = await provider.search_images(
            bounds=request.bounds,
            start_date=request.start_date,
            end_date=request.end_date,
            max_cloud_cover=request.max_cloud_cover
        )
        
        if not images:
            raise HTTPException(
                status_code=404,
                detail="No observations found matching the criteria"
            )
        
        # Store or update in database
        db_images = []
        for img in images:
            # Check if already exists
            existing = db.query(SatelliteImage).filter(
                SatelliteImage.stac_id == img["stac_id"]
            ).first()
            
            if existing:
                db_images.append(existing)
            else:
                db_img = SatelliteImage(
                    satellite_name=request.satellite,
                    stac_id=img["stac_id"],
                    acquisition_date=img["acquisition_date"],
                    cloud_cover=img.get("cloud_cover"),
                    bounds=img["bounds"],
                    image_metadata=img.get("metadata"),
                    bands=img.get("metadata", {}).get("bands", [])
                )
                db.add(db_img)
                db.commit()
                db.refresh(db_img)
                db_images.append(db_img)
        
        return db_images
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search observations: {str(e)}")


@router.post("/process", response_model=ObservationResponse)
async def process_observation(
    request: ProcessObservationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Process a satellite observation: download bands, clip to AOI, calculate indices.
    
    Processing happens asynchronously in the background.
    """
    # Find the satellite image
    sat_image = db.query(SatelliteImage).filter(
        SatelliteImage.stac_id == request.stac_id
    ).first()
    
    if not sat_image:
        raise HTTPException(status_code=404, detail="Satellite image not found")
    
    # Check if already processed with same AOI
    existing_obs = db.query(Observation).filter(
        Observation.stac_id == request.stac_id,
        Observation.aoi_bounds == request.aoi_bounds
    ).first()
    
    if existing_obs and existing_obs.processing_status == "completed":
        return existing_obs
    
    # Create new observation record
    observation = Observation(
        satellite_image_id=sat_image.id,
        stac_id=request.stac_id,
        aoi_bounds=request.aoi_bounds,
        processing_status="processing",
        processing_timestamp=datetime.utcnow()
    )
    db.add(observation)
    db.commit()
    db.refresh(observation)
    
    # Process in background
    background_tasks.add_task(
        _process_observation_task,
        observation.id,
        sat_image.image_metadata.get("assets", {}),
        request.aoi_bounds,
        request.clip_to_aoi,
        db
    )
    
    return observation


async def _process_observation_task(
    observation_id: int,
    assets: dict,
    aoi_bounds: Optional[dict],
    clip_to_aoi: bool,
    db: Session
):
    """Background task to process observation"""
    pipeline = PreprocessingPipeline()
    
    try:
        # Process the observation
        result = await pipeline.process_sentinel2_observation(
            stac_id=str(observation_id),
            assets=assets,
            bounds=aoi_bounds,
            clip_to_aoi=clip_to_aoi
        )
        
        # Update database
        observation = db.query(Observation).filter(
            Observation.id == observation_id
        ).first()
        
        if observation:
            observation.processing_status = result.get("processing_status", "failed")
            observation.processing_timestamp = datetime.utcnow()

            if result.get("processing_status") == "completed":
                observation.band_files = result.get("band_files")
                observation.index_files = result.get("index_files")
                observation.image_metadata = result.get("metadata")
            else:
                observation.error_message = result.get("error")

            db.commit()
            
    except Exception as e:
        # Update with error
        observation = db.query(Observation).filter(
            Observation.id == observation_id
        ).first()
        if observation:
            observation.processing_status = "failed"
            observation.error_message = str(e)
            observation.processing_timestamp = datetime.utcnow()
            db.commit()
    finally:
        await pipeline.close()


@router.get("/observations", response_model=List[ObservationResponse])
async def list_observations(
    skip: int = 0,
    limit: int = 100,
    processing_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List processed observations"""
    query = db.query(Observation)
    
    if processing_status:
        query = query.filter(Observation.processing_status == processing_status)
    
    observations = query.order_by(Observation.created_at.desc()).offset(skip).limit(limit).all()
    return observations


@router.get("/observations/{observation_id}", response_model=ObservationResponse)
async def get_observation(
    observation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific observation"""
    observation = db.query(Observation).filter(
        Observation.id == observation_id
    ).first()
    
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    return observation


@router.get("/observations/{observation_id}/layers")
async def get_observation_layers(
    observation_id: int,
    db: Session = Depends(get_db)
):
    """Get available layers for an observation"""
    observation = db.query(Observation).filter(
        Observation.id == observation_id
    ).first()
    
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    if observation.processing_status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Observation not processed yet. Status: {observation.processing_status}"
        )
    
    return {
        "observation_id": observation_id,
        "stac_id": observation.stac_id,
        "bands": observation.band_files or {},
        "indices": observation.index_files or {},
        "metadata": observation.image_metadata
    }
