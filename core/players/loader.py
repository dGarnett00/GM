from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


@dataclass
class PlayerRating:
    season: Optional[int] = None
    hgt: Optional[int] = None
    stre: Optional[int] = None
    spd: Optional[int] = None
    jmp: Optional[int] = None
    endu: Optional[int] = None
    ins: Optional[int] = None
    dnk: Optional[int] = None
    ft: Optional[int] = None
    fg: Optional[int] = None
    tp: Optional[int] = None
    diq: Optional[int] = None
    oiq: Optional[int] = None
    drb: Optional[int] = None
    pss: Optional[int] = None
    reb: Optional[int] = None


@dataclass
class Player:
    tid: Optional[int]
    name: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    pos: Optional[str] = None
    hgt: Optional[int] = None
    weight: Optional[int] = None
    born: Optional[Dict[str, Any]] = None
    contract: Optional[Dict[str, Any]] = None
    draft: Optional[Dict[str, Any]] = None
    college: Optional[str] = None
    imgURL: Optional[str] = None
    srID: Optional[str] = None
    injury: Optional[Dict[str, Any]] = None
    awards: Optional[List[Dict[str, Any]]] = None
    relatives: Optional[List[Dict[str, Any]]] = None
    transactions: Optional[List[Dict[str, Any]]] = None
    stats: Optional[List[Dict[str, Any]]] = None
    ratings: List[PlayerRating] = field(default_factory=list)


def _default_players_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "players.json"


def _normalize_player(obj: Dict[str, Any]) -> Player:
    # Determine name fields
    first = obj.get("firstName")
    last = obj.get("lastName")
    combined = obj.get("name")
    if combined and not (first or last):
        # Split if possible, else keep whole string as name
        parts = str(combined).split()
        if len(parts) >= 2:
            first, last = parts[0], " ".join(parts[1:])
        else:
            first, last = None, None
        display_name = str(combined)
    else:
        # Build display name from first/last if available
        if first or last:
            display_name = " ".join([p for p in [first, last] if p])
        else:
            display_name = obj.get("name") or "Unknown"

    # Ratings list: convert dicts in either format to PlayerRating objects
    ratings_raw = obj.get("ratings", []) or []
    ratings: List[PlayerRating] = []
    for r in ratings_raw:
        if not isinstance(r, dict):
            continue
        ratings.append(PlayerRating(**{k: r.get(k) for k in PlayerRating.__dataclass_fields__.keys()}))

    return Player(
        tid=obj.get("tid"),
        name=display_name,
        firstName=first,
        lastName=last,
        pos=obj.get("pos"),
        hgt=obj.get("hgt"),
        weight=obj.get("weight"),
        born=obj.get("born"),
        contract=obj.get("contract"),
        draft=obj.get("draft"),
        college=obj.get("college"),
        imgURL=obj.get("imgURL"),
        srID=obj.get("srID"),
        injury=obj.get("injury"),
        awards=obj.get("awards"),
        relatives=obj.get("relatives"),
        transactions=obj.get("transactions"),
        stats=obj.get("stats"),
    ratings=ratings,
    )


def _dedupe_players(players: List[Player]) -> List[Player]:
    # Key by strong identifiers in order: srID, (first+last), display name
    seen: Dict[str, Player] = {}
    def key_for(p: Player) -> Optional[str]:
        if p.srID:
            return f"sr:{p.srID}"
        if p.firstName or p.lastName:
            return f"fl:{(p.firstName or '').strip().lower()}|{(p.lastName or '').strip().lower()}"
        if p.name:
            return f"nm:{p.name.strip().lower()}"
        return None
    result: List[Player] = []
    for p in players:
        k = key_for(p)
        if k is None:
            result.append(p)
            continue
        if k in seen:
            # Merge: prefer non-null fields; extend ratings/stats/awards/transactions
            base = seen[k]
            for field_name in ("tid","pos","hgt","weight","born","contract","draft","college","imgURL","injury"):
                if getattr(base, field_name) in (None, [], {}):
                    setattr(base, field_name, getattr(p, field_name))
            if not base.srID and p.srID:
                base.srID = p.srID
            # Merge arrays
            for arr_name in ("awards","relatives","transactions","stats"):
                a = getattr(base, arr_name)
                b = getattr(p, arr_name)
                if b:
                    if a:
                        a.extend(b)
                    else:
                        setattr(base, arr_name, list(b))
            # Merge ratings by season when season present; otherwise append
            existing_by_season: Dict[Optional[int], PlayerRating] = {r.season: r for r in base.ratings}
            for r in p.ratings:
                if r.season in existing_by_season and r.season is not None:
                    # Prefer higher non-null values
                    target = existing_by_season[r.season]
                    for attr in PlayerRating.__dataclass_fields__.keys():
                        v_cur = getattr(target, attr)
                        v_new = getattr(r, attr)
                        if v_cur is None and v_new is not None:
                            setattr(target, attr, v_new)
                        elif isinstance(v_cur, int) and isinstance(v_new, int):
                            setattr(target, attr, max(v_cur, v_new))
                else:
                    base.ratings.append(r)
        else:
            seen[k] = p
            result.append(p)
    return result


def load_players(path: Path | None = None) -> List[Player]:
    """Load players from canonical data file.

    Supports either a single object with top-level fields (version, startingSeason, players)
    or a bare {"players": [...]} structure. Normalizes and de-duplicates entries.
    """
    p = Path(path) if path else _default_players_path()
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # Accept either list or dict with players key
    raw_players: List[Dict[str, Any]]
    if isinstance(data, dict) and isinstance(data.get("players"), list):
        raw_players = data["players"]
    elif isinstance(data, list):
        raw_players = data
    else:
        return []

    normalized = [_normalize_player(obj) for obj in raw_players if isinstance(obj, dict)]
    return _dedupe_players(normalized)
