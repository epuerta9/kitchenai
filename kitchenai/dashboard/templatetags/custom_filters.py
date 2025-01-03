from django import template
import json
import logging
import markdown2

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def contains(value, substring):
    """Check if a string contains a given substring."""
    return substring in value


@register.filter(name='get_range')
def get_range(value):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):
    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>
    """
    return range(1, int(value) + 1)


@register.filter(name='format_deepeval_logs')
def format_logs(log_text):
    try:
        if not log_text:
            logger.warning("Empty log_text received")
            return ""
            
        logger.debug(f"Processing log_text: {log_text}")
        
        # Split into sections
        sections = log_text.split('\n \n')
        formatted_sections = []
        
        for section in sections:
            try:
                if section.startswith('Statements:'):
                    # Parse statements array
                    json_str = section.replace('Statements:', '').strip()
                    logger.debug(f"Parsing statements JSON: {json_str}")
                    statements = json.loads(json_str)
                    formatted_statements = ['• ' + stmt for stmt in statements]
                    formatted_sections.append('Statements:\n' + '\n'.join(formatted_statements))
                
                elif section.startswith('Verdicts:'):
                    # Parse verdicts array
                    json_str = section.replace('Verdicts:', '').strip()
                    logger.debug(f"Parsing verdicts JSON: {json_str}")
                    verdicts = json.loads(json_str)
                    formatted_verdicts = []
                    for i, v in enumerate(verdicts):
                        verdict = '✓' if v['verdict'].lower() == 'yes' else '✗'
                        reason = f" - {v['reason']}" if v['reason'] else ''
                        formatted_verdicts.append(f'{verdict} Verdict {i+1}{reason}')
                    formatted_sections.append('Verdicts:\n' + '\n'.join(formatted_verdicts))
                
                else:
                    formatted_sections.append(section)
            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error in section: {section}")
                logger.error(f"JSON error details: {str(je)}")
                formatted_sections.append(section)
            except Exception as e:
                logger.error(f"Error processing section: {section}")
                logger.error(f"Error details: {str(e)}")
                formatted_sections.append(section)
        
        result = '\n\n'.join(formatted_sections)
        logger.debug(f"Formatted result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Top-level error in format_deepeval_logs: {str(e)}")
        logger.error(f"Input was: {log_text}")
        return str(log_text)  # Return the original text if formatting fails
    






@register.filter(name='markdown')
def markdown_format(text):
    return markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'break-on-newline'])