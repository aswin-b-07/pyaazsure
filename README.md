# 🧅 PyaazSure

### **Smart Onion Quality Assessment & Grading System**
**SIH 2026 Prototype • Software Problem Statement Solution**

---

## 1. Project Overview
**PyaazSure** is an AI-powered lot-level onion quality grading and digital assessment system built for **Smart India Hackathon (SIH) 2026**.

In traditional onion procurement across Indian mandis and buffer stock depots (e.g., NAFED, NCCF), quality evaluation relies heavily on manual sampling and subjective visual inspection. This leads to inconsistency, disputes in price determination, delayed procurement workflows, and stock spoilage.

**PyaazSure** automates and standardizes onion quality assessment by combining sample image capture, AI-driven defect classification, a deterministic grading engine, transparent quality certification, and historical audit logging.

---

## 2. SIH Problem Statement
* **Domain:** Smart Agriculture, Post-Harvest Quality Control & Supply Chain Management.
* **Challenge:** Develop an AI-powered lot-level onion quality grading system to classify onions into procurement grades, calculate defect ratios, detect early spoilage, and flag low-confidence assessments for human verification.

---

## 3. PyaazSure Solution
PyaazSure introduces an end-to-end digital pipeline:
1. **Automated Lot Registration:** Generates unique sequential lot identifiers (e.g., `ONN-2026-00001`).
2. **Batch Image Capture:** Collects sample images representing the onion lot.
3. **Decoupled AI Inference Layer:** Predicts onion quality classes (`Healthy`, `Damaged`, `Rotten`, `Sprouted`, `Undersized`) and confidence scores.
4. **Independent Grading Engine:** Aggregates image predictions to compute **Grade A %**, **URS % (Under Size / Minor Defect)**, and **Defective %**.
5. **Human Review Rule:** Automatically flags lots with average AI confidence `< 80%` as `"Needs Human Review"`.
6. **Digital Quality Certificate:** Provides transparent metrics, visual chart analytics, defect counts, and a clear *"Why did this lot receive this assessment?"* narrative.

---

## 4. Key Features
* 🏷️ **Lot Registration & Auto ID:** Sequential lot ID generation (`ONN-2026-XXXXX`).
* 📷 **Batch Sample Capture:** Multi-image upload dropzone + 1-Click prototype synthetic batch generator (10/50/100 onions).
* 🤖 **Replaceable AI Inference Module:** Isolated `backend/ml/mock_inference.py` engine easily swappable with real YOLOv8 or CNN models.
* 📊 **Deterministic Grading Engine:** Decoupled business logic enforcing official procurement grading thresholds.
* 📄 **Digital Quality Report:** Interactive charts (Chart.js), defect breakdown tables, printable quality certificates, and narrative justifications.
* 📜 **Lot History & Audit Log:** Searchable dashboard archive with filtering by procurement centre, date, and review status.

---

## 5. System Architecture & Data Flow

```
┌────────────────────────┐
│    Lot Registration    │  (ONN-2026-XXXXX)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│   Batch Image Upload   │  (Sample Image Files)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│   Mock AI Inference    │  (backend/ml/mock_inference.py)
└───────────┬────────────┘
            │  Predictions & Confidence Scores
            ▼
┌────────────────────────┐
│     Grading Engine     │  (backend/services/grading.py)
└───────────┬────────────┘
            │  Grade A %, URS %, Defective %, Review Flag
            ▼
┌────────────────────────┐
│ Digital Quality Report │  (PDF/Printable Certificate + Charts)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  Lot History & Audit   │  (Searchable Archive DB)
└────────────────────────┘
```

---

## 6. Technology Stack
* **Backend Framework:** Python 3.12 + FastAPI (Async REST API)
* **Database & ORM:** SQLite + SQLAlchemy ORM
* **Data Validation:** Pydantic V2
* **Frontend Web App:** Vanilla HTML5, Modern CSS3 Design System, JavaScript (ES6+), Chart.js (CDNs)
* **Testing:** Pytest + TestClient / HTTPX

---

## 7. Project Structure

```
pyaazsure/
│
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI Application & Static File Mounting
│   ├── database.py             # SQLAlchemy Engine & SQLite Connection
│   ├── models.py               # ORM Database Models (Lot, Image, Report)
│   ├── schemas.py              # Pydantic Schemas for Validation
│   │
│   ├── api/                    # REST API Endpoint Controllers
│   │   ├── __init__.py
│   │   ├── lots.py             # Lot Registration & Retrieval
│   │   ├── images.py           # Image Upload & Synthetic Batch Generator
│   │   └── reports.py          # AI Analysis Execution & Reports
│   │
│   ├── services/               # Core Business Logic Services
│   │   ├── __init__.py
│   │   ├── grading.py          # Grading Engine (Grade A %, URS %, Defective %)
│   │   └── report_service.py   # Narrative Justification Generator
│   │
│   └── ml/                     # Machine Learning Layer (Decoupled)
│       ├── __init__.py
│       └── mock_inference.py   # MOCK AI Inference Module
│
├── frontend/                   # Responsive Web Dashboard
│   ├── index.html              # Executive Dashboard
│   ├── lot.html                # Lot Registration Form
│   ├── upload.html             # Sample Capture & AI Trigger Page
│   ├── report.html             # Digital Quality Report Certificate
│   ├── history.html            # Searchable Lot History Archive
│   │
│   ├── css/
│   │   └── style.css           # Modern CSS Design System
│   │
│   └── js/
│       ├── app.js              # Shared Utilities & Navbar State
│       ├── lot.js              # Lot Form Logic
│       ├── upload.js           # Upload & AI Simulation Controls
│       ├── report.js           # Chart.js Visualizations & Report Renderer
│       └── history.js          # Search & Filter Logic
│
├── uploads/                    # Local storage for uploaded sample images
├── tests/                      # Automated Test Suite
│   ├── __init__.py
│   ├── test_mock_inference.py  # Mock ML Isolation Tests
│   ├── test_grading.py         # Grading Rules & Threshold Tests
│   └── test_full_workflow.py   # Integration Pipeline Tests
│
├── README.md                   # Complete Documentation
├── requirements.txt            # Python Dependencies
└── .gitignore                  # Git Ignore Rules
```

---

## 8. Database Schema

### `LOTS` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Internal Database ID |
| `lot_id` | String | Unique, Indexed, Not Null | Formatted ID (`ONN-2026-00001`) |
| `centre_name` | String | Not Null | Procurement Centre Name |
| `date` | String | Not Null | Assessment Date (`YYYY-MM-DD`) |
| `sample_size_expected` | Integer | Default 100 | Target sample count |
| `status` | String | Default "Registered" | Status (`Registered`, `Images Uploaded`, `AI Assessment Complete`, `Needs Human Review`) |
| `created_at` | DateTime | Default UTC | Record creation timestamp |

### `IMAGES` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Internal Image ID |
| `image_id` | String | Unique, Indexed, Not Null | Unique identifier (`IMG-xxxxxxxx`) |
| `lot_id` | String | Foreign Key (`lots.lot_id`) | Associated Lot ID |
| `file_path` | String | Not Null | Relative path to image file |
| `predicted_class` | String | Nullable | Class (`Healthy`, `Damaged`, `Rotten`, `Sprouted`, `Undersized`) |
| `confidence` | Float | Nullable | Confidence Score (70.0% - 99.0%) |

### `REPORTS` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Internal Report ID |
| `lot_id` | String | Foreign Key (`lots.lot_id`), Unique | Associated Lot ID |
| `grade_a_pct` | Float | Default 0.0 | % Healthy Onions |
| `urs_pct` | Float | Default 0.0 | % Undersized Onions |
| `defective_pct` | Float | Default 0.0 | % Damaged + Rotten + Sprouted |
| `avg_confidence` | Float | Default 0.0 | Average AI Confidence Score |
| `needs_review` | Boolean | Default False | `True` if `avg_confidence < 80.0%` |
| `healthy_count` | Integer | Default 0 | Count of healthy onions |
| `damaged_count` | Integer | Default 0 | Count of damaged onions |
| `rotten_count` | Integer | Default 0 | Count of rotten onions |
| `sprouted_count` | Integer | Default 0 | Count of sprouted onions |
| `undersized_count` | Integer | Default 0 | Count of undersized onions |
| `total_analyzed` | Integer | Default 0 | Total onions analyzed |

---

## 9. API Endpoints

### Lots API
* `POST /api/lots` — Register a new onion lot (Auto-generates Lot ID).
* `GET /api/lots` — List all registered lots (Supports `search` and `status_filter`).
* `GET /api/lots/{lot_id}` — Get details for a specific lot.

### Images API
* `POST /api/lots/{lot_id}/images` — Upload multiple sample onion images.
* `POST /api/lots/{lot_id}/generate-sample-images` — Generate synthetic sample image batch (10, 50, 100 onions) for prototype testing.
* `GET /api/lots/{lot_id}/images` — List all sample images associated with a lot.

### Reports & Analysis API
* `POST /api/lots/{lot_id}/analyze` — Run mock AI inference on images, calculate lot grades, generate digital quality report.
* `GET /api/lots/{lot_id}/report` — Retrieve quality report for a specific lot.
* `GET /api/reports` — Retrieve all quality reports.
* `GET /api/stats` — Retrieve aggregated dashboard overview statistics.

---

## 10. How to Run Locally

### Prerequisites
* Python 3.10+ installed.

### Step 1: Clone & Setup Virtual Environment
```bash
# Clone repo
git clone https://github.com/your-org/pyaazsure.git
cd pyaazsure

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run FastAPI Application Server
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Access Web Application
Open your web browser and navigate to:
```
http://localhost:8000
```
* **Dashboard:** `http://localhost:8000/index.html`
* **Swagger API Docs:** `http://localhost:8000/docs`

### Step 5: Run Automated Tests
```bash
pytest
```

---

## 11. How Mock AI Works
The file `backend/ml/mock_inference.py` contains the function `mock_inference(image_path: str)`:
* It randomly assigns each uploaded image one status:
  - `Healthy`
  - `Damaged`
  - `Rotten`
  - `Sprouted`
  - `Undersized`
* It assigns a random confidence score between **70.0%** and **99.0%**.
* It returns the prediction object: `{"predicted_class": "Healthy", "confidence": 91.50}`.

This function is explicitly isolated so that inference logic remains independent of API controllers and database models.

---

## 12. How to Replace Mock AI with a Real ML Model
To integrate a trained computer vision model (e.g., YOLOv8, ResNet-50, or custom CNN):

1. Open `backend/ml/mock_inference.py` (or create `backend/ml/yolo_inference.py`).
2. Maintain the signature: `mock_inference(image_path: str) -> dict`.
3. Replace the random prediction logic with model inference:
```python
import torch
from PIL import Image

# Load trained YOLOv8 / PyTorch model
MODEL = torch.load("path/to/onion_yolo_model.pt")

def mock_inference(image_path: str) -> dict:
    img = Image.open(image_path)
    results = MODEL(img)
    
    predicted_class = results.names[results.probs.top1] # e.g. 'Healthy'
    confidence = float(results.probs.top1conf) * 100.0   # e.g. 94.2
    
    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 2)
    }
```
4. **No changes** to `api/reports.py`, `services/grading.py`, `database.py`, or the frontend are required!

---

## 13. Current Limitations

1. **Simulated Predictions for Workflow Demonstration:** AI inference in `backend/ml/mock_inference.py` currently uses simulated/mock predictions (random class assignment + confidence score) to demonstrate the complete end-to-end software pipeline, automated grading logic, database persistence, and visual reporting interface.
2. **Model Training in Progress:** Real machine learning model training is actively in progress using publicly sourced onion image datasets:
   * **Zenodo Onion Bulb Dataset**
   * **Hugging Face Onion Classification Dataset**
   * **Good Onion Dataset - Harvard Dataverse**
3. **Decoupled Architecture Design:** The software architecture is explicitly designed so `backend/ml/mock_inference.py` can be swapped with a fully trained model (e.g., YOLOv8 / CNN) without modifying any REST API endpoints, database models, grading rules, or frontend components.
4. **RGB Surface-Level Vision:** Standard RGB cameras detect external defects (sprouting, rot, surface damage, size); internal rot detection requires future optical sensor integration.

---

## 14. Roadmap

The following roadmap features are planned for upcoming development phases:

* 🤖 **Real Model Integration:** Swapping `mock_inference.py` with trained YOLOv8 / CNN deep learning models trained on public datasets (Zenodo, Hugging Face, Harvard Dataverse) and custom mandi samples.
* 🧅 **Multi-Onion Object Detection:** Implementing object detection to segment, bound, and independently grade multiple onions captured in a single photo.
* 📐 **OpenCV-Based Size Estimation:** Automated pixel-to-millimeter spatial calibration using OpenCV contour measurement for precise `Undersized` classification.
* 📱 **QR-Based Digital Lot Records:** Generating printable, secure QR code lot passports attached to procurement bags for instant verification of digital quality certificates across mandis and storage depots.
* 💡 **Explainable AI (XAI):** Integrating Grad-CAM heatmaps to visually highlight defect regions for inspector confidence.
* 🔬 **NIR Internal Sensing:** Exploring Near-Infrared optical sensors for non-destructive internal rot detection.

---

## License
Developed for **Smart India Hackathon (SIH) 2026**. Prototype implementation.
