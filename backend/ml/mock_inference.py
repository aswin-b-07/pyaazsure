"""
=============================================================================
PYAAZSURE ML INFERENCE MODULE - MOCK IMPLEMENTATION
=============================================================================
WARNING / NOTICE:
This module contains MOCK AI INFERENCE logic for prototyping and SIH 2026
demonstration purposes.

The current implementation randomly generates onion quality predictions and
confidence scores. It DOES NOT execute a trained deep learning model.

MODULARITY & REPLACABILITY:
To replace this mock logic with a real computer vision model (e.g., YOLOv8,
ResNet, EfficientNet, or custom CNN trained on onion defect datasets):

1. Keep the function signature `mock_inference(image_path: str) -> dict`.
2. Replace the random selection logic inside `mock_inference()` with your model:
   - Load image from `image_path` (using OpenCV or Pillow).
   - Perform preprocessing & tensor transformation.
   - Run inference: `model(image_tensor)`.
   - Map output logits to class labels: ['Healthy', 'Damaged', 'Rotten', 'Sprouted', 'Undersized'].
   - Extract prediction class and confidence percentage (70.0 to 100.0).
3. The rest of the application (APIs, Database, Grading Engine, Frontend, Reports)
   will continue to function seamlessly without any modifications.
=============================================================================
"""

import random
import time
from typing import Dict, List, Any

# Valid onion quality prediction classes
CLASSES = [
    "Healthy",     # Grade A candidate
    "Damaged",     # Defective (cuts, bruises, mechanical damage)
    "Rotten",      # Defective (fungal/bacterial decay)
    "Sprouted",    # Defective (premature germination)
    "Undersized"   # Under Size / Minor Defect (URS)
]

# Realistic class probability distribution for simulation
# Mostly healthy, with some defective/undersized samples
CLASS_WEIGHTS = [0.65, 0.10, 0.08, 0.07, 0.10]


def mock_inference(image_path: str) -> Dict[str, Any]:
    """
    Simulates AI model inference on a single onion image.

    Args:
        image_path (str): File system path to the onion image.

    Returns:
        dict: {
            "predicted_class": str, # e.g. "Healthy"
            "confidence": float     # e.g. 91.5 (percentage score 70.0 - 99.0%)
        }
    """
    # Simulate slight processing delay for realistic UX (optional small sleep)
    # time.sleep(0.01)

    # Randomly select a class based on weighted distribution
    predicted_class = random.choices(CLASSES, weights=CLASS_WEIGHTS, k=1)[0]

    # Generate random confidence score between 70.0% and 99.0%
    confidence = round(random.uniform(70.0, 99.0), 2)

    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "is_mock": True
    }


def mock_inference_batch(image_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Simulates batch inference over multiple onion images.

    Args:
        image_paths (list[str]): List of image file paths.

    Returns:
        list[dict]: List of prediction dictionaries.
    """
    results = []
    for path in image_paths:
        prediction = mock_inference(path)
        results.append(prediction)
    return results
