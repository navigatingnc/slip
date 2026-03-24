"""CSV exporter for SLIP — Phase 10.
Exports the ranked Opportunities from a SlipReport to a CSV file.
"""
import csv
from typing import List
from .report import SlipReport

def export_opportunities(report: SlipReport, filepath: str) -> None:
    """
    Export the opportunities from a SlipReport to a CSV file.
    Args:
        report: The SlipReport containing opportunities to export.
        filepath: The path to the output CSV file.
    """
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Title",
            "Composite Score",
            "Severity",
            "Frequency",
            "Automation Potential",
            "Signal Count"
        ])
        for opp in report.opportunities:
            writer.writerow([
                opp.title,
                opp.composite_score,
                opp.severity,
                opp.frequency,
                opp.automation_potential,
                len(opp.friction_points)
            ])
