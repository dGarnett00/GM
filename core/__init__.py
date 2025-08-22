"""Core domain logic for the Basketball GM app."""

from .game import simulate_game, generate_summary, generate_boxscore

__all__ = ["simulate_game", "generate_summary", "generate_boxscore"]
