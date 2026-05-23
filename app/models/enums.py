from enum import Enum


class TaskStatus(str, Enum):

    PENDING = "pending"

    IN_PROGRESS = "in_progress"

    PROCESSING_COMPLETION = "processing_completion"

    COMPLETED = "completed"

    CANCELLED = "cancelled"