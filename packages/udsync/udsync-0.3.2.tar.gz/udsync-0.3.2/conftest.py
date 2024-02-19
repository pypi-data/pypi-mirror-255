import pytest
import pathlib
from confattr import ConfigFile

@pytest.fixture(autouse=True)
def reset_config(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(ConfigFile, 'config_directory', str(tmp_path))
