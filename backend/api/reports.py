from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import Lot, Image, Report
from backend.schemas import ReportResponse, DashboardStats, DefectBreakdown, LotResponse
from backend.ml.mock_inference import mock_inference
from backend.services.grading import calculate_lot_grade
from backend.services.report_service import generate_report_explanation

router = APIRouter(tags=["Reports & Analytics"])


@router.post("/api/lots/{lot_id}/analyze", response_model=ReportResponse)
def analyze_lot(lot_id: str, db: Session = Depends(get_db)):
    """
    Executes Mock AI inference on all images in a lot, runs the grading engine,
    updates database records, and generates the digital quality report.
    """
    lot = db.query(Lot).filter(Lot.lot_id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lot '{lot_id}' not found."
        )

    images = db.query(Image).filter(Image.lot_id == lot_id).all()
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No images found for lot '{lot_id}'. Upload images before analyzing."
        )

    predictions = []
    # Step 1: Execute Mock AI Inference on each image
    for img in images:
        pred = mock_inference(img.file_path)
        img.predicted_class = pred["predicted_class"]
        img.confidence = pred["confidence"]
        predictions.append(pred)

    db.commit()

    # Step 2: Run Grading Engine
    grading_result = calculate_lot_grade(predictions)

    # Step 3: Update or Create Report Record in REPORTS table
    existing_report = db.query(Report).filter(Report.lot_id == lot_id).first()
    if existing_report:
        report = existing_report
    else:
        report = Report(lot_id=lot_id)

    report.grade_a_pct = grading_result["grade_a_pct"]
    report.urs_pct = grading_result["urs_pct"]
    report.defective_pct = grading_result["defective_pct"]
    report.avg_confidence = grading_result["avg_confidence"]
    report.needs_review = grading_result["needs_review"]
    report.healthy_count = grading_result["healthy_count"]
    report.damaged_count = grading_result["damaged_count"]
    report.rotten_count = grading_result["rotten_count"]
    report.sprouted_count = grading_result["sprouted_count"]
    report.undersized_count = grading_result["undersized_count"]
    report.total_analyzed = grading_result["total_analyzed"]

    # Step 4: Update Lot status
    lot.status = grading_result["status"]

    db.add(report)
    db.commit()
    db.refresh(report)
    db.refresh(lot)

    # Generate narrative explanation
    explanation = generate_report_explanation(grading_result)

    return ReportResponse(
        id=report.id,
        lot_id=report.lot_id,
        centre_name=lot.centre_name,
        date=lot.date,
        total_analyzed=report.total_analyzed,
        grade_a_pct=report.grade_a_pct,
        urs_pct=report.urs_pct,
        defective_pct=report.defective_pct,
        avg_confidence=report.avg_confidence,
        needs_review=report.needs_review,
        status=lot.status,
        defect_breakdown=DefectBreakdown(
            healthy=report.healthy_count,
            damaged=report.damaged_count,
            rotten=report.rotten_count,
            sprouted=report.sprouted_count,
            undersized=report.undersized_count
        ),
        explanation=explanation,
        created_at=report.created_at
    )


@router.get("/api/lots/{lot_id}/report", response_model=ReportResponse)
def get_lot_report(lot_id: str, db: Session = Depends(get_db)):
    """
    Fetches the digital quality report for a specific lot.
    """
    lot = db.query(Lot).filter(Lot.lot_id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lot '{lot_id}' not found."
        )

    report = db.query(Report).filter(Report.lot_id == lot_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report for lot '{lot_id}' has not been generated yet. Run analysis first."
        )

    report_dict = {
        "grade_a_pct": report.grade_a_pct,
        "urs_pct": report.urs_pct,
        "defective_pct": report.defective_pct,
        "healthy_count": report.healthy_count,
        "undersized_count": report.undersized_count,
        "damaged_count": report.damaged_count,
        "rotten_count": report.rotten_count,
        "sprouted_count": report.sprouted_count,
        "total_analyzed": report.total_analyzed,
        "avg_confidence": report.avg_confidence,
        "needs_review": report.needs_review,
        "status": lot.status
    }
    explanation = generate_report_explanation(report_dict)

    return ReportResponse(
        id=report.id,
        lot_id=report.lot_id,
        centre_name=lot.centre_name,
        date=lot.date,
        total_analyzed=report.total_analyzed,
        grade_a_pct=report.grade_a_pct,
        urs_pct=report.urs_pct,
        defective_pct=report.defective_pct,
        avg_confidence=report.avg_confidence,
        needs_review=report.needs_review,
        status=lot.status,
        defect_breakdown=DefectBreakdown(
            healthy=report.healthy_count,
            damaged=report.damaged_count,
            rotten=report.rotten_count,
            sprouted=report.sprouted_count,
            undersized=report.undersized_count
        ),
        explanation=explanation,
        created_at=report.created_at
    )


@router.get("/api/reports", response_model=List[ReportResponse])
def list_reports(db: Session = Depends(get_db)):
    """
    Retrieves all generated quality reports across all lots.
    """
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    result = []
    for rep in reports:
        lot = db.query(Lot).filter(Lot.lot_id == rep.lot_id).first()
        report_dict = {
            "grade_a_pct": rep.grade_a_pct,
            "urs_pct": rep.urs_pct,
            "defective_pct": rep.defective_pct,
            "healthy_count": rep.healthy_count,
            "undersized_count": rep.undersized_count,
            "damaged_count": rep.damaged_count,
            "rotten_count": rep.rotten_count,
            "sprouted_count": rep.sprouted_count,
            "total_analyzed": rep.total_analyzed,
            "avg_confidence": rep.avg_confidence,
            "needs_review": rep.needs_review,
            "status": lot.status if lot else "Unknown"
        }
        explanation = generate_report_explanation(report_dict)

        result.append(ReportResponse(
            id=rep.id,
            lot_id=rep.lot_id,
            centre_name=lot.centre_name if lot else "N/A",
            date=lot.date if lot else "N/A",
            total_analyzed=rep.total_analyzed,
            grade_a_pct=rep.grade_a_pct,
            urs_pct=rep.urs_pct,
            defective_pct=rep.defective_pct,
            avg_confidence=rep.avg_confidence,
            needs_review=rep.needs_review,
            status=lot.status if lot else "Unknown",
            defect_breakdown=DefectBreakdown(
                healthy=rep.healthy_count,
                damaged=rep.damaged_count,
                rotten=rep.rotten_count,
                sprouted=rep.sprouted_count,
                undersized=rep.undersized_count
            ),
            explanation=explanation,
            created_at=rep.created_at
        ))
    return result


@router.get("/api/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated metrics for the overview dashboard.
    """
    total_lots = db.query(Lot).count()

    total_onions = db.query(func.sum(Report.total_analyzed)).scalar() or 0
    avg_grade_a = db.query(func.avg(Report.grade_a_pct)).scalar() or 0.0
    lots_needing_review = db.query(Report).filter(Report.needs_review == True).count()

    recent_lots_db = db.query(Lot).order_by(Lot.created_at.desc()).limit(5).all()
    recent_lots = []
    for lot in recent_lots_db:
        img_count = db.query(Image).filter(Image.lot_id == lot.lot_id).count()
        recent_lots.append(LotResponse(
            id=lot.id,
            lot_id=lot.lot_id,
            centre_name=lot.centre_name,
            date=lot.date,
            sample_size_expected=lot.sample_size_expected,
            status=lot.status,
            created_at=lot.created_at,
            image_count=img_count
        ))

    return DashboardStats(
        total_lots=total_lots,
        total_onions_analyzed=int(total_onions),
        avg_grade_a_pct=round(float(avg_grade_a), 2),
        lots_needing_review=lots_needing_review,
        recent_lots=recent_lots
    )
