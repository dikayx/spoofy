import re


def extract_csrf_token(response_data):
    # Needed to extract the CSRF token from the response data and to use it in the form submission
    csrf_token_regex = (
        rb'<input\n\s*type="hidden"\n\s*name="csrf_token"\n\s*value="([^"]+)"\n\s*/>'
    )
    csrf_token = re.search(csrf_token_regex, response_data).group(1)
    return csrf_token


def test_index_page(client):
    # Test the index page loads correctly
    response = client.get("/")
    assert response.status_code == 200
    assert b"Enter a URL" in response.data


def test_404_page(client):
    # Test that a non-existing page returns a 404 status
    response = client.get("/invalid")
    assert response.status_code == 404


def test_index_title(client):
    # Test that the title of the index page is correct
    response = client.get("/")
    title_regex = rb"<title>\s*Spoofy \| Domain Spoofing Test\s*</title>"
    assert bool(re.search(title_regex, response.data))


def test_form_present(client):
    # Test that the form is present on the index page
    response = client.get("/")
    assert b'<form method="POST" id="analyzeForm">' in response.data


def test_submit_form(client):
    # Test form submission with CSRF token
    response = client.get("/")
    csrf_token = extract_csrf_token(response.data)
    post_response = client.post(
        "/", data={"url": "example.com", "csrf_token": csrf_token}
    )
    assert post_response.status_code == 200
    assert b"Domain Check Results" in post_response.data


def test_results_page_mx_record(client):
    # Test the results page for MX record display
    response = client.get("/")
    csrf_token = extract_csrf_token(response.data)
    post_response = client.post(
        "/", data={"url": "example.com", "csrf_token": csrf_token}
    )
    assert post_response.status_code == 200
    assert b"MX Record:" in post_response.data
    assert b"Valid" in post_response.data or b"Invalid" in post_response.data


def test_results_page_spf_record(client):
    # Test the results page for SPF record display
    response = client.get("/")
    csrf_token = extract_csrf_token(response.data)
    post_response = client.post(
        "/", data={"url": "example.com", "csrf_token": csrf_token}
    )
    assert post_response.status_code == 200
    assert b"SPF Record:" in post_response.data
    assert (
        b"Vulnerable" in post_response.data
        or b"Valid" in post_response.data
        or b"Invalid" in post_response.data
    )


def test_results_page_dmarc_record(client):
    # Test the results page for DMARC record display
    response = client.get("/")
    csrf_token = extract_csrf_token(response.data)
    post_response = client.post(
        "/", data={"url": "example.com", "csrf_token": csrf_token}
    )
    assert post_response.status_code == 200
    assert b"DMARC Record:" in post_response.data
    assert (
        b"Vulnerable" in post_response.data
        or b"Valid" in post_response.data
        or b"Invalid" in post_response.data
    )


def test_results_page_dkim_record(client):
    # Test the results page for DKIM record display
    response = client.get("/")
    csrf_token = extract_csrf_token(response.data)
    post_response = client.post(
        "/", data={"url": "example.com", "csrf_token": csrf_token}
    )
    assert post_response.status_code == 200
    assert b"DKIM Record:" in post_response.data
    assert b"Valid" in post_response.data or b"Invalid" in post_response.data


def test_results_page_back_button(client):
    # Test that the "Check Another Domain" button is present on the results page
    response = client.get("/")
    csrf_token = extract_csrf_token(response.data)
    post_response = client.post(
        "/", data={"url": "example.com", "csrf_token": csrf_token}
    )
    assert post_response.status_code == 200
    assert b"Check Another Domain" in post_response.data


def test_submit_button_present(client):
    response = client.get("/")
    submit_button_regex = rb'<button\s+type="submit"\s+class="btn\s+btn-primary\s+btn-lg\s+btn-block"\s+id="submitButton"\s*>'
    assert re.search(submit_button_regex, response.data) is not None


def test_spinner_present(client):
    # The spinner is only visible when the form is being submitted
    response = client.get("/")
    spinner_regex = rb'<div\s+id="spinner"\s+class="spinner-border\s+text-primary\s+ms-2"\s+role="status">'
    assert re.search(spinner_regex, response.data) is None
