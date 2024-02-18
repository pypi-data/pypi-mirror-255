import pytest, subprocess
from my_functions_beatzaplenty import run_command

def test_run_command_successful_execution():
    command = ["echo", "Hello, World!"]
    assert run_command(command) is True

def test_run_command_failure():
    command = ["nonexistent_command"]
    assert run_command(command) is False

def test_run_command_exception_handling():
    command = ["command_with_syntax_error"]
    # Replace the command above with one that would cause an exception
    # in your run_command function, e.g., by having invalid syntax.
    with pytest.raises(Exception):
        run_command(subprocess.CalledProcessError)

# You can add more tests based on the specific scenarios you want to cover.
if __name__ == '__main__':
    pytest.main()
