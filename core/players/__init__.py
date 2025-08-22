"""Players package: data models and loaders for player-related functionality.

Exports:
- load_players: Load normalized Player objects from canonical data.
- Player, PlayerRating: Dataclasses representing players and their ratings.
"""

from .loader import load_players, Player, PlayerRating

__all__ = ["load_players", "Player", "PlayerRating"]
