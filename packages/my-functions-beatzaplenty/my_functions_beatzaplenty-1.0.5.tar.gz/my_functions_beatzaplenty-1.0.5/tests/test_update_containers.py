import pytest
from unittest.mock import MagicMock

# Assuming your module is named 'your_module'
from my_functions_beatzaplenty import update_containers, run_command

@pytest.fixture
def mock_run_command(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("my_functions_beatzaplenty.general_purpose.run_command", mock)
    return mock

def test_update_containers_success(mock_run_command):
    # Arrange
    services = ["esphome", "webdav"]

    # Act
    update_containers.main(services)

    # Assert
    assert mock_run_command.call_count == 4
    mock_run_command.assert_any_call(["docker-compose", "--file", "/docker/esphome/docker-compose.yml", "pull"])
    mock_run_command.assert_any_call(["docker-compose", "--file", "/docker/esphome/docker-compose.yml", "up", "-d"])
    mock_run_command.assert_any_call(["docker-compose", "--file", "/docker/webdav/docker-compose.yml", "pull"])
    mock_run_command.assert_any_call(["docker-compose", "--file", "/docker/webdav/docker-compose.yml", "up", "-d"])

def test_update_containers_failure(mock_run_command):
    # Arrange
    services = ["service1", "service2"]
    mock_run_command.side_effect = [True, False, True, False]

    # Act
    update_containers.main(services)

    # Assert
    assert mock_run_command.call_count == 4
    mock_run_command.assert_any_call(["docker-compose", "--file", "/docker/service1/docker-compose.yml", "pull"])
    mock_run_command.assert_any_call(["docker-compose", "--file", "/docker/service1/docker-compose.yml", "up", "-d"])
    mock_run_command.assert_any_call(["docker-compose", "--file", "/docker/service2/docker-compose.yml", "pull"])
    mock_run_command.assert_any_call(["docker-compose", "--file", "/docker/service2/docker-compose.yml", "up", "-d"])

    # The second service should not be attempted if the first one fails

# Run the tests with: pytest -v test_your_module.py
if __name__ == '__main__':
    pytest.main()