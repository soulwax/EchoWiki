---
title: "GitHub Pages"
---

This wiki is a static GitHub Pages site published from its own public repository.
Inside the private game repository it is mounted as a submodule under:

```text
Docs/Wiki
```

Inside the wiki repository itself, source pages live under `src/content/docs`,
static images live under `public/assets`, and the sidebar is configured in
`astro.config.mjs`. The site uses Astro Starlight and builds to static HTML in
`dist`.

## Publishing

The wiki repository includes:

```text
.github/workflows/pages.yml
```

That workflow installs dependencies, runs `npm run build`, and publishes `dist`
as the GitHub Pages artifact on pushes to `main`. It can also be run manually
from the GitHub Actions tab.

The workflow expects repository Pages settings to use "GitHub Actions" as the source.

## Local Preview

Run the Starlight dev server:

```powershell
npm run dev
```

Then open the local URL printed by Astro.

## Editing Pages

Add Markdown pages under:

```text
src/content/docs
```

Then add the page to the Starlight sidebar in:

```text
astro.config.mjs
```

Starlight emits static routes, so normal page refreshes work on GitHub Pages.

## Dependencies

The site uses:

- Astro
- Starlight
- TypeScript for project checks
- a tiny local Mermaid Markdown transform

Mermaid rendering is initialized from the Starlight page head.
