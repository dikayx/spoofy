import re


def is_valid_domain(domain) -> bool:
    """
    Basic domain validation using regex.

    :param domain: The domain to validate as a string.

    :return: A boolean indicating if the domain is valid.
    """
    domain_pattern = re.compile(
        r"^(?!:\/\/)([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,11}?$"
    )
    return domain_pattern.match(domain) is not None
