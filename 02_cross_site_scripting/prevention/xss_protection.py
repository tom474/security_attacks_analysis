import re

# Layer 2: XSS Detection - Input Validation
def detect_xss(input_string):
    """
    Detect potential XSS patterns in the input.
    """
    patterns = [
        r"<script.*?>",  # Detect script tags
        r"on\w+="        # Detect inline event handlers (e.g., onclick, onmouseover)
    ]
    for pattern in patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    return False

# Layer 3: Input Sanitization
def sanitize_input(input_string):
    """
    Sanitize user input to remove potentially dangerous characters.
    """
    sanitized = re.sub(r"[<>\"']", "", input_string)
    print(f"[INFO] Input sanitized: {sanitized}")
    return sanitized