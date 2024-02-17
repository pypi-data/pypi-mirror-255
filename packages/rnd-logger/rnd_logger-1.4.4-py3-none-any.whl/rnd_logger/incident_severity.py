import enum
from enum import auto


class IncidentSeverity(enum.Enum):
    NONE = auto()
    MINOR = auto()
    MAJOR = auto()
    CRITICAL = auto()
