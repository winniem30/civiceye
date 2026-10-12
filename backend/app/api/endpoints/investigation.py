from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.session import get_db
from app.db.models import Investigation, ChangeEvent, User
from pydantic import BaseModel

router = APIRouter()


class InvestigationCreateRequest(BaseModel):
    change_event_id: int
    user_id: int
    report: Optional[str] = None


class InvestigationResponse(BaseModel):
    id: int
    change_event_id: int
    user_id: int
    report: Optional[str]
    ai_summary: Optional[str]
    findings: Optional[dict]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/create", response_model=InvestigationResponse)
async def create_investigation(
    request: InvestigationCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new investigation for a change event.
    """
    # Get change event
    change_event = db.query(ChangeEvent).filter(
        ChangeEvent.id == request.change_event_id
    ).first()

    if not change_event:
        raise HTTPException(status_code=404, detail="Change event not found")

    # Get user
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if investigation already exists
    existing = db.query(Investigation).filter(
        Investigation.change_event_id == request.change_event_id,
        Investigation.status == "in_progress"
    ).first()

    if existing:
        return existing

    # Generate AI summary from change event data
    ai_summary = generate_ai_summary(change_event)

    # Create investigation
    investigation = Investigation(
        change_event_id=request.change_event_id,
        user_id=request.user_id,
        report=request.report,
        ai_summary=ai_summary,
        findings={
            "change_area": change_event.change_area,
            "change_percentage": change_event.change_percentage,
            "confidence": change_event.confidence,
            "is_human_induced": change_event.is_human_induced,
            "activity_type": change_event.activity_type
        },
        status="in_progress",
        created_at=datetime.utcnow()
    )

    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    return investigation


@router.get("/list", response_model=list[InvestigationResponse])
async def list_investigations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List investigations with optional filters"""
    query = db.query(Investigation)

    if status:
        query = query.filter(Investigation.status == status)

    if user_id:
        query = query.filter(Investigation.user_id == user_id)

    investigations = query.order_by(Investigation.created_at.desc()).offset(skip).limit(limit).all()
    return investigations


@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(investigation_id: int, db: Session = Depends(get_db)):
    """Get a specific investigation"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id
    ).first()

    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    return investigation


@router.put("/{investigation_id}/complete")
async def complete_investigation(
    investigation_id: int,
    report: str,
    db: Session = Depends(get_db)
):
    """Complete an investigation with a final report"""
    investigation = db.query(Investigation).filter(
        Investigation.id == investigation_id
    ).first()

    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    investigation.status = "completed"
    investigation.report = report
    investigation.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(investigation)

    return investigation


def generate_ai_summary(change_event: ChangeEvent) -> str:
    """Generate an AI summary for the investigation"""
    summary_parts = []

    # Basic change info
    summary_parts.append(
        f"Change event #{change_event.id} detected with "
        f"{change_event.change_percentage:.2f}% area change."
    )

    # Human vs natural
    if change_event.is_human_induced is not None:
        if change_event.is_human_induced:
            summary_parts.append(
                f"Activity classified as human-induced with "
                f"{change_event.human_confidence * 100:.1f}% confidence."
            )
        else:
            summary_parts.append(
                f"Activity classified as natural with "
                f"{(1 - change_event.human_confidence) * 100:.1f}% confidence."
            )

    # Activity type
    if change_event.activity_type:
        summary_parts.append(
            f"Activity type identified as: {change_event.activity_type} "
            f"({change_event.activity_confidence * 100:.1f}% confidence)."
        )

    # Risk level based on confidence
    if change_event.confidence > 0.8:
        summary_parts.append("High confidence detection requires immediate attention.")
    elif change_event.confidence > 0.5:
        summary_parts.append("Moderate confidence detection recommended for review.")
    else:
        summary_parts.append("Low confidence detection - manual verification recommended.")

    return " ".join(summary_parts)
