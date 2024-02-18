A Sphinx theme for sites hosted at [palewi.re](https://palewi.re/).

## Installation

Install the theme with pipenv:

```bash
pipenv install palewire-sphinx-theme
```

Then, in your Sphinx project's `conf.py` file, add the following line:

```python
html_theme = "palewire"
```

## Configuration

The theme supports two different layouts, a "wide" layout and a "narrow" layout. The wide layout that includes a sidebar is the default. You can switch to the narrow single-column layout by adding the following line to your `conf.py` file:

```python
html_theme_options = {
    "nosidebar": True,
}
```

When using the wide layout, you can control which elements are included in the sidebar by adding the `html_sidebars` option to your `conf.py` file. Here's an example that includes the default sidebar elements:

```python
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
    ]
}
```

Further configution of this setting is explained by the [Sphinx documentation](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_sidebars).
