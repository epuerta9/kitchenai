from django.dispatch import Signal

# Define a project-wide signal


prompt_preprocess = Signal()


query_preprocess = Signal()
query_postprocess = Signal()