# EchoWiki

Public contributor website for EchoWarrior, mounted into the private game
repository as the `Docs/Wiki` submodule.

The site is built with Astro and Starlight, then deployed to GitHub Pages from
this repository.

## Local Development

```powershell
npm install
npm run dev
```

## Verification

```powershell
npm run build
```

## Content

- Source pages live under `src/content/docs`.
- Static images live under `public/assets`.
- Sidebar structure lives in `astro.config.mjs`.
- Mermaid diagrams use fenced `mermaid` code blocks and are transformed by
  `src/plugins/remark-mermaid.mjs`.

## Publishing

The `.github/workflows/pages.yml` workflow builds the Starlight site and uploads
`dist` as the GitHub Pages artifact.
