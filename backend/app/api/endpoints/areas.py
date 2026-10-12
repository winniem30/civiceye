from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.db.models import Area
from pydantic import BaseModel

router = APIRouter()


class AreaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    bounds: dict  # {min_x, min_y, max_x, max_y}
    geometry: Optional[dict] = None


class AreaResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    bounds: dict
    geometry: Optional[dict]

    class Config:
        from_attributes = True


@router.post("/", response_model=AreaResponse)
async def create_area(area: AreaCreate, db: Session = Depends(get_db)):
    db_area = Area(
        name=area.name,
        description=area.description,
        bounds=area.bounds,
        geometry=area.geometry  # Store as JSON for MVP
    )
    db.add(db_area)
    db.commit()
    db.refresh(db_area)

    return db_area


@router.get("/", response_model=List[AreaResponse])
async def list_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    areas = db.query(Area).offset(skip).limit(limit).all()
    return areas


@router.get("/{area_id}", response_model=AreaResponse)
async def get_area(area_id: int, db: Session = Depends(get_db)):
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area


@router.delete("/{area_id}")
async def delete_area(area_id: int, db: Session = Depends(get_db)):
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    db.delete(area)
    db.commit()

    return {"message": "Area deleted successfully"}
