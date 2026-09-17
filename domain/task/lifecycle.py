from enum import Enum

class TaskLifecycle(str, Enum):
    ACTIVE = 'active'
    PAUSED = "paused"
    CLOSED = "closed"
