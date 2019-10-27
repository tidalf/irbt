"""
Setup test configuration.

Setup test config
"""

from collections import namedtuple

from irbt import Robot

import pytest

from tests.cloud_mock import CloudMock

Credential = namedtuple('Credential', 'username password')


@pytest.fixture(scope='module')
def credential():
    """Return credential."""
    return Credential('test@example.com', 'test_password')


@pytest.fixture(scope='module')
def Cloud():  # noqa: N802
    """Cloud class (mock)."""
    return CloudMock


@pytest.fixture(scope='module')
def cloud(credential):
    """Cloud instance (mock)."""
    return CloudMock(credential.username, credential.password)


@pytest.fixture(scope='module')
def robot(cloud):
    """Robot instance (mock)."""
    return Robot(cloud)
