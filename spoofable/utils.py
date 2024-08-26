import dns.resolver
import dns.dnssec
import dns.message
import dns.query
import dns.rdatatype
import re


def check_mx_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = [str(r.exchange).rstrip('.') for r in answers]
        invalid_responses = {"", ".", "localhost"}  # Add more if needed

        valid_mx_records = [
            mx for mx in mx_records
            if mx not in invalid_responses
        ]

        valid = len(valid_mx_records) > 0

        if not valid:
            mx_records = ["Invalid or misconfigured MX records found"]
        else:
            mx_records = valid_mx_records

    except Exception as e:
        mx_records = [str(e)]
        valid = False
    
    return valid, mx_records


def check_spf_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        spf_record = next((r.to_text() for r in answers if 'v=spf1' in r.to_text()), None)
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


def check_dmarc_record(domain):
    try:
        answers = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
        dmarc_record = next((r.to_text() for r in answers if 'v=DMARC1' in r.to_text()), None)
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


def check_dkim_record(domain):
    # List of common selectors to check
    common_selectors = [
        "default", "google", "mail", "key1", "dkim", "s1", "s2", "k1", "k2"
    ]
    
    valid = False
    dkim_record = "No valid DKIM record found"

    try:
        for selector in common_selectors:
            dkim_domain = f"{selector}._domainkey.{domain}"
            try:
                answers = dns.resolver.resolve(dkim_domain, 'TXT')
                dkim_record = next((r.to_text() for r in answers if 'v=DKIM1' in r.to_text()), None)
                if dkim_record:
                    valid = True
                    break  # Stop checking once a valid record is found
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                continue  # Move on to the next selector if no record is found
    except Exception as e:
        dkim_record = str(e)
        valid = False

    return valid, dkim_record
