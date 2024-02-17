import pytest

from sl_optimizer.utils import check_file_exists


def test_check_file_exists(tmp_path):
    file_path = tmp_path / "nonexistent_file.txt"
    check_file_exists(str(file_path))


def test_check_file_exists_raises_error_when_file_exists(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.touch()

    with pytest.raises(FileExistsError):
        check_file_exists(str(file_path))
