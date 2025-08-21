"""Backward-compat shim: old path simulation.game now forwards to core.game"""
from core import game as _game

# Re-export for legacy imports
simulate_game = _game.simulate_game
generate_summary = _game.generate_summary

__all__ = ["simulate_game", "generate_summary"]
