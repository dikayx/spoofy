from unittest.mock import MagicMock
from spoofable.utils import check_mx_record, check_spf_record, check_dmarc_record, check_dkim_record
from unittest.mock import patch, MagicMock
import dns.resolver


@patch('dns.resolver.resolve')
def test_check_mx_record_valid(mock_dns_resolver):
    # Simulate a valid MX record response
    mock_answer = MagicMock()
    mock_answer.exchange = "mx.example.com."
    mock_dns_resolver.return_value = [mock_answer]

    valid, records = check_mx_record("example.com")
    assert valid is True
    assert records == ["mx.example.com"]

@patch('dns.resolver.resolve')
def test_check_mx_record_invalid_minimal_response(mock_dns_resolver):
    # Simulate a minimal/invalid MX record response
    mock_answer = MagicMock()
    mock_answer.exchange = "."
    mock_dns_resolver.return_value = [mock_answer]

    valid, records = check_mx_record("example.com")
    assert valid is False
    assert records == ["Invalid or misconfigured MX records found"]

@patch('dns.resolver.resolve')
def test_check_mx_record_exception(mock_dns_resolver):
    # Simulate DNS resolver throwing an exception
    mock_dns_resolver.side_effect = dns.resolver.NoAnswer("No MX record found")

    valid, records = check_mx_record("example.com")
    assert valid is False
    assert "No MX record found" in records[0]


@patch('dns.resolver.resolve')
def test_check_spf_record_valid(mock_dns_resolver):
    # Simulate a valid SPF record response
    mock_answer = MagicMock()
    mock_answer.to_text.return_value = 'v=spf1 ip4:192.0.2.0/24 -all'
    mock_dns_resolver.return_value = [mock_answer]

    valid, spf_record = check_spf_record("example.com")
    assert valid is False  # The SPF record contains '-all', which should mark it as invalid
    assert spf_record == 'v=spf1 ip4:192.0.2.0/24 -all'

@patch('dns.resolver.resolve')
def test_check_spf_record_no_record(mock_dns_resolver):
    # Simulate no SPF record found
    mock_dns_resolver.return_value = []

    valid, spf_record = check_spf_record("example.com")
    assert valid is False
    assert spf_record == "No SPF record found"

@patch('dns.resolver.resolve')
def test_check_spf_record_exception(mock_dns_resolver):
    # Simulate DNS resolver throwing an exception
    mock_dns_resolver.side_effect = dns.resolver.NoAnswer("No SPF record found")

    valid, spf_record = check_spf_record("example.com")
    assert valid is False
    assert "No SPF record found" in spf_record


@patch('dns.resolver.resolve')
def test_check_dmarc_record_vulnerable(mock_dns_resolver):
    # Simulate a DMARC record with policy p=none (vulnerable)
    mock_answer = MagicMock()
    mock_answer.to_text.return_value = 'v=DMARC1; p=none'
    mock_dns_resolver.return_value = [mock_answer]

    valid, dmarc_record, assessment = check_dmarc_record("example.com")
    assert valid is False
    assert dmarc_record == 'v=DMARC1; p=none'
    assert assessment == "Vulnerable (p=none)"

@patch('dns.resolver.resolve')
def test_check_dmarc_record_protected(mock_dns_resolver):
    # Simulate a DMARC record with policy p=quarantine (protected)
    mock_answer = MagicMock()
    mock_answer.to_text.return_value = 'v=DMARC1; p=quarantine'
    mock_dns_resolver.return_value = [mock_answer]

    valid, dmarc_record, assessment = check_dmarc_record("example.com")
    assert valid is True
    assert dmarc_record == 'v=DMARC1; p=quarantine'
    assert assessment == "Protected (p=quarantine/reject)"

@patch('dns.resolver.resolve')
def test_check_dmarc_record_no_record(mock_dns_resolver):
    # Simulate no DMARC record found
    mock_dns_resolver.return_value = []

    valid, dmarc_record, assessment = check_dmarc_record("example.com")
    assert valid is False
    assert dmarc_record == "No DMARC record found"
    assert assessment == "No DMARC record found"

@patch('dns.resolver.resolve')
def test_check_dmarc_record_exception(mock_dns_resolver):
    # Simulate DNS resolver throwing an exception
    mock_dns_resolver.side_effect = dns.resolver.NoAnswer("No DMARC record found")

    valid, dmarc_record, assessment = check_dmarc_record("example.com")
    assert valid is False
    assert "No DMARC record found" in dmarc_record
    assert assessment == "Error checking DMARC record"


@patch('dns.resolver.resolve')
def test_check_dkim_record_valid(mock_dns_resolver):
    # Simulate a valid DKIM record response for the 'default' selector
    mock_answer = MagicMock()
    mock_answer.to_text.return_value = 'v=DKIM1; k=rsa; p=...'
    mock_dns_resolver.return_value = [mock_answer]

    valid, dkim_record = check_dkim_record("example.com")
    assert valid is True
    assert 'v=DKIM1' in dkim_record

@patch('dns.resolver.resolve')
def test_check_dkim_record_no_valid(mock_dns_resolver):
    # Simulate no valid DKIM record found
    mock_dns_resolver.side_effect = dns.resolver.NoAnswer()
    
    valid, dkim_record = check_dkim_record("example.com")
    assert valid is False
    assert dkim_record == "No valid DKIM record found"

@patch('dns.resolver.resolve')
def test_check_dkim_record_multiple_selectors(mock_dns_resolver):
    # Simulate the second selector being valid
    def resolve_side_effect(dkim_domain, record_type):
        if dkim_domain == "mail._domainkey.example.com":
            mock_answer = MagicMock()
            mock_answer.to_text.return_value = 'v=DKIM1; k=rsa; p=...'
            return [mock_answer]
        else:
            raise dns.resolver.NoAnswer()

    mock_dns_resolver.side_effect = resolve_side_effect
    
    valid, dkim_record = check_dkim_record("example.com")
    assert valid is True
    assert 'v=DKIM1' in dkim_record
