from django.dispatch import Signal

# Response evaluation signals
response_evaluate = Signal()
bias_detect = Signal()
performance_monitor = Signal()
evaluation_framework_triggered = Signal()
