from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json
import os
from app.db.session import get_db
from app.db.models import ChangeEvent, SatelliteImage
from app.ml.change_detection import ChangeDetector
from app.preprocessing.pipeline import PreprocessingPipeline
from pydantic import BaseModel

router = APIRouter()


class ChangeDetectionRequest(BaseModel):
    image_t1_id: int
    image_t2_id: int
    area_id: Optional[int] = None
    method: str = "baseline"  # baseline, siamese_cnn


class ChangeDetectionResponse(BaseModel):
    id: int
    change_area: float
    change_percentage: float
    confidence: float
    is_human_induced: Optional[bool]
    human_confidence: Optional[float]
    activity_type: Optional[str]
    activity_confidence: Optional[float]
    change_mask_path: Optional[str]
    bounding_geometry: Optional[dict]

    class Config:
        from_attributes = True


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


@router.post("/detect", response_model=ChangeDetectionResponse)
async def detect_change(
    request: ChangeDetectionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Try synthetic data first
    synthetic_data = load_synthetic_data()
    if synthetic_data:
        # Return synthetic change event
        event = synthetic_data[0]  # Use first event
        return ChangeDetectionResponse(
            id=event["change_event_id"],
            change_area=event["change_area"],
            change_percentage=event["change_percentage"],
            confidence=event["confidence"],
            is_human_induced=True,
            human_confidence=0.8,
            activity_type=event["change_type"],
            activity_confidence=0.7,
            change_mask_path=None,
            bounding_geometry=event["bounds"]
        )
    
    # Fall back to actual database
    image_t1 = db.query(SatelliteImage).filter(SatelliteImage.id == request.image_t1_id).first()
    image_t2 = db.query(SatelliteImage).filter(SatelliteImage.id == request.image_t2_id).first()
    
    if not image_t1 or not image_t2:
        raise HTTPException(status_code=404, detail="One or both images not found")
    
    # Create change event
    change_event = ChangeEvent(
        image_t1_id=request.image_t1_id,
        image_t2_id=request.image_t2_id,
        area_id=request.area_id
    )
    db.add(change_event)
    db.commit()
    db.refresh(change_event)
    
    # Run change detection in background
    background_tasks.add_task(
        run_change_detection,
        change_event.id,
        image_t1.file_path,
        image_t2.file_path,
        request.method,
        db
    )
    
    return change_event


@router.get("/events", response_model=list[ChangeDetectionResponse])
async def list_change_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Try synthetic data first
    synthetic_data = load_synthetic_data()
    if synthetic_data:
        events = []
        for event in synthetic_data[skip:skip+limit]:
            events.append(ChangeDetectionResponse(
                id=event["change_event_id"],
                change_area=event["change_area"],
                change_percentage=event["change_percentage"],
                confidence=event["confidence"],
                is_human_induced=True,
                human_confidence=0.8,
                activity_type=event["change_type"],
                activity_confidence=0.7,
                change_mask_path=None,
                bounding_geometry=event["bounds"]
            ))
        return events
    
    # Fall back to database
    events = db.query(ChangeEvent).offset(skip).limit(limit).all()
    return events


@router.get("/events/{event_id}", response_model=ChangeDetectionResponse)
async def get_change_event(event_id: int, db: Session = Depends(get_db)):
    # Try synthetic data first
    synthetic_data = load_synthetic_data()
    if synthetic_data:
        # Find event by ID (event_id = area_id * 100 + 1)
        for event in synthetic_data:
            if event["change_event_id"] == event_id:
                return ChangeDetectionResponse(
                    id=event["change_event_id"],
                    change_area=event["change_area"],
                    change_percentage=event["change_percentage"],
                    confidence=event["confidence"],
                    is_human_induced=True,
                    human_confidence=0.8,
                    activity_type=event["change_type"],
                    activity_confidence=0.7,
                    change_mask_path=None,
                    bounding_geometry=event["bounds"]
                )
    
    # Fall back to database
    event = db.query(ChangeEvent).filter(ChangeEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Change event not found")
    return event


async def run_change_detection(
    event_id: int,
    image_t1_path: str,
    image_t2_path: str,
    method: str,
    db: Session
):
    """Background task to run change detection"""
    try:
        # Preprocess images
        pipeline = PreprocessingPipeline()
        img_t1_processed = await pipeline.load_and_preprocess(image_t1_path)
        img_t2_processed = await pipeline.load_and_preprocess(image_t2_path)
        
        # Run change detection
        detector = ChangeDetector(method=method)
        result = await detector.detect_change(img_t1_processed, img_t2_processed)
        
        # Update database
        event = db.query(ChangeEvent).filter(ChangeEvent.id == event_id).first()
        if event:
            event.change_area = result["change_area"]
            event.change_percentage = result["change_percentage"]
            event.confidence = result["confidence"]
            event.change_mask_path = result.get("change_mask_path")
            event.bounding_geometry = result.get("bounding_geometry")
            event.last_updated = datetime.utcnow()
            db.commit()
    except Exception as e:
        print(f"Change detection failed: {str(e)}")
