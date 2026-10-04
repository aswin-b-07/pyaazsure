"""
=============================================================================
PYAAZSURE REPORT SERVICE
=============================================================================
Service layer responsible for generating transparent, human-readable quality
reports and narrative explanations for assessed onion lots.
=============================================================================
"""

from typing import Dict, Any


def generate_report_explanation(report_data: Dict[str, Any]) -> str:
    """
    Generates a clear explanation answering: 'Why did this lot receive this assessment?'

    Args:
        report_data (dict): Contains grading metrics and defect counts.

    Returns:
        str: Multi-line plain text / markdown structured explanation.
    """
    grade_a = report_data.get("grade_a_pct", 0.0)
    urs = report_data.get("urs_pct", 0.0)
    defective = report_data.get("defective_pct", 0.0)

    healthy = report_data.get("healthy_count", 0)
    undersized = report_data.get("undersized_count", 0)
    damaged = report_data.get("damaged_count", 0)
    rotten = report_data.get("rotten_count", 0)
    sprouted = report_data.get("sprouted_count", 0)
    total = report_data.get("total_analyzed", 0)

    avg_conf = report_data.get("avg_confidence", 0.0)
    status = report_data.get("status", "AI Assessment Complete")

    explanation = (
        f"This lot (Total Analyzed: {total} onions) was graded with {grade_a}% Grade A (Premium Quality), "
        f"{urs}% Under Size (URS), and {defective}% Defective onions.\n\n"
        f"Defect Breakdown:\n"
        f"- Healthy: {healthy} sample(s)\n"
        f"- Undersized: {undersized} sample(s)\n"
        f"- Damaged: {damaged} sample(s)\n"
        f"- Rotten: {rotten} sample(s)\n"
        f"- Sprouted: {sprouted} sample(s)\n\n"
        f"Average AI Confidence across all images was {avg_conf}%.\n"
    )

    if report_data.get("needs_review", False):
        explanation += (
            "Flagged for Human Review: Average AI confidence is below the required 80.0% threshold. "
            "A manual inspector must verify this assessment before final procurement payout."
        )
    else:
        explanation += (
            "Status: AI Assessment Complete. Confidence threshold (>80%) satisfied."
        )

    return explanation
