import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import Lot, Image, Report
from backend.schemas import LotCreate, LotResponse

router = APIRouter(prefix="/api/lots", tags=["Lots"])


def generate_next_lot_id(db: Session) -> str:
    """
    Auto-generates sequential Lot IDs in the format: ONN-2026-00001
    """
    year = 2026
    # Get total count of lots in database
    max_id = db.query(func.max(Lot.id)).scalar() or 0
    next_num = max_id + 1
    return f"ONN-{year}-{next_num:05d}"


@router.post("", response_model=LotResponse, status_code=status.HTTP_201_CREATED)
def create_lot(lot_in: LotCreate, db: Session = Depends(get_db)):
    """
    Registers a new onion lot in the database with auto-generated Lot ID.
    """
    lot_id = generate_next_lot_id(db)

    # Ensure uniqueness just in case
    while db.query(Lot).filter(Lot.lot_id == lot_id).first():
        num = int(lot_id.split("-")[-1]) + 1
        lot_id = f"ONN-2026-{num:05d}"

    new_lot = Lot(
        lot_id=lot_id,
        centre_name=lot_in.centre_name,
        date=lot_in.date,
        sample_size_expected=lot_in.sample_size_expected,
        status="Registered"
    )

    db.add(new_lot)
    db.commit()
    db.refresh(new_lot)

    return LotResponse(
        id=new_lot.id,
        lot_id=new_lot.lot_id,
        centre_name=new_lot.centre_name,
        date=new_lot.date,
        sample_size_expected=new_lot.sample_size_expected,
        status=new_lot.status,
        created_at=new_lot.created_at,
        image_count=0
    )


@router.get("", response_model=List[LotResponse])
def list_lots(
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieves all registered onion lots with optional status filter & search.
    """
    query = db.query(Lot)

    if status_filter:
        query = query.filter(Lot.status == status_filter)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Lot.lot_id.ilike(search_pattern)) | (Lot.centre_name.ilike(search_pattern))
        )

    lots = query.order_by(Lot.created_at.desc()).all()

    result = []
    for lot in lots:
        img_count = db.query(Image).filter(Image.lot_id == lot.lot_id).count()
        result.append(LotResponse(
            id=lot.id,
            lot_id=lot.lot_id,
            centre_name=lot.centre_name,
            date=lot.date,
            sample_size_expected=lot.sample_size_expected,
            status=lot.status,
            created_at=lot.created_at,
            image_count=img_count
        ))

    return result


@router.get("/{lot_id}", response_model=LotResponse)
def get_lot(lot_id: str, db: Session = Depends(get_db)):
    """
    Retrieves a single lot by its lot_id.
    """
    lot = db.query(Lot).filter(Lot.lot_id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lot with ID '{lot_id}' not found."
        )

    img_count = db.query(Image).filter(Image.lot_id == lot.lot_id).count()
    return LotResponse(
        id=lot.id,
        lot_id=lot.lot_id,
        centre_name=lot.centre_name,
        date=lot.date,
        sample_size_expected=lot.sample_size_expected,
        status=lot.status,
        created_at=lot.created_at,
        image_count=img_count
    )
