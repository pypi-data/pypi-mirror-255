from unittest.mock import call
from unittest.mock import patch
import pytest
from my_functions_beatzaplenty import install_required_modules

@pytest.fixture
def requirements_file(tmp_path):
    # Create a temporary requirements.txt file for testing
    requirements_content = "numpy==1.18.5\nrequests==2.25.1\n"
    requirements_path = tmp_path / "requirements.txt"
    with open(requirements_path, "w") as f:
        f.write(requirements_content)
    return str(requirements_path)

def test_install_required_modules_installed(capfd, requirements_file):
    # Mock find_spec to simulate that the modules are already installed
    with patch('importlib.util.find_spec', return_value=True):
        install_required_modules(requirements_file)

    # Check output
    captured = capfd.readouterr()
    assert "Module numpy is already installed." in captured.out
    assert "Module requests is already installed." in captured.out

def test_install_required_modules_not_installed(capfd, requirements_file):
    # Mock find_spec to simulate that the modules are not installed
    with patch('importlib.util.find_spec', return_value=None):
        # Mock subprocess.call to prevent actual installation during the test
        with patch('subprocess.call') as mock_call:
            install_required_modules(requirements_file)

    # Check output
    captured = capfd.readouterr()
    assert "Module numpy not found. Installing..." in captured.out
    assert "Module requests not found. Installing..." in captured.out

    # Check that pip install was called with the correct arguments
    expected_calls = [
    call(['pip', 'install', 'numpy==1.18.5']),
    call(['pip', 'install', 'requests==2.25.1']),
]
    mock_call.assert_has_calls(expected_calls, any_order=True)


def test_install_required_modules_missing_file(capfd):
    # Mock find_spec to simulate that the modules are not installed
    with patch('importlib.util.find_spec', return_value=None):
        # Mock subprocess.call to prevent actual installation during the test
        with patch('subprocess.call'):
            with pytest.raises(FileNotFoundError) as e:
                install_required_modules("nonexistent_file.txt")
    print("Actual error message:", str(e.value))
    # Check if the expected substring is present in the error message
    assert "The requirements file 'nonexistent_file.txt' does not exist." in str(e.value)
if __name__ == '__main__':
    pytest.main()
