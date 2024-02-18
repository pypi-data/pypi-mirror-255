import pytest

from seeq import spy
from seeq.sdk.configuration import ClientConfiguration


@pytest.mark.unit
def test_session_segregation():
    session1 = spy.Session()
    session2 = spy.Session()

    default_retry = ClientConfiguration.DEFAULT_RETRY_TIMEOUT_IN_SECONDS

    assert session1.options.retry_timeout_in_seconds == default_retry
    assert session2.options.retry_timeout_in_seconds == default_retry
    assert session1.client_configuration.verify_ssl
    assert session2.client_configuration.verify_ssl

    session1.client_configuration.verify_ssl = False
    session2.options.retry_timeout_in_seconds = 3254

    assert session1.client_configuration.retry_timeout_in_seconds == default_retry
    assert session2.client_configuration.retry_timeout_in_seconds == 3254
    assert not session1.client_configuration.verify_ssl
    assert session2.client_configuration.verify_ssl
