
from simbatch.core import settings as sett
import pytest


@pytest.fixture(scope="module")
def settings():
    # TODO pytest-datadir pytest-datafiles
    return sett.Settings(5, ini_file="S:/simbatch/simbatch/config.ini")


def test_update_ui_colors(settings):
    settings.ui_color_mode = 1
    assert settings.update_ui_colors() is True


def test_check_data_integration(settings):
    assert settings.check_data_integration() is True