import os
import configparser
import pytest
from my_functions_beatzaplenty import create_config_file


@pytest.fixture
def sample_config_data():
    return {
        'Section1': {'key1': 'value1', 'key2': 'value2'},
        'Section2': {'key3': 'value3', 'key4': 'value4'}
    }

@pytest.fixture
def temp_config_file(tmp_path):
    return tmp_path / "test_config.ini"

def test_create_config_file(tmp_path, sample_config_data):
    file_path = tmp_path / "test_config.ini"
    
    create_config_file(sample_config_data, file_path)

    # Check if the file is created
    assert file_path.exists()

    # Check if the content of the file is correct
    config = configparser.ConfigParser()
    config.read(file_path)
    
    assert config.sections() == ['Section1', 'Section2']
    assert dict(config['Section1']) == {'key1': 'value1', 'key2': 'value2'}
    assert dict(config['Section2']) == {'key3': 'value3', 'key4': 'value4'}

def test_create_config_file_exception_handling(tmp_path, sample_config_data, capsys):
    # Create a file in read-only mode to simulate an exception
    file_path = tmp_path / "test_config.ini"
    file_path.touch()
    os.chmod(file_path, 0o444)  # Make the file read-only

    create_config_file(sample_config_data, file_path)

    # Check if an error message is printed
    captured = capsys.readouterr()
    assert "Error:" in captured.out

if __name__ == '__main__':
    pytest.main()
