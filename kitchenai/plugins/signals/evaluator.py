from django.dispatch import Signal


# Context evaluation signals
context_retrieved = Signal()  # When context is fetched from vector store
context_filtered = Signal()  # After context processing/filtering
context_injected = Signal()  # When context is prepared for LLM prompt

# Response evaluation signals
response_received = Signal()  # Raw LLM response received
response_processed = Signal()  # After response processing/formatting
response_delivered = Signal()  # When response is sent to user

# Metrics and analytics signals
latency_recorded = Signal()  # Performance timing data
token_usage_recorded = Signal()  # Token consumption metrics
quality_metrics_recorded = Signal()  # Response quality measurements

# Dataset and ground truth signals
ground_truth_compared = Signal()  # When response is compared to expected output
dataset_recorded = Signal()  # When interaction is saved to evaluation dataset
evaluation_metrics_updated = Signal()  # When evaluation scores are updated
evaluation_completed = Signal()  # When evaluation is completed
