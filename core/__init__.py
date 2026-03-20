"""SLIP core package — friction detection engine."""

from .detector import detect
from .models import FrictionPoint, Opportunity
from .scorer import score

__all__ = ["detect", "FrictionPoint", "Opportunity", "score"]
