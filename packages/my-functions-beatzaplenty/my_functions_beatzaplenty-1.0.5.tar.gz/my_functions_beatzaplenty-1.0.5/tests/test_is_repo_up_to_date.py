import subprocess
import pytest
from unittest.mock import patch
from my_functions_beatzaplenty import is_repo_up_to_date

def test_is_repo_up_to_date_up_to_date(tmp_path, capsys, monkeypatch):
    # Set up a temporary directory for testing
    test_path = tmp_path / "test_repo"
    test_path.mkdir()

    # Monkeypatch subprocess.run to return a status indicating the repository is up to date
    def mock_subprocess_run(*args, **kwargs):
        if args == (['git', 'fetch'],) or args == (['git', 'status', '-uno'],):
            return subprocess.CompletedProcess(None, 0, "On branch main\nYour branch is up to date with 'origin/main'.", None)
        return subprocess.run(*args, **kwargs)

    monkeypatch.setattr(subprocess, 'run', mock_subprocess_run)

    # Call the function with the test path
    is_repo_up_to_date(test_path)

    # Capture the printed output
    captured = capsys.readouterr()

    # Assert that the output indicates the repository is up to date
    assert "Local repository is up to date." in captured.out
    assert "Local repository is not up to date. Pulling changes..." not in captured.out
    assert "Changes pulled successfully." not in captured.out

def test_is_repo_up_to_date_behind(tmp_path, capsys, monkeypatch):
    # Set up a temporary directory for testing
    test_path = tmp_path / "test_repo"
    test_path.mkdir()

    # Monkeypatch subprocess.run to return a status indicating the repository is behind
    def mock_subprocess_run(*args, **kwargs):
        if args == (['git', 'fetch'],):
            return subprocess.CompletedProcess(None, 0, '', None)
        elif args == (['git', 'status', '-uno'],):
            return subprocess.CompletedProcess(None, 0, "On branch main\nYour branch is behind 'origin/main' by 1 commit, and can be fast-forwarded.", None)
        elif args == (['git', 'pull'],):
            return subprocess.CompletedProcess(None, 0, '', None)
        return subprocess.run(*args, **kwargs)

    monkeypatch.setattr(subprocess, 'run', mock_subprocess_run)

    # Call the function with the test path
    is_repo_up_to_date(test_path)

    # Capture the printed output
    captured = capsys.readouterr()

    # Assert that the output indicates the repository is behind and changes are pulled successfully
    assert "Local repository is not up to date. Pulling changes..." in captured.out
    assert "Changes pulled successfully." in captured.out
    assert "Local repository is up to date." not in captured.out

if __name__ == "__main__":
    pytest.main()
