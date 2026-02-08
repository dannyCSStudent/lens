# apps/api/app/core/enums.py

from enum import Enum

class PostType(str, Enum):
    expression = "expression"
    claim = "claim"
    investigation = "investigation"

class EvidenceDirection(str, Enum):
    supports = "supports"
    contradicts = "contradicts"

class ContentStatus(str, Enum):
    active = "active"
    locked = "locked"
    removed_illegal = "removed_illegal"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
