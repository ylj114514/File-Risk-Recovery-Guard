"""Dataclasses used by the file guard engine."""

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class FileSnapshot:
    """Immutable-like snapshot of a protected file at scan time."""

    relative_path: str
    absolute_path: str
    file_name: str
    extension: str
    size: int
    mtime: float
    sha256: str
    sensitivity: str

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class RiskEvent:
    """Risk event generated from a detected file change."""

    event_type: str
    relative_path: str
    old_hash: Optional[str]
    new_hash: Optional[str]
    old_size: Optional[int]
    new_size: Optional[int]
    score: int
    level: str
    evidence: str
    suggestion: str
    detected_at: str

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary."""
        return asdict(self)
