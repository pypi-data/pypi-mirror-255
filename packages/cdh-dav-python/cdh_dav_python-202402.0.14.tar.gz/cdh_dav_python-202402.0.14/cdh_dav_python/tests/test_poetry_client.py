from cdh_dav_python.poetry_service.poetry_client import PoetryClient
import subprocess


def test_print_version(capsys):
    """
    Test case to verify the output of the print_version method in the PoetryClient class.

    It checks if the output matches the expected output after calling the print_version method.

    Args:
        capsys: pytest fixture for capturing stdout and stderr.

    Returns:
        None
    """
    # Arrange
    expected_output = "current_working_dir:/path/to/current/working/dir\n"
    expected_output += "b'1.1.0\\n': poetry version succeeded"

    # Act
    PoetryClient.print_version()

    # Assert
    captured = capsys.readouterr()
    assert captured.out == expected_output
