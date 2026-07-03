# GitHub Pages

This wiki is a static GitHub Pages site published from its own public repository.
Inside the private game repository it is mounted as a submodule under:

```text
Docs/Wiki
```

Inside the wiki repository itself, `index.html`, `_sidebar.md`, `assets/`, and
`pages/` live at the repository root. It uses Docsify, so there is no Node,
Cargo, Ruby, or build step for the wiki itself. `index.html` loads Markdown
pages at runtime.

## Publishing

The wiki repository includes:

```text
.github/workflows/pages.yml
```

That workflow publishes the wiki repository root as the GitHub Pages artifact on
pushes to `main`, and can also be run manually from the GitHub Actions tab.

The workflow expects repository Pages settings to use "GitHub Actions" as the source.

## Local Preview

Run a static server:

```powershell
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Editing Pages

Add Markdown pages under:

```text
pages
```

Then add the page to:

```text
_sidebar.md
```

Docsify uses hash routing, so normal page refreshes work on GitHub Pages without a separate 404 redirect.

## Dependencies

The site loads these libraries from jsDelivr:

- Docsify
- Docsify Themeable
- Docsify search
- Docsify copy-code
- Docsify pagination

If offline docs become important later, vendor those assets under `vendor/` and update `index.html` to use local files.
