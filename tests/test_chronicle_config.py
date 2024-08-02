import pytest

from labchronicle.chronicle import Chronicle
import yaml


class MockChronicle(Chronicle):
    """
    A mock class for testing Chronicle. Allows killing the singleton instance.
    """

    @classmethod
    def kill_singleton(_class):
        _class._instance = None


# Test default config
def test_default_config(monkeypatch):
    c = MockChronicle()
    assert c._config["log_path"] == "./log"
    assert c._config["handler"] == "hdf5"
    c.kill_singleton()


# Test config from file
def test_config_from_file(tmp_path):
    config = {
        "log_path": "./test_log_read",
        "handler": "test_handler_read"
    }

    config_path = tmp_path / "config.yml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    c = MockChronicle(config_path=config_path)
    assert c._config["log_path"] == "./test_log_read"
    assert c._config["handler"] == "test_handler_read"

    c.kill_singleton()


# Test environment variable configuration
def test_config_from_env_vars(monkeypatch):
    monkeypatch.setenv('LAB_CHRONICLE_LOG_DIR', './env_log')
    monkeypatch.setenv('LAB_CHRONICLE_HANDLER', 'env_handler')

    c = MockChronicle()
    assert c._config["log_path"] == "./env_log"
    assert c._config["handler"] == "env_handler"
    c.kill_singleton()


# Test invalid configuration
def test_invalid_config(monkeypatch):
    def mock_invalid(*args, **kwargs):
        class MockFile:
            def __enter__(self, *args, **kwargs):
                return self

            def __exit__(self, *args, **kwargs):
                pass

            def read(self, *args, **kwargs):
                return ""

        return MockFile()

    monkeypatch.setattr("builtins.open", mock_invalid)

    with pytest.raises(ValueError):
        c = MockChronicle("invalid_path")
        c.kill_singleton()
