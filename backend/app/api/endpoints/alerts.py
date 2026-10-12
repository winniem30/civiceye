from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.session import get_db
from app.db.models import Alert, ChangeEvent
from app.ml.risk_assessment import RiskLevel
from pydantic import BaseModel

router = APIRouter()


class AlertResponse(BaseModel):
    id: int
    change_event_id: Optional[int]
    alert_type: str
    severity: str
    status: str
    title: str
    description: str
    location: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertCreateRequest(BaseModel):
    change_event_id: int
    alert_type: str = "standard"  # standard, unreported_change
    title: Optional[str] = None
    description: Optional[str] = None


@router.post("/generate", response_model=AlertResponse)
async def generate_alert(
    request: AlertCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an alert for a change event based on risk assessment.
    """
    # Get change event
    change_event = db.query(ChangeEvent).filter(
        ChangeEvent.id == request.change_event_id
    ).first()

    if not change_event:
        raise HTTPException(status_code=404, detail="Change event not found")

    # Check if alert already exists
    existing_alert = db.query(Alert).filter(
        Alert.change_event_id == request.change_event_id
    ).first()

    if existing_alert:
        return existing_alert

    # Determine severity based on change event
    severity = "low"
    if change_event.confidence > 0.8:
        severity = "high"
    elif change_event.confidence > 0.5:
        severity = "medium"

    # Override to critical if human-induced and high confidence
    if change_event.is_human_induced and change_event.human_confidence > 0.7:
        severity = "critical"

    # Generate title and description if not provided
    title = request.title
    if not title:
        activity = change_event.activity_type or "unknown"
        title = f"{activity.capitalize()} Detected" if activity != "unknown" else "Change Detected"

    description = request.description
    if not description:
        description = f"Change detected with {change_event.change_percentage:.2f}% area change"
        if change_event.is_human_induced:
            description += ". Human-induced activity confirmed"

    # Create alert
    alert = Alert(
        change_event_id=request.change_event_id,
        alert_type=request.alert_type,
        severity=severity,
        status="open",
        title=title,
        description=description,
        location=f"Event #{request.change_event_id}",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


@router.get("/list", response_model=list[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List alerts with optional filters"""
    query = db.query(Alert)

    if status:
        query = query.filter(Alert.status == status)

    if severity:
        query = query.filter(Alert.severity == severity)

    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}/status")
async def update_alert_status(
    alert_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update alert status"""
    valid_statuses = ["open", "investigating", "resolved", "dismissed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = status
    alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)

    return alert
