from chronophore.config import _load_config, _use_default


def test_no_config_file(nonexistent_file):
    """Try to load a config file that doesn't exist.
    Ensure that the default config file is created in
    its place.
    """
    test_config = nonexistent_file
    _load_config(test_config)
    assert test_config.is_file()


def test_use_default(nonexistent_file):
    """Try to load a config file that doesn't exist.
    Ensure that the default configuration is loaded
    instead.
    """
    parser = _use_default(nonexistent_file)
    sections = ('gui', 'validation')
    assert set(sections) == set(parser.sections())


def test_invalid_config_file(invalid_file):
    """Try to load in invalid config file.
    Copy it to a backup and replace it with
    the default.
    """
    backup = invalid_file.with_suffix('.bak')
    _load_config(invalid_file)
    assert backup.is_file()
    assert invalid_file.is_file()
    backup.unlink()
