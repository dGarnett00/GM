from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import json
import logging


def _default_rosters_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "rosters" / "rosters.json"


def _get_fallback_roster(team_name: str) -> List[str]:
    """Generate a fallback roster for a team."""
    return [f"{team_name} Player {i+1}" for i in range(12)]


def load_rosters(path: Path | None = None) -> Dict[str, List[str]]:
    """Load team rosters from JSON file with comprehensive error handling."""
    logger = logging.getLogger('basketball_gm')
    p = Path(path) if path else _default_rosters_path()
    
    if not p.exists():
        logger.warning(f"Rosters file not found at {p}, returning empty rosters")
        return {}
    
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            logger.error(f"Rosters file {p} should contain a dictionary, got {type(data)}")
            return {}
        
        # Validate and clean roster data
        rosters = {}
        for team_name, roster in data.items():
            if not isinstance(team_name, str) or not team_name.strip():
                logger.warning(f"Invalid team name in rosters: {team_name}")
                continue
                
            if not isinstance(roster, list):
                logger.warning(f"Roster for {team_name} should be a list, got {type(roster)}")
                continue
            
            # Clean and validate roster entries
            clean_roster = []
            for player in roster:
                if isinstance(player, (str, int)) and str(player).strip():
                    clean_roster.append(str(player).strip())
                else:
                    logger.warning(f"Invalid player entry in {team_name} roster: {player}")
            
            if clean_roster:
                rosters[team_name.strip()] = clean_roster
            else:
                logger.warning(f"No valid players found for team {team_name}")
        
        logger.info(f"Successfully loaded rosters for {len(rosters)} teams from {p}")
        return rosters
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in rosters file {p}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading rosters from {p}: {e}")
        return {}


def get_team_roster(team_display_name: str, rosters: Dict[str, List[str]] | None = None) -> List[str]:
    """Get roster for a team with fallback generation."""
    logger = logging.getLogger('basketball_gm')
    
    if not team_display_name or not team_display_name.strip():
        logger.warning("Empty team name provided for roster lookup")
        return []
    
    if rosters is None:
        rosters = load_rosters()
    
    # Try exact match first
    roster = rosters.get(team_display_name.strip())
    if roster:
        return [str(x) for x in roster if isinstance(x, (str, int))]
    
    # Try case-insensitive match
    team_lower = team_display_name.strip().lower()
    for team_name, team_roster in rosters.items():
        if team_name.lower() == team_lower:
            return [str(x) for x in team_roster if isinstance(x, (str, int))]
    
    # Generate fallback roster
    logger.info(f"No roster found for {team_display_name}, generating fallback")
    return _get_fallback_roster(team_display_name.strip())
