"""Sphinx theme for palewi.re documentation."""
from os import path


def setup(app):
    """Register the theme with Sphinx."""
    theme_path = path.abspath(path.dirname(__file__))
    app.add_html_theme("palewire", theme_path)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
