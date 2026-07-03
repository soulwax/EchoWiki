---
title: "Vercel Deployment"
---

This wiki is a static Vercel site published from its own public repository.
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
vercel.json
```

Vercel uses that file to install dependencies with `npm ci`, build with
`npm run build`, and serve the generated `dist` directory. The Astro `site`
value is read from Vercel environment variables when available, so preview and
production deployments generate correct canonical URLs at the deployed site
root.

## Local Preview

Run the Starlight dev server:

```powershell
npm run dev
```

Then open the local URL printed by Astro.

## Deploy From The CLI

After linking this directory to a Vercel project, a preview deployment can be
created with:

```powershell
npx vercel deploy
```

Production deploys use:

```powershell
npx vercel deploy --prod
```

For deterministic deploys, build locally first and deploy the prebuilt output:

```powershell
npx vercel build --prod
npx vercel deploy --prebuilt --prod
```

## Editing Pages

Add Markdown pages under:

```text
src/content/docs
```

Then add the page to the Starlight sidebar in:

```text
astro.config.mjs
```

Starlight emits static routes, so normal page refreshes work on Vercel.

## Dependencies

The site uses:

- Astro
- Starlight
- TypeScript for project checks
- a tiny local Mermaid Markdown transform

Mermaid rendering is initialized from the Starlight page head.
