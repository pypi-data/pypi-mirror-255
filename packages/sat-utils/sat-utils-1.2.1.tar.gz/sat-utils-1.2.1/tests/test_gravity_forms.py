from unittest.mock import patch

from requests.exceptions import RequestException
from sat.gravity_forms import GravityForms


def test_environment_variable_error():
    try:
        gravity_forms = GravityForms()
        gravity_forms.get("/forms/2/entries")
        assert False
    except ValueError:
        assert True


def test_request_exception_get(caplog):
    with patch("requests_oauthlib.OAuth1Session.get") as mock_get:
        mock_get.side_effect = RequestException("Simulated request exception.")
        gravity_forms = GravityForms(
            consumer_key="your_key", consumer_secret="your_secret", base_url="https://baseurl.edu"
        )
        response = gravity_forms.get("/forms/2/entries")
        assert response == {}
        assert "Simulated request exception." in caplog.text
