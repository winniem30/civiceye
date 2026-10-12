from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
import os
import numpy as np
from PIL import Image
import io
from app.db.session import get_db
from app.db.models import Observation
from app.core.config import settings

router = APIRouter()


@router.get("/raster/{observation_id}/{layer_name}")
async def get_raster_tile(
    observation_id: int,
    layer_name: str,
    width: int = 512,
    height: int = 512,
    db: Session = Depends(get_db)
):
    """
    Get a raster layer as an image tile (MVP - simplified without rasterio).

    Returns a PNG image of the specified layer (band or index).
    """
    # Get observation
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

    # Get layer file path
    layer_path = None
    if layer_name in (observation.band_files or {}):
        layer_path = observation.band_files[layer_name]
    elif layer_name in (observation.index_files or {}):
        layer_path = observation.index_files[layer_name]
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Layer {layer_name} not found. Available: {list((observation.band_files or {}).keys()) + list((observation.index_files or {}).keys())}"
        )

    # For MVP, generate a mock image if file doesn't exist or is a placeholder
    try:
        # Generate a random image for MVP
        data = np.random.rand(height, width) * 255
        data_norm = data.astype(np.uint8)

        # Create PIL image
        img = Image.fromarray(data_norm, mode='L')

        # Convert to PNG
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return Response(content=img_byte_arr.getvalue(), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate raster tile: {str(e)}")


@router.get("/raster/{observation_id}/{layer_name}/metadata")
async def get_raster_metadata(
    observation_id: int,
    layer_name: str,
    db: Session = Depends(get_db)
):
    """Get metadata for a raster layer (MVP - simplified)"""
    # Get observation
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

    # Return mock metadata for MVP
    return {
        "layer_name": layer_name,
        "observation_id": observation_id,
        "crs": "EPSG:4326",
        "bounds": observation.aoi_bounds or {},
        "width": 512,
        "height": 512,
        "dtype": "uint8",
        "note": "Mock metadata for MVP"
    }
