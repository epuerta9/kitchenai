from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)    

def is_enabled():
    return settings.DEEPEVAL_PLUGIN["is_enabled"]

def format_deepeval_logs(log_text):
    try:
        if not log_text:
            return ""
        
        # Try to parse the entire string as JSON first
        try:
            data = json.loads(log_text)
            # If it's already JSON, format it nicely
            if isinstance(data, dict):
                formatted_sections = []
                for key, value in data.items():
                    formatted_sections.append(f"{key}:")
                    if isinstance(value, list):
                        formatted_sections.extend([f"  • {item}" for item in value])
                    else:
                        formatted_sections.append(f"  {value}")
                return "\n".join(formatted_sections)
        except json.JSONDecodeError:
            pass

        # If not JSON, try our original formatting
        # Clean up the input string first
        log_text = log_text.replace('\n[', '[').replace('\n]', ']')
        sections = log_text.split('\n\n')
        formatted_sections = []
        
        for section in sections:
            if 'Statements:' in section:
                try:
                    # Extract the JSON array part
                    json_str = section[section.find('['):section.rfind(']')+1]
                    statements = json.loads(json_str)
                    formatted_sections.append('Statements:')
                    formatted_sections.extend([f"  • {stmt}" for stmt in statements])
                except:
                    formatted_sections.append(section)
            
            elif 'Verdicts:' in section:
                try:
                    json_str = section[section.find('['):section.rfind(']')+1]
                    verdicts = json.loads(json_str)
                    formatted_sections.append('Verdicts:')
                    for i, v in enumerate(verdicts, 1):
                        verdict = '✓' if v.get('verdict', '').lower() == 'yes' else '✗'
                        reason = f" - {v.get('reason')}" if v.get('reason') else ''
                        formatted_sections.append(f"  {verdict} Verdict {i}{reason}")
                except:
                    formatted_sections.append(section)
            
            else:
                formatted_sections.append(section.strip())
        
        return "\n".join(formatted_sections)
        
    except Exception as e:
        logger.error(f"Error formatting logs: {e}")
        return str(log_text)

