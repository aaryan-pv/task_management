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