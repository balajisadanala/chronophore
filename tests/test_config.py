import pathlib
import pytest

from chronophore.config import _load_config, _use_default


@pytest.fixture()
def missing_options_file(tmpdir, request):
    """Return a path to an config file that is
    valid, but missing expected options (commented
    out below).
    Remove the file when a test is finished with it.
    """
    data_dir = pathlib.Path(str(tmpdir))
    missing_options_file = data_dir.joinpath('invalid')
    with missing_options_file.open('w') as f:
        f.write(
            '[gui]\n'
            # + 'message_duration = 5\n'
            + 'gui_welcome_label = Welcome to the STEM Learning Center!\n'
            # + 'full_user_names = True\n'
            + 'large_font_size = 30\n'
            + 'medium_font_size = 18\n'
            + 'small_font_size = 15\n'
            + 'tiny_font_size = 10\n'
        )

    def tearDown():
        if missing_options_file.exists():
            missing_options_file.unlink()

    request.addfinalizer(tearDown)
    return missing_options_file


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
    sections = ('gui',)
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


def test_missing_options(missing_options_file):
    """Load a config file that is valid,
    but missing one or more options
    """
    backup = missing_options_file.with_suffix('.bak')
    _load_config(missing_options_file)
    assert backup.is_file()
    assert missing_options_file.is_file()
    backup.unlink()
