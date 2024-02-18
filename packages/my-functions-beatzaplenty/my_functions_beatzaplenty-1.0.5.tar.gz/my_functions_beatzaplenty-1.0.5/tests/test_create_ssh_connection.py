import os
from unittest.mock import Mock, patch
import pytest
from my_functions_beatzaplenty import create_ssh_connection

def test_create_ssh_connection_success():
    hostname = "localhost"
    username = "wayne"
    keyfile = f'{os.getenv("HOME")}/.ssh/id_rsa'
    port = 22  # Change this to a valid port for your testing environment

    # Mocking the paramiko.SSHClient and paramiko.AutoAddPolicy
    with patch("paramiko.SSHClient") as mock_ssh_client, \
         patch("paramiko.AutoAddPolicy") as mock_auto_add_policy:
        
        # Mock the return value of connect method
        mock_connect = Mock()
        mock_ssh_client.return_value = mock_connect

        # Call the function
        ssh = create_ssh_connection(hostname, username, keyfile, port=port, max_retries=5, retry_interval=1)

        # Assertions
        assert ssh == mock_connect
        mock_ssh_client.assert_called_once()
        mock_auto_add_policy.assert_called_once()
        mock_connect.connect.assert_called_once_with(hostname, username=username, key_filename=keyfile, port=port)

def test_create_ssh_connection_failure():
    hostname = "notahost"
    username = "user"
    keyfile = "/path/to/nonexistent/keyfile"
    port = 2222  # Change this to a valid port for your testing environment

    with pytest.raises(RuntimeError, match="Failed to create SSH connection after 10 attempts."):
        create_ssh_connection(hostname, username, keyfile, max_retries=10, retry_interval=1, port=port)

# Run the tests with pytest
if __name__ == '__main__':
    pytest.main()
