import dns.dnssec
import dns.message
import dns.query
import dns.rdatatype
import dns.resolver
import re
import socket
import ssl

from datetime import datetime


def check_mx_record(domain) -> tuple:
    """
    Check if the domain has valid MX records.

    :param domain: The domain to check as a string.

    :return: A tuple containing a boolean indicating if the MX records are valid and a list of MX records.
    """
    try:
        answers = dns.resolver.resolve(domain, "MX")
        mx_records = [str(r.exchange).rstrip(".") for r in answers]
        invalid_responses = {"", ".", "localhost"}

        valid_mx_records = [mx for mx in mx_records if mx not in invalid_responses]

        valid = len(valid_mx_records) > 0

        if not valid:
            mx_records = ["Invalid or misconfigured MX records found"]
        else:
            mx_records = valid_mx_records

    except Exception as e:
        mx_records = [str(e)]
        valid = False

    return valid, mx_records


def check_spf_record(domain) -> tuple:
    """
    Check if the domain has a valid SPF record.

    :param domain: The domain to check as a string.

    :return: A tuple containing a boolean indicating if the SPF record is valid and the SPF record.
    """
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        spf_record = next(
            (r.to_text() for r in answers if "v=spf1" in r.to_text()), None
        )
        valid = True
        if spf_record:
            if re.search(r"\s*(\+all|\~all|\-all)", spf_record, re.IGNORECASE):
                valid = False
        else:
            spf_record = "No SPF record found"
            valid = False
    except Exception as e:
        spf_record = str(e)
        valid = False
    return valid, spf_record


def check_dmarc_record(domain) -> tuple:
    """
    Check if the domain has a valid DMARC record.

    :param domain: The domain to check as a string.

    :return: A tuple containing a boolean indicating if the DMARC record is valid, the DMARC record, and an assessment.
    """
    try:
        answers = dns.resolver.resolve(f"_dmarc.{domain}", "TXT")
        dmarc_record = next(
            (r.to_text() for r in answers if "v=DMARC1" in r.to_text()), None
        )
        valid = False
        assessment = "No DMARC record found"
        if dmarc_record:
            if "p=none" in dmarc_record:
                assessment = "Vulnerable (p=none)"
            elif "p=quarantine" in dmarc_record or "p=reject" in dmarc_record:
                valid = True
                assessment = "Protected (p=quarantine/reject)"
            else:
                assessment = "Unknown DMARC policy"
        else:
            dmarc_record = "No DMARC record found"
    except Exception as e:
        dmarc_record = str(e)
        valid = False
        assessment = "Error checking DMARC record"
    return valid, dmarc_record, assessment


def check_dkim_record(domain) -> tuple:
    """
    Check if the domain has a valid DKIM record. Only common selectors are checked as per RFC 6376.

    :param domain: The domain to check as a string.

    :return: A tuple containing a boolean indicating if the DKIM record is valid and the DKIM record.
    """
    common_selectors = [
        "default",
        "google",
        "mail",
        "key1",
        "dkim",
        "s1",
        "s2",
        "k1",
        "k2",
    ]

    valid = False
    dkim_record = "No valid DKIM record found"

    try:
        for selector in common_selectors:
            dkim_domain = f"{selector}._domainkey.{domain}"
            try:
                answers = dns.resolver.resolve(dkim_domain, "TXT")
                dkim_record = next(
                    (r.to_text() for r in answers if "v=DKIM1" in r.to_text()), None
                )
                if dkim_record:
                    valid = True
                    break
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                continue
    except Exception as e:
        dkim_record = str(e)
        valid = False

    return valid, dkim_record


def check_ssl_certificate(domain) -> tuple:
    """
    Check if the domain has a valid SSL certificate by connecting to the domain over HTTPS.
    The certificate is considered valid if the common name or any of the
    Subject Alternative Names (SANs) match the domain.

    :param domain: The domain to check as a string.

    :return: A tuple containing a boolean indicating if the SSL certificate is valid and a message.
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

                subject = dict(x[0] for x in cert["subject"])
                common_name = subject.get("commonName", "")

                san_list = []
                if "subjectAltName" in cert:
                    san_list = [name[1] for name in cert["subjectAltName"]]

                issuer = dict(x[0] for x in cert["issuer"])
                issuer_common_name = issuer.get("commonName", "")

                not_before = cert.get("notBefore")
                not_after = cert.get("notAfter")
                validity_start = datetime.strptime(not_before, "%b %d %H:%M:%S %Y %Z")
                validity_end = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")

                domain_pattern = re.compile(
                    rf"^(?:\*\.)?{re.escape(domain)}$", re.IGNORECASE
                )

                if domain_pattern.match(common_name) or any(
                    domain_pattern.match(san) for san in san_list
                ):
                    return (
                        True,
                        f"Issued by: {issuer_common_name}. Valid from {validity_start} to {validity_end}",
                    )
                else:
                    return (
                        False,
                        f"Certificate common name {common_name} or SANs {san_list} do not match domain {domain}",
                    )

    except ssl.SSLCertVerificationError as e:
        return False, f"Certificate verification error: {str(e)}"
    except Exception as e:
        return False, f"Certificate error: {str(e)}"
