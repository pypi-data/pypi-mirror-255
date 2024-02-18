import os
from dotenv import load_dotenv, find_dotenv, set_key
import sys
from unittest.mock import patch

import pytest
if sys.platform == 'win32':
    from cdh_dav_python.windows_service.windows_credential import WindowsCredential
    import win32cred

sys.path.append("..")

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


@pytest.fixture
def mocker():
    with patch.object(win32cred, 'CredEnumerate') as mock_CredEnumerate:
        yield mock_CredEnumerate


def test_list_credentials():

    if sys.platform != 'win32':
        return

    # Call the function under test
    credentials = WindowsCredential.list_credentials()

    # Assert the returned credentials match the expected value
    # assert credentials == expected_credentials

    print(credentials)


def test_get_credential_by_address(mocker):

    if sys.platform != 'win32':
        return

    # Define the expected credential
    expected_credential = {
        'TargetName': 'git:https://github.com',
        'UserName': 'username',
        'CredentialBlob': 'password'
    }
    mocker.return_value = [expected_credential]

    # Call the function under test
    credential = WindowsCredential.get_credential_by_address(
        'LegacyGeneric:target=GitHub - https://api.github.com/jcbowyer')

    # Assert that the mocked function was called correctly
    # mocker.assert_called_once_with(None, win32cred.CRED_TYPE_GENERIC)

    # Assert the returned credential matches the expected value
    # assert credential == expected_credential

    print(credential)


if __name__ == '__main__':
    pytest.main()
