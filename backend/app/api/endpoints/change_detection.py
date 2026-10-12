from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.session import get_db
from app.db.models import ChangeEvent, Observation, Alert
from app.ml.change_detection import get_change_detector
from app.ml.classification import BaselineHumanClassifier, BaselineActivityClassifier
from app.ml.risk_assessment import RiskAssessmentEngine
from app.preprocessing.pipeline import PreprocessingPipeline
from pydantic import BaseModel
import numpy as np

router = APIRouter()


class ChangeDetectionRequest(BaseModel):
    observation_t1_id: int
    observation_t2_id: int
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
    last_updated: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/detect", response_model=ChangeDetectionResponse)
async def detect_change(
    request: ChangeDetectionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Get observations
    obs_t1 = db.query(Observation).filter(Observation.id == request.observation_t1_id).first()
    obs_t2 = db.query(Observation).filter(Observation.id == request.observation_t2_id).first()

    if not obs_t1 or not obs_t2:
        raise HTTPException(status_code=404, detail="One or both observations not found")

    if obs_t1.processing_status != "completed" or obs_t2.processing_status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Both observations must be processed before change detection"
        )

    # Create change event
    change_event = ChangeEvent(
        image_t1_id=obs_t1.satellite_image_id,
        image_t2_id=obs_t2.satellite_image_id,
        area_id=request.area_id
    )
    db.add(change_event)
    db.commit()
    db.refresh(change_event)

    # Run change detection in background
    background_tasks.add_task(
        run_change_detection,
        change_event.id,
        obs_t1,
        obs_t2,
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
    events = db.query(ChangeEvent).offset(skip).limit(limit).all()
    return events


@router.get("/events/{event_id}", response_model=ChangeDetectionResponse)
async def get_change_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(ChangeEvent).filter(ChangeEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Change event not found")
    return event


async def run_change_detection(
    event_id: int,
    obs_t1: Observation,
    obs_t2: Observation,
    method: str,
    db: Session
):
    """Background task to run change detection with classification and risk assessment (MVP - simplified)"""
    try:
        # For MVP, generate mock index data
        def generate_mock_indices() -> dict:
            """Generate mock spectral indices"""
            size = 100
            return {
                "ndvi": np.random.rand(size, size) * 0.8 - 0.2,  # NDVI typically -0.2 to 0.6
                "ndwi": np.random.rand(size, size) * 0.6 - 0.3,  # NDWI typically -0.3 to 0.3
                "ndbi": np.random.rand(size, size) * 0.4 - 0.1  # NDBI typically -0.1 to 0.3
            }

        indices_t1 = generate_mock_indices()
        indices_t2 = generate_mock_indices()

        # Create image-like data for change detection
        img_t1 = {
            "image": np.stack([indices_t1["ndvi"], indices_t1["ndwi"], indices_t1["ndbi"]]),
            "indices": indices_t1
        }

        img_t2 = {
            "image": np.stack([indices_t2["ndvi"], indices_t2["ndwi"], indices_t2["ndbi"]]),
            "indices": indices_t2
        }

        # Run change detection
        detector = get_change_detector(method)
        change_result = await detector.detect_change(img_t1, img_t2)

        # Run human vs natural classification
        human_classifier = BaselineHumanClassifier()
        classification_data = {
            "change_mask": change_result.get("change_mask"),
            "change_percentage": change_result.get("change_percentage", 0),
            "indices_t1": indices_t1,
            "indices_t2": indices_t2
        }
        human_result = await human_classifier.classify(classification_data)

        # Run activity classification
        activity_classifier = BaselineActivityClassifier()
        activity_result = await activity_classifier.classify(classification_data)

        # Run risk assessment
        risk_engine = RiskAssessmentEngine()
        # Create basic GIS context from observation bounds
        gis_context = {
            "is_protected_area": False,
            "proximity_to_water": 5000,
            "proximity_to_forest": 5000,
            "proximity_to_urban": 10000,
            "proximity_to_roads": 1000,
            "population_density": 500,
            "slope": 10,
            "land_cover_type": "mixed"
        } if obs_t1.aoi_bounds else None

        risk_assessment = risk_engine.assess_risk(
            change_data={**change_result, "is_human_induced": human_result.get("is_human_induced")},
            gis_context=gis_context,
            classification=activity_result
        )

        # Update database with all results
        event = db.query(ChangeEvent).filter(ChangeEvent.id == event_id).first()
        if event:
            event.change_area = change_result["change_area"]
            event.change_percentage = change_result["change_percentage"]
            event.confidence = change_result["confidence"]
            event.bounding_geometry = change_result.get("bounding_geometry")
            event.is_human_induced = human_result.get("is_human_induced")
            event.human_confidence = human_result.get("confidence")
            event.activity_type = activity_result.get("activity_type")
            event.activity_confidence = activity_result.get("confidence")
            event.last_updated = datetime.utcnow()
            db.commit()

            # Generate alert automatically for high-risk changes
            if (event.is_human_induced and
                event.human_confidence > 0.6 and
                event.change_percentage > 1.0):
                # Check if alert already exists
                existing_alert = db.query(Alert).filter(
                    Alert.change_event_id == event_id
                ).first()

                if not existing_alert:
                    # Determine severity
                    severity = "medium"
                    if event.human_confidence > 0.8:
                        severity = "critical"
                    elif event.human_confidence > 0.7:
                        severity = "high"

                    # Create alert
                    alert = Alert(
                        change_event_id=event_id,
                        alert_type="standard",
                        severity=severity,
                        status="open",
                        title=f"{event.activity_type.capitalize() if event.activity_type else 'Change'} Detected",
                        description=f"Human-induced {event.activity_type or 'change'} detected with {event.change_percentage:.2f}% area change",
                        location=f"Event #{event_id}",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(alert)
                    db.commit()
                    print(f"Alert generated for event {event_id}")

        print(f"Change detection completed for event {event_id}")

    except Exception as e:
        print(f"Change detection failed for event {event_id}: {str(e)}")
        import traceback
        traceback.print_exc()
