import pytest
from unittest.mock import patch
from my_functions_beatzaplenty import remote_update

@pytest.fixture
def mock_ssh():
    with patch('my_functions_beatzaplenty.general_purpose.create_ssh_connection') as mock:
        yield mock

@pytest.fixture
def mock_execute_ssh_command():
    with patch('my_functions_beatzaplenty.general_purpose.execute_ssh_command') as mock:
        yield mock

def test_remote_update_with_default_values(mock_ssh, mock_execute_ssh_command):
    config = {
        'ssh_hostname': 'edge.lan.ddnsgeek.com',
        'ssh_username': 'linode',
        'keyfile': '/home/wayne/.ssh/id_rsa.pub',
        'containers': 'doods passbolt'
        # You may add other config parameters as needed for your test cases
    }

    remote_update(config)

    # Assert that create_ssh_connection was called with the correct arguments
    mock_ssh.assert_called_once_with('edge.lan.ddnsgeek.com', 'linode', '/home/wayne/.ssh/id_rsa.pub', port=22)

    # Assert that execute_ssh_command was called with the correct argument
    expected_command = 'python3 -m my_functions_beatzaplenty.remote_update doods passbolt'
    mock_execute_ssh_command.assert_called_once_with(mock_ssh.return_value, command=expected_command)

def test_remote_update_with_custom_values(mock_ssh, mock_execute_ssh_command):
    config = {
        'ssh_hostname': 'example.com',
        'ssh_username': 'user',
        'keyfile': 'key.pem',
        'ssh_port': 2222,
        'update_script': 'custom_script.py',
        'containers': 'container1 container2'
        # You may add other config parameters as needed for your test cases
    }

    remote_update(config)

    # Assert that create_ssh_connection was called with the correct arguments
    mock_ssh.assert_called_once_with('example.com', 'user', 'key.pem', port=2222)

    # Assert that execute_ssh_command was called with the correct argument
    expected_command = 'python3 custom_script.py'
    mock_execute_ssh_command.assert_called_once_with(mock_ssh.return_value, command=expected_command)

# Add more test cases as needed
if __name__ == "__main__":
    pytest.main()