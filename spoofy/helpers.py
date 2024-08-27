import re


def is_valid_domain(domain):
    # Basic domain validation regex
    domain_pattern = re.compile(
        r"^(?!:\/\/)([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,11}?$"
    )
    return domain_pattern.match(domain) is not None
