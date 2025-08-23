from dataclasses import dataclass
from pathlib import Path
import json
import logging
from typing import List, Optional


@dataclass
class Team:
    # Display name used throughout the app (kept for backward compatibility)
    name: str

    # Rich metadata (optional)
    tid: Optional[int] = None
    cid: Optional[int] = None  # 0 = East, 1 = West
    did: Optional[int] = None  # 0..5 divisions
    region: Optional[str] = None
    abbrev: Optional[str] = None
    pop: Optional[float] = None  # in millions
    stadiumCapacity: Optional[int] = None


def _default_teams_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "teams.json"


def _get_fallback_teams() -> List[Team]:
    """Return a fallback list of teams if data file is unavailable."""
    return [Team(name=n) for n in [
        "Lakers", "Warriors", "Celtics", "Bulls", "Heat", "Suns",
        "Knicks", "Nets", "Sixers", "Raptors", "Magic", "Hawks"
    ]]


def load_teams(path: Path | None = None) -> List[Team]:
    """Load teams from JSON file with comprehensive error handling."""
    logger = logging.getLogger('basketball_gm')
    p = Path(path) if path else _default_teams_path()
    
    # Check if file exists
    if not p.exists():
        logger.warning(f"Teams file not found at {p}, using fallback teams")
        return _get_fallback_teams()
    
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            logger.error(f"Teams file {p} should contain a list, got {type(data)}")
            return _get_fallback_teams()
            
        teams = []
        for i, item in enumerate(data):
            try:
                if isinstance(item, dict):
                    # Prefer region+name if provided, else "name" as-is
                    region = item.get("region")
                    base_name = item.get("name")
                    
                    if not base_name:
                        logger.warning(f"Team at index {i} missing name field, skipping")
                        continue
                        
                    display_name = (f"{region} {base_name}".strip()) if region and base_name else base_name
                    
                    # Validate numeric fields
                    def safe_int(value, field_name):
                        if value is None:
                            return None
                        try:
                            return int(value)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid {field_name} for team {display_name}: {value}")
                            return None
                    
                    def safe_float(value, field_name):
                        if value is None:
                            return None
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid {field_name} for team {display_name}: {value}")
                            return None
                    
                    teams.append(
                        Team(
                            name=display_name,
                            tid=safe_int(item.get("tid"), "tid"),
                            cid=safe_int(item.get("cid"), "cid"),
                            did=safe_int(item.get("did"), "did"),
                            region=region,
                            abbrev=item.get("abbrev"),
                            pop=safe_float(item.get("pop"), "pop"),
                            stadiumCapacity=safe_int(item.get("stadiumCapacity"), "stadiumCapacity"),
                        )
                    )
                elif isinstance(item, str) and item.strip():
                    teams.append(Team(name=item.strip()))
                else:
                    # Try to convert to string as fallback
                    name = str(item).strip()
                    if name:
                        teams.append(Team(name=name))
                        
            except Exception as e:
                logger.warning(f"Error processing team at index {i}: {e}")
                continue
        
        if not teams:
            logger.warning("No valid teams found in file, using fallback")
            return _get_fallback_teams()
            
        logger.info(f"Successfully loaded {len(teams)} teams from {p}")
        return teams
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in teams file {p}: {e}")
        return _get_fallback_teams()
    except Exception as e:
        logger.error(f"Error loading teams from {p}: {e}")
        return _get_fallback_teams()
