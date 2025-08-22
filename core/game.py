"""Compatibility shim exposing game and boxscore APIs under core.game."""

from .game.sim import simulate_game, generate_summary
from .boxscore.generate import generate_boxscore

__all__ = ["simulate_game", "generate_summary", "generate_boxscore"]
