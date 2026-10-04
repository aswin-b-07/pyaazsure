import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_full_lot_assessment_pipeline():
    """
    Integration test for complete workflow:
    1. Register Lot
    2. Generate synthetic sample images
    3. Run AI analysis
    4. Retrieve quality report
    """
    # 1. Register Lot
    reg_response = client.post("/api/lots", json={
        "centre_name": "Test Mandi Hub",
        "date": "2026-10-03",
        "sample_size_expected": 20
    })
    assert reg_response.status_code == 201
    lot_data = reg_response.json()
    lot_id = lot_data["lot_id"]
    assert lot_id.startswith("ONN-2026-")

    # 2. Generate 10 synthetic sample images
    gen_response = client.post(f"/api/lots/{lot_id}/generate-sample-images?count=10")
    assert gen_response.status_code == 201
    images = gen_response.json()
    assert len(images) == 10

    # 3. Execute AI Analysis
    analyze_response = client.post(f"/api/lots/{lot_id}/analyze")
    assert analyze_response.status_code == 200
    report_data = analyze_response.json()

    assert report_data["lot_id"] == lot_id
    assert report_data["total_analyzed"] == 10
    assert 0 <= report_data["grade_a_pct"] <= 100
    assert "defect_breakdown" in report_data

    # 4. Fetch Report via GET endpoint
    get_rep_res = client.get(f"/api/lots/{lot_id}/report")
    assert get_rep_res.status_code == 200
    assert get_rep_res.json()["lot_id"] == lot_id
