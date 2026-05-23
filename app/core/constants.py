from app.models.enums import TaskStatus


ALLOWED_STATUS_TRANSITIONS = {

    TaskStatus.PENDING: [
        TaskStatus.IN_PROGRESS,
        TaskStatus.CANCELLED
    ],

    TaskStatus.IN_PROGRESS: [
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED
    ],

    TaskStatus.COMPLETED: [],

    TaskStatus.CANCELLED: []
}

def validate_status_transition(
    current_status: TaskStatus,
    new_status: TaskStatus
):

    allowed = ALLOWED_STATE_TRANSITIONS


    return new_status in allowed
