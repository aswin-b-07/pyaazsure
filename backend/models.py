import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Lot(Base):
    """
    LOTS TABLE
    Stores metadata for registered onion lots.
    """
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lot_id = Column(String, unique=True, index=True, nullable=False)  # e.g., ONN-2026-00001
    centre_name = Column(String, nullable=False)                       # e.g., Nashik Mandi Hub 1
    date = Column(String, nullable=False)                              # YYYY-MM-DD
    sample_size_expected = Column(Integer, default=100)               # Target sample size
    status = Column(String, default="Registered")                     # Registered, Images Uploaded, AI Assessment Complete, Needs Human Review
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    images = relationship("Image", back_populates="lot", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="lot", uselist=False, cascade="all, delete-orphan")


class Image(Base):
    """
    IMAGES TABLE
    Stores uploaded onion sample images and AI prediction results.
    """
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_id = Column(String, unique=True, index=True, nullable=False)
    lot_id = Column(String, ForeignKey("lots.lot_id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    predicted_class = Column(String, nullable=True)  # Healthy, Damaged, Rotten, Sprouted, Undersized
    confidence = Column(Float, nullable=True)       # AI confidence score (0.0 to 100.0 or 0.70 to 0.99)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    lot = relationship("Lot", back_populates="images")


class Report(Base):
    """
    REPORTS TABLE
    Stores aggregated lot-level grading metrics and review status.
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lot_id = Column(String, ForeignKey("lots.lot_id", ondelete="CASCADE"), unique=True, nullable=False)
    grade_a_pct = Column(Float, nullable=False, default=0.0)      # % Healthy
    urs_pct = Column(Float, nullable=False, default=0.0)          # % Undersized
    defective_pct = Column(Float, nullable=False, default=0.0)    # % Damaged + Rotten + Sprouted
    avg_confidence = Column(Float, nullable=False, default=0.0)   # Average AI confidence
    needs_review = Column(Boolean, nullable=False, default=False)  # True if avg_confidence < 80%

    # Detailed defect breakdown counts
    healthy_count = Column(Integer, default=0)
    damaged_count = Column(Integer, default=0)
    rotten_count = Column(Integer, default=0)
    sprouted_count = Column(Integer, default=0)
    undersized_count = Column(Integer, default=0)
    total_analyzed = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    lot = relationship("Lot", back_populates="report")
