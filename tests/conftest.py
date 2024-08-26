import pytest

from spoofable.app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture
def mock_dns_resolver(mocker):
    return mocker.patch('dns.resolver.resolve')