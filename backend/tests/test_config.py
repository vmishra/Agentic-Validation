import config

def test_model_default():
    assert config.MODEL == "gemini-3.5-flash"

def test_ignore_set_has_node_modules():
    assert "node_modules" in config.IGNORE_DIRS
    assert ".git" in config.IGNORE_DIRS

def test_caps_are_positive():
    assert config.MAX_FILE_BYTES == 1_000_000
    assert config.ZIP_MAX_UNCOMPRESSED == 300_000_000
