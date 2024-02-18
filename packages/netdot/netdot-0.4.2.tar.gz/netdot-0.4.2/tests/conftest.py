import os
import xml.etree.ElementTree as ET

import pytest

import netdot


def pytest_addoption(parser):
    parser.addoption(
        '--generate-docs',
        action='store_true',
        default=False,
        help='Update the generated documentation files.',
    )


@pytest.fixture
def generate_docs(request):
    return request.config.getoption('--generate-docs')


@pytest.fixture
def netdot_url() -> str:
    return os.environ.get('NETDOT_URL', 'https://nsdb.uoregon.edu')


@pytest.fixture
def username() -> str:
    return os.environ.get('NETDOT_USERNAME', 'not-defined-NETDOT_USERNAME-env-var')


@pytest.fixture
def password() -> str:
    return os.environ.get('NETDOT_PASSWORD', 'not-defined-NETDOT_PASSWORD-env-var')


@pytest.fixture
def repository(netdot_url, username, password) -> netdot.Repository:
    return netdot.Repository(
        netdot_url,
        username,
        password,
        threads=1,
        times_to_retry=0,
        timeout=5,  # seconds
    )


@pytest.fixture(scope='module')
def vcr_config():
    return {
        'before_record_request': [sanitize_NetdotLogin_path],
        'before_record_response': [raise_for_System_Errors, ignore_html_body],
    }


def raise_for_System_Errors(response):
    """Raise an exception if the response body indicates an error."""
    response_body = response['body']['string']
    # b'<div class="containerhead">Error</div>',
    # b'System error',
    if b'error' in response_body.lower() and not response_body.startswith(HTML_IGNORED_MESSAGE):
        error_index = response_body.lower().rfind(b'error')
        error_message = response_body[error_index - 100 : error_index + 300]
        # TODO figure out how to also ensure that the cassette doesn't get written in this case... Maybe return None?
        raise Exception(f"{response_body}\nDetected a System error in the response body (see full response body above): {error_message}")
    return response


HTML_IGNORED_MESSAGE = b'HTML content ignored (unless the word "error" was found) (see conftest.py)'
def ignore_html_body(response):
    """We do not care about responses that start with <html>.

    We are testing data APIs, and this makes the cassettes much more readable to ignore the HTML pages returned.
    """
    try:
        if response['body']['string'].strip().startswith(b'<html>'):
            response['body']['string'] = HTML_IGNORED_MESSAGE
    except TypeError:
        pass
    return response


def sanitize_NetdotLogin_path(request):
    """Clear the "body" of the request if it is sent to the /NetdotLogin path."""
    if request.path == '/NetdotLogin':
        request.body = 'BLANK (see conftest.py)'
    return request
