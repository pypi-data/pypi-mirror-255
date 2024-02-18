import pytest


def test_extracting_tokens(root):
    # Be careful with failures here not to print tokens.
    #  To avoid printing local variables use pytest.fail
    if root._session_token is None:
        pytest.fail("session token should not be None")
    if root._master_token is None:
        pytest.fail("master token should not be None")
