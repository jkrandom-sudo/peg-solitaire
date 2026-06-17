"""Persistent leaderboard (top 10)."""
import json
import time
from pathlib import Path
from typing import List, Optional


DEFAULT_PATH = Path.home() / ".pegsolitaire_scores.json"
MAX_ENTRIES = 10


def load(path: Optional[Path] = None) -> List[dict]:
    if path is None:
        path = DEFAULT_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return []


def save(scores: List[dict], path: Optional[Path] = None) -> None:
    if path is None:
        path = DEFAULT_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def add(name: str, score: int, variant: str, pegs_left: int, path: Optional[Path] = None) -> List[dict]:
    scores = load(path)
    scores.append({
        "name": name[:12] if name else "anon",
        "score": int(score),
        "variant": variant,
        "pegs": int(pegs_left),
        "time": int(time.time()),
    })
    scores.sort(key=lambda e: (-int(e.get("score", 0)), int(e.get("time", 0))))
    scores = scores[:MAX_ENTRIES]
    save(scores, path)
    return scores


def compute_score(pegs_left: int, perfect: bool, variant: str) -> int:
    """Score = base − pegs_left × 30 + perfect bonus + variant bonus.

    Fewer pegs left is better. Perfect (last peg in centre) earns +200.
    """
    if pegs_left < 1:
        return 0
    base = 1000
    penalty = (pegs_left - 1) * 30
    bonus = 200 if perfect else 0
    variant_bonus = {"english": 0, "european": 50}.get(variant, 0)
    return max(0, base - penalty + bonus + variant_bonus)
