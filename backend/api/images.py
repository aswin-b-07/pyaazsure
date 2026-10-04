import os
import uuid
import random
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from PIL import Image as PILImage, ImageDraw

from backend.database import get_db
from backend.models import Lot, Image
from backend.schemas import ImageResponse

router = APIRouter(prefix="/api/lots", tags=["Images"])

# Base directory for uploads
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{lot_id}/images", response_model=List[ImageResponse], status_code=status.HTTP_201_CREATED)
async def upload_images(
    lot_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads multiple sample onion images for a specific lot.
    """
    lot = db.query(Lot).filter(Lot.lot_id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lot '{lot_id}' not found."
        )

    lot_upload_dir = UPLOADS_DIR / lot_id
    lot_upload_dir.mkdir(parents=True, exist_ok=True)

    uploaded_records = []
    for file in files:
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        unique_img_id = f"IMG-{uuid.uuid4().hex[:8]}"
        file_name = f"{unique_img_id}{ext}"
        save_path = lot_upload_dir / file_name

        # Write file to disk
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)

        # Store relative file path
        rel_path = f"uploads/{lot_id}/{file_name}"

        img_record = Image(
            image_id=unique_img_id,
            lot_id=lot_id,
            file_path=rel_path,
            predicted_class=None,
            confidence=None
        )
        db.add(img_record)
        uploaded_records.append(img_record)

    # Update lot status if needed
    if lot.status == "Registered":
        lot.status = "Images Uploaded"

    db.commit()
    for rec in uploaded_records:
        db.refresh(rec)

    return uploaded_records


@router.post("/{lot_id}/generate-sample-images", response_model=List[ImageResponse], status_code=status.HTTP_201_CREATED)
def generate_sample_images(
    lot_id: str,
    count: int = 10,
    db: Session = Depends(get_db)
):
    """
    Simulates sample capture by generating N synthetic sample onion images for quick testing.
    """
    lot = db.query(Lot).filter(Lot.lot_id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lot '{lot_id}' not found."
        )

    if count < 1 or count > 200:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 200.")

    lot_upload_dir = UPLOADS_DIR / lot_id
    lot_upload_dir.mkdir(parents=True, exist_ok=True)

    generated_records = []
    # Onion color palettes (Purplish red, yellowish orange, brown peel, sprouted green)
    color_palettes = [
        ("#9c27b0", "#e1bee7"), # Purple Red
        ("#e65100", "#ffe0b2"), # Golden Yellow
        ("#bf360c", "#ffccbc"), # Deep Amber/Red
        ("#8d6e63", "#d7ccc8"), # Brown Skin
        ("#2e7d32", "#c8e6c9")  # Sprouted Green accent
    ]

    for i in range(count):
        unique_img_id = f"IMG-{uuid.uuid4().hex[:8]}"
        file_name = f"{unique_img_id}.png"
        save_path = lot_upload_dir / file_name


        # Draw a synthetic onion image using PIL
        img = PILImage.new("RGB", (300, 300), color="#f5f5f5")
        draw = ImageDraw.Draw(img)

        c1, c2 = random.choice(color_palettes)
        # Onion bulb body
        draw.ellipse([50, 50, 250, 250], fill=c1, outline="#3e2723", width=3)
        # Inner rings
        draw.ellipse([80, 80, 220, 220], fill=c2, outline="#4e342e", width=2)
        draw.ellipse([110, 110, 190, 190], fill=c1, outline="#5d4037", width=2)
        # Onion root/sprout top detail
        draw.polygon([(150, 20), (135, 55), (165, 55)], fill="#1b5e20")

        # Label text on image
        draw.text((15, 15), f"Lot: {lot_id}", fill="#212121")
        draw.text((15, 270), f"Sample #{i+1}", fill="#424242")

        img.save(save_path, "PNG")

        rel_path = f"uploads/{lot_id}/{file_name}"
        img_record = Image(
            image_id=unique_img_id,
            lot_id=lot_id,
            file_path=rel_path,
            predicted_class=None,
            confidence=None
        )
        db.add(img_record)
        generated_records.append(img_record)

    if lot.status == "Registered":
        lot.status = "Images Uploaded"

    db.commit()
    for rec in generated_records:
        db.refresh(rec)

    return generated_records


@router.get("/{lot_id}/images", response_model=List[ImageResponse])
def get_lot_images(lot_id: str, db: Session = Depends(get_db)):
    """
    Retrieves all uploaded images for a lot.
    """
    images = db.query(Image).filter(Image.lot_id == lot_id).order_by(Image.id.asc()).all()
    return images
