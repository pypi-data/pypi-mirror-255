import pytest
from unittest.mock import MagicMock, call, patch
from my_functions_beatzaplenty import run_updates  # replace 'your_module' with the actual module name

@pytest.fixture
def mock_platform(monkeypatch):
    def mock_freedesktop_os_release():
        return {'ID': 'linuxmint'}
    
    monkeypatch.setattr('platform.freedesktop_os_release', mock_freedesktop_os_release)

@pytest.fixture
def mock_run_command(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('my_functions_beatzaplenty.general_purpose.run_command', mock)
    return mock

@pytest.fixture
def mock_check_command_exists(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('my_functions_beatzaplenty.general_purpose.check_command_exists', mock)
    return mock
    
    
@pytest.fixture
def mock_update_containers(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('my_functions_beatzaplenty.update_containers.main', mock)
    return mock

def test_run_updates(mock_platform, mock_run_command, mock_check_command_exists, mock_update_containers, monkeypatch):
    containers = ['container1', 'container2']

    # Mock run_command to do nothing
    with patch('my_functions_beatzaplenty.general_purpose.run_command', new_callable=MagicMock) as mock_run_command:
        run_updates(containers)

        # Assertions for the behavior of your mocked functions
        mock_run_command.assert_has_calls([
            call(('sudo', 'apt-get', 'update')),
            call(('sudo', 'apt-get', 'upgrade', '-y')),
            call(('sudo', 'apt-get', 'autoremove', '-y')),
            call(('flatpak', 'update', '-y')),
            call(('sudo', 'flatpak', 'remove', '--unused', '-y')),
            call(('cinnamon-spice-updater', '--update-all')),
        ], any_order=True)

    mock_check_command_exists.assert_called_with("docker")

    mock_update_containers.assert_called_once_with(containers)

if __name__ == '__main__':
    pytest.main()
