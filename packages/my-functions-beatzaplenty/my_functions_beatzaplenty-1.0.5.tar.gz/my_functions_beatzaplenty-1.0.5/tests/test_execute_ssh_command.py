import pytest
from unittest.mock import Mock, patch
from my_functions_beatzaplenty import execute_ssh_command  # Replace 'your_module' with the actual module name

@pytest.fixture
def mock_ssh_client():
    # Create a mock SSHClient object
    mock_ssh = Mock()
    return mock_ssh

def test_execute_ssh_command_success(mock_ssh_client, capsys, monkeypatch):
    # Mock the necessary objects and methods
    mock_transport = Mock()
    mock_channel = Mock()
    mock_transport.open_session.return_value = mock_channel
    mock_ssh_client.get_transport.return_value = mock_transport

    # Set up the command and expected output
    command = "echo 'Hello, World!'"
    expected_output = "Hello, World!"

    # Mock the output received from the channel
    mock_channel.recv_ready.side_effect = [True, False]  # To exit the loop after one iteration
    mock_channel.recv.return_value.decode.return_value = expected_output

    # Mock the exit status
    mock_channel.recv_exit_status.return_value = 0

    with monkeypatch.context() as m:
        # Replace the built-in print function with a function that captures the output
        captured_output = []

        def mock_print(*args, **kwargs):
            captured_output.append(args[0])

        m.setattr("builtins.print", mock_print)

        # Call the function
        exit_status = execute_ssh_command(mock_ssh_client, command)

        # Assert the expected behavior
        mock_ssh_client.close.assert_called_once()
        mock_ssh_client.get_transport.assert_called_once()
        mock_transport.open_session.assert_called_once_with()
        mock_channel.get_pty.assert_called_once_with()
        mock_channel.exec_command.assert_called_once_with(command)

        # Check the captured output
        assert captured_output[0] == expected_output

        # Check the exit status
        assert exit_status == 0

# Run the tests using pytest
# Command: pytest -v test_your_module.py
if __name__ == '__main__':
    pytest.main()
