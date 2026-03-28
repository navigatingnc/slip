"""SLIP core package — friction detection engine."""

from .detector import detect
from .models import FrictionPoint, Opportunity
from .scorer import score
from .ingestion import Signal, normalise, ingest
from .persistence import save_report, load_reports, load_report_by_id
from .report import SlipReport, generate_report
from .ideation import generate_concepts, BusinessConcept

__all__ = [
    "detect",
    "FrictionPoint",
    "Opportunity",
    "score",
    "Signal",
    "normalise",
    "ingest",
    "SlipReport",
    "generate_report",
    "save_report",
    "load_reports",
    "load_report_by_id",
    "generate_concepts",
    "BusinessConcept",
]
