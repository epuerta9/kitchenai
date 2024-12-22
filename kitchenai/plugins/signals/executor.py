from django.dispatch import Signal

# Background task execution signals
task_started = Signal()  # Fired when a background task starts
task_completed = Signal()  # Fired when a background task completes
task_failed = Signal()  # Fired when a background task fails
