"""
Test cloud class.

Early stage
"""


def test_cloud(credential, Cloud):  # noqa: N803
    """
    Test cloud.

    Test cloud
    """
    assert(credential.username == 'test@example.com')
    assert(credential.password == 'test_password')
    cloud = Cloud(credential.username, credential.password)
    assert(cloud)
