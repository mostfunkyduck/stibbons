import re

def parse_email(email_header: str) -> str:
    results = re.search(r'\s?<?([a-zA-Z0-9]+@[a-zA-Z0-9.]+\s?)>?', email_header)
    if not results:
        return ''
    return results.group(1)

