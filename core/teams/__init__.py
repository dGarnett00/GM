"""Teams package: data models, loaders, and roster helpers."""

from .loader import load_teams, Team
from .rosters import load_rosters, get_team_roster

__all__ = ["load_teams", "Team", "load_rosters", "get_team_roster"]
