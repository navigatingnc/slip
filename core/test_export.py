"""Tests for the export module."""
import os
import csv
from .models import FrictionPoint, Opportunity
from .report import SlipReport
from .export import export_opportunities

def test_export_opportunities(tmp_path):
    # Setup mock data
    fp = FrictionPoint(description="test", pattern="delay", score=0.8)
    opp = Opportunity(
        title="delay reduction opportunity",
        friction_points=[fp],
        frequency=1.0,
        severity=0.8,
        automation_potential=0.8,
        composite_score=0.87
    )
    report = SlipReport(
        signal_count=1,
        friction_count=1,
        opportunities=[opp],
        top_pattern="delay",
        top_opportunity="delay reduction opportunity"
    )
    
    filepath = tmp_path / "test_export.csv"
    export_opportunities(report, str(filepath))
    
    assert filepath.exists()
    
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Check header
        assert rows[0] == [
            "Title", "Composite Score", "Severity", "Frequency", 
            "Automation Potential", "Signal Count"
        ]
        
        # Check data
        assert rows[1] == [
            "delay reduction opportunity", "0.87", "0.8", "1.0", "0.8", "1"
        ]
