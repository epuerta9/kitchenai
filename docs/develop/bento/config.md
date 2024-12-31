# Bento Configuration Schema

## Overview
Every bento package in KitchenAI requires a configuration that defines its core properties. This document outlines the schema and validation rules for bento configurations.

## Schema Definition

### Required Fields

| Field | Type | Description | Pattern |
|-------|------|-------------|---------|
| `name` | string | The name identifier of the bento package | `^[a-zA-Z0-9_-]+$` |
| `description` | string | A brief description of the bento package's purpose | - |
| `namespace` | string | The namespace used for URL routing | `^[a-zA-Z0-9_-]+$` |
| `home` | string | The home route identifier | `^[a-zA-Z0-9_-]+$` |
| `tags` | array[string] | List of tags associated with the package | Each tag: `^[a-zA-Z0-9_-]+$` |

### Example Configuration
```json
{
    "name": "kitchenai_rag_simple_bento",
    "description": "a simple RAG starter that covers majority of cases",
    "namespace": "simple_rag",
    "home": "home",
    "tags": ["rag-simple", "bento", "kitchenai_rag_simple_bento"]
}
```

## Validation Rules

- **Name**: Must contain only alphanumeric characters, underscores, or hyphens
- **Namespace**: Must contain only alphanumeric characters, underscores, or hyphens
- **Home**: Must contain only alphanumeric characters, underscores, or hyphens
- **Tags**: 
  - Must have at least one tag
  - Each tag must contain only alphanumeric characters, underscores, or hyphens
  - No duplicate tags allowed

## Using the Configuration

```python
from kitchenai.core.schema.base import validate_bento_config

# Your bento configuration
config = {
    "name": "my_bento",
    "description": "My awesome bento package",
    "namespace": "my-namespace",
    "home": "home",
    "tags": ["my-tag", "bento"]
}

# Validate the configuration
validate_bento_config(config)
```

## Error Handling

The validation will raise `ValidationError` with descriptive messages for any configuration issues:

- Missing required fields
- Invalid characters in name, namespace, or home
- Empty tags list
- Invalid tag format
- Duplicate tags

## Best Practices

1. Use descriptive names that reflect the bento's purpose
2. Keep namespaces short but meaningful
3. Include relevant tags for discoverability
4. Provide clear, concise descriptions
5. Use lowercase with hyphens for better readability

## Related Documentation
- [Bento Development Guide](./development.md)
- [Configuration Examples](./examples.md) 