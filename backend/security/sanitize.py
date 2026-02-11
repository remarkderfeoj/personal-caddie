"""
Security Sanitization Module

Prevents prompt injection and other text-based attacks.

CRITICAL: Never pass raw user input directly into LLM prompts.
Always sanitize first.
"""

import re
from typing import Optional

# Maximum length for user-generated text
MAX_USER_INPUT_LENGTH = 500

# Patterns that look like prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"ignore\s+all\s+previous",
    r"disregard\s+previous",
    r"system\s*:",
    r"you\s+are\s+now",
    r"you\s+are\s+a",
    r"pretend\s+you\s+are",
    r"act\s+as",
    r"<\s*system\s*>",
    r"<\s*user\s*>",
    r"<\s*assistant\s*>",
]

INJECTION_REGEX = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


def sanitize_user_text(text: str) -> str:
    """
    Sanitize user-generated text.
    
    Removes:
    - Control characters
    - Excessive whitespace
    - Prompt injection patterns
    - HTML tags
    - Null bytes
    
    Args:
        text: Raw user input
    
    Returns:
        Sanitized text (may be empty if everything was removed)
    
    Raises:
        ValueError: If text appears to be a prompt injection attempt
    """
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:MAX_USER_INPUT_LENGTH]
    
    # Check for prompt injection patterns
    if INJECTION_REGEX.search(text):
        raise ValueError("Text contains suspicious patterns and was rejected")
    
    # Remove control characters and null bytes
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Collapse excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def build_caddie_prompt(template: str, **safe_vars) -> str:
    """
    Safe prompt builder for LLM integration (future).
    
    Only inserts validated, typed data into predefined template slots.
    User-generated text goes in a clearly delimited block.
    
    Args:
        template: Prompt template with {placeholders}
        **safe_vars: Validated variables to insert
    
    Returns:
        Assembled prompt with user input clearly isolated
    
    Example:
        prompt = build_caddie_prompt(
            "Generate recommendation for {club} at {distance} yards.\\n\\nUser notes: <user_input>{notes}</user_input>",
            club="7-iron",
            distance=150,
            notes=sanitize_user_text(raw_user_notes)
        )
    """
    # Ensure all variables are sanitized
    for key, value in safe_vars.items():
        if isinstance(value, str) and len(value) > 0:
            # If it looks like user content, ensure it's sanitized
            if not (isinstance(value, (int, float, bool)) or value in safe_vars.get('_safe_enums', [])):
                safe_vars[key] = sanitize_user_text(value)
    
    return template.format(**safe_vars)


def validate_id_format(id_str: str, max_length: int = 50) -> bool:
    """
    Validate ID format (alphanumeric, dash, underscore only).
    
    Args:
        id_str: ID string to validate
        max_length: Maximum allowed length
    
    Returns:
        True if valid, False otherwise
    """
    if not id_str or len(id_str) > max_length:
        return False
    
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', id_str))
