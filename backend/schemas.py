from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


# --- LOT SCHEMAS ---
class LotCreate(BaseModel):
    centre_name: str = Field(..., json_schema_extra={"example": "Nashik Mandi Hub 1"})
    date: str = Field(..., json_schema_extra={"example": "2026-10-03"})
    sample_size_expected: int = Field(default=100, ge=1, json_schema_extra={"example": 100})


class LotResponse(BaseModel):
    id: int
    lot_id: str
    centre_name: str
    date: str
    sample_size_expected: int
    status: str
    created_at: datetime
    image_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


# --- IMAGE SCHEMAS ---
class ImageResponse(BaseModel):
    id: int
    image_id: str
    lot_id: str
    file_path: str
    predicted_class: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- REPORT SCHEMAS ---
class DefectBreakdown(BaseModel):
    healthy: int = 0
    damaged: int = 0
    rotten: int = 0
    sprouted: int = 0
    undersized: int = 0


class ReportResponse(BaseModel):
    id: int
    lot_id: str
    centre_name: Optional[str] = None
    date: Optional[str] = None
    total_analyzed: int
    grade_a_pct: float
    urs_pct: float
    defective_pct: float
    avg_confidence: float
    needs_review: bool
    status: str
    defect_breakdown: DefectBreakdown
    explanation: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- DASHBOARD / STATS SCHEMAS ---
class DashboardStats(BaseModel):
    total_lots: int
    total_onions_analyzed: int
    avg_grade_a_pct: float
    lots_needing_review: int
    recent_lots: List[LotResponse]
