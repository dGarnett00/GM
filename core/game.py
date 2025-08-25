"""Compatibility shim for boxscore API under core.game (simulation removed)."""

from .boxscore.generate import generate_boxscore

__all__ = ["generate_boxscore"]
