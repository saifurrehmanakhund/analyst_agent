"""Input guardrails for the data-analyst pipeline."""

import re
import logging

logger = logging.getLogger(__name__)

# Patterns that suggest a column may contain PII.
PII_PATTERNS = [
    r"ssn",
    r"social.?security",
    r"e.?mail",
    r"phone",
    r"credit.?card",
    r"password",
    r"passport",
    r"driver.?licen[sc]e",
    r"date.?of.?birth",
    r"dob",
    r"national.?id",
    r"tax.?id",
]

_PII_RE = re.compile("|".join(PII_PATTERNS), re.IGNORECASE)

# Patterns that suggest code injection attempts
MALICIOUS_PATTERNS = [
    # Python code execution
    r"\bexec\s*\(",
    r"\beval\s*\(",
    r"__import__",
    r"\bcompile\s*\(",
    r"\bglobals\s*\(",
    r"\blocals\s*\(",
    
    # OS/System commands
    r"\bos\s*\.\s*system",
    r"\bos\s*\.\s*popen",
    r"\bsubprocess",
    r"\bshutil\s*\.\s*rmtree",
    r"\bopen\s*\(",
    
    # File operations (overly broad for data queries)
    r"\bwrite\s*\(",
    r"\bremove\s*\(",
    r"\bunlink\s*\(",
    r"\bdelete.*file",
    
    # SQL injection attempts (even though we don't use raw SQL)
    r"\bDROP\s+TABLE",
    r"\bDROP\s+DATABASE",
    r"\bDELETE\s+FROM",
    r"\bTRUNCATE",
    r"\bALTER\s+TABLE",
    r"\bUPDATE\s+.*\s+SET",
    r";\s*DROP",
    r"--\s*$",  # SQL comment at end
    
    # Network/external access
    r"\bsocket\s*\.",
    r"\brequests\s*\.",
    r"\burllib",
    r"\bhttp\s*\.",
]

_MALICIOUS_RE = re.compile("|".join(MALICIOUS_PATTERNS), re.IGNORECASE)


def check_pii_columns(columns: list[str]) -> list[str]:
    """
    Return column names that match known PII patterns.
    
    Parameters
    ----------
    columns : list[str]
        Column names to check
        
    Returns
    -------
    list[str]
        Names of columns that appear to contain PII
    """
    return [col for col in columns if _PII_RE.search(col)]


def check_malicious_input(question: str) -> tuple[bool, str | None]:
    """
    Check if a user question contains potentially malicious code patterns.
    
    Parameters
    ----------
    question : str
        The natural language question from the user
        
    Returns
    -------
    tuple[bool, str | None]
        (is_malicious, error_message)
        - is_malicious: True if question contains suspicious patterns
        - error_message: User-friendly message if blocked, None otherwise
    """
    if not question:
        return False, None
    
    # Check for malicious patterns
    if _MALICIOUS_RE.search(question):
        logger.warning(f"Malicious pattern detected in question: {question[:100]}")
        return True, "❌ Your question contains potentially unsafe patterns. Please rephrase your question using natural language only."
    
    # Check for excessive length (potential DoS)
    if len(question) > 1000:
        logger.warning(f"Excessively long question ({len(question)} chars): {question[:100]}")
        return True, "❌ Question is too long. Please ask a more concise question (max 1000 characters)."
    
    return False, None


def check_pii_in_question(question: str) -> tuple[bool, str | None]:
    """
    Check if a user question is trying to expose PII.
    
    Parameters
    ----------
    question : str
        The natural language question from the user
        
    Returns
    -------
    tuple[bool, str | None]
        (has_pii_request, error_message)
        - has_pii_request: True if question asks for PII
        - error_message: User-friendly message if blocked, None otherwise
    """
    if not question:
        return False, None
    
    question_lower = question.lower()
    
    # Check for explicit PII requests
    for pattern in PII_PATTERNS:
        if re.search(pattern, question_lower):
            logger.warning(f"PII request detected in question: {question[:100]}")
            return True, "❌ Cannot process queries involving personal information (emails, phone numbers, SSNs, etc.)."
    
    # Check for "show all" or "export" patterns combined with email/names
    export_patterns = [r"show.*all.*email", r"get.*all.*email", r"export.*email", r"download.*user.*data"]
    for pattern in export_patterns:
        if re.search(pattern, question_lower):
            logger.warning(f"Data export request detected: {question[:100]}")
            return True, "❌ Cannot export or show all personal information. Ask specific questions instead."
    
    return False, None
