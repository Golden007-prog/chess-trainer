"""The locale registry, i18n/locales.toml (brief §8): one entry per UI file, and valid values."""

from pathlib import Path

import pytest

from app.locales import DEFAULT_LOCALE, load_locales

I18N_DIR = Path(__file__).parent.parent.parent / "web" / "i18n"
GOOD = """
[locales.en]
direction = "ltr"
scripts = ["latin"]
reviewed = true
"""


def test_every_ui_file_has_an_entry_and_every_entry_a_file():
    """The registry lists exactly the languages with a file in web/i18n."""
    files = {path.stem for path in I18N_DIR.glob("*.json")}
    assert set(load_locales()) == files


def test_the_fallback_is_english_left_to_right():
    """The fallback locale is in the registry and is left to right."""
    locale = load_locales()[DEFAULT_LOCALE]
    assert locale.direction == "ltr"
    assert locale.reviewed


def test_optional_tools_can_be_left_out(tmp_path):
    """A locale with no LanguageTool code or Vale styles loads, with nothing to check.

    Args:
        tmp_path (Path): A temporary folder.
    """
    path = tmp_path / "locales.toml"
    path.write_text(GOOD, encoding="utf-8")
    locale = load_locales(path)["en"]
    assert locale.languagetool is None
    assert locale.vale == ()


@pytest.mark.parametrize(
    "change",
    [
        ('direction = "ltr"', 'direction = "up"'),
        ('scripts = ["latin"]', 'scripts = ["klingon"]'),
        ('scripts = ["latin"]', "scripts = []"),
        ("reviewed = true", 'reviewed = "yes"'),
        ("reviewed = true", 'reviewed = true\nfallback = "pt-BR"'),
        ("reviewed = true", 'reviewed = true\nvale = "UI"'),
        ("[locales.en]", "[locales.de]"),
    ],
)
def test_bad_values_fail_loudly(tmp_path, change):
    """A wrong, unknown or missing value, or no English entry, is an error.

    Args:
        tmp_path (Path): A temporary folder.
        change (tuple[str, str]): The text replaced in a good registry, and its replacement.
    """
    path = tmp_path / "locales.toml"
    path.write_text(GOOD.replace(*change), encoding="utf-8")
    with pytest.raises(ValueError):
        load_locales(path)
