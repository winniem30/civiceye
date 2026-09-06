from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
from app.db.session import get_db
from app.db.models import Area
from pydantic import BaseModel
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

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


def load_synthetic_data():
    """Load synthetic data for testing"""
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "synthetic_areas.json")
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                return json.load(f)
    except:
        pass
    return None


@router.post("/", response_model=AreaResponse)
async def create_area(area: AreaCreate, db: Session = Depends(get_db)):
    db_area = Area(
        name=area.name,
        description=area.description,
        bounds=area.bounds
    )
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    
    return db_area


@router.get("/", response_model=List[AreaResponse])
async def list_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Try synthetic data first
    synthetic_data = load_synthetic_data()
    if synthetic_data:
        areas = synthetic_data[skip:skip+limit]
        return [
            AreaResponse(
                id=area["id"],
                name=area["name"],
                description=area["description"],
                bounds=area["bounds"],
                geometry=None
            )
            for area in areas
        ]
    
    # Fall back to database
    areas = db.query(Area).offset(skip).limit(limit).all()
    
    response = []
    for area in areas:
        area_dict = {
            "id": area.id,
            "name": area.name,
            "description": area.description,
            "bounds": area.bounds,
            "geometry": None
        }
        if area.geometry:
            shape = to_shape(area.geometry)
            area_dict["geometry"] = mapping(shape)
        response.append(AreaResponse(**area_dict))
    
    return response


@router.get("/{area_id}", response_model=AreaResponse)
async def get_area(area_id: int, db: Session = Depends(get_db)):
    # Try synthetic data first
    synthetic_data = load_synthetic_data()
    if synthetic_data:
        for area in synthetic_data:
            if area["id"] == area_id:
                return AreaResponse(
                    id=area["id"],
                    name=area["name"],
                    description=area["description"],
                    bounds=area["bounds"],
                    geometry=None
                )
    
    # Fall back to database
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    area_dict = {
        "id": area.id,
        "name": area.name,
        "description": area.description,
        "bounds": area.bounds,
        "geometry": None
    }
    if area.geometry:
        shape = to_shape(area.geometry)
        area_dict["geometry"] = mapping(shape)
    
    return AreaResponse(**area_dict)


@router.delete("/{area_id}")
async def delete_area(area_id: int, db: Session = Depends(get_db)):
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    db.delete(area)
    db.commit()
    
    return {"message": "Area deleted successfully"}
