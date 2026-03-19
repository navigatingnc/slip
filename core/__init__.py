"""SLIP core package — friction detection engine."""

from .detector import detect
from .models import FrictionPoint

__all__ = ["detect", "FrictionPoint"]
