from django.dispatch import Signal

# Generator Taxonomy Signals
# These signals are used for plugins that generate new content based on input data

# Fired to generate new content like summaries or explanations
content_generate = Signal()

# Fired to generate vector embeddings for input data
embedding_generate = Signal()

# Fired to generate templates or structured content
template_generate = Signal()
