---
title: "EchoWarrior Contributor Wiki"
---

<div class="hero-lockup">
  <img class="site-mark" src="/Shisaku-2.png" alt="EchoWarrior wiki mark" />
  <img class="hero-screenshot" src="/assets/readme-window.png" alt="EchoWarrior prototype window" />
</div>

This wiki is written for someone who may want to contribute to EchoWarrior and needs a calm first map of the codebase. It documents the main code surface: the crate entry points, app shell, state model, asset and pack gateways, logging, performance hooks, mod manifest layer, and command-line tools.

It deliberately does not document every `src/game`, `src/runtime`, `src/data`, `src/ui`, `src/save`, or `src/scripting` submodule in detail. Those areas already have focused design docs, and they change faster than the main crate boundary.

## Prototype At A Glance

<div class="visual-grid">
  <figure>
    <img src="/shader_arena_1.png" alt="Shader arena with VFX tuning controls and runtime HUD" />
    <figcaption>Shader arena: runtime VFX, HUD layering, and data-driven tuning visible in one frame.</figcaption>
  </figure>
  <figure>
    <img src="/dialogue_1.png" alt="Dialogue scene with rain, HUD, and speaker portrait" />
    <figcaption>Dialogue scene: choreography, speaker UI, atmosphere, and gameplay state sharing the same runtime.</figcaption>
  </figure>
</div>

## What To Read First

- [New Contributor Start](pages/new-contributor-start/) if this is your first hour in the repo.
- [Visual Orientation](pages/visual-orientation/) to connect screenshots to the systems behind them.
- [Contribution Workflow](pages/contribution-workflow/) before opening a pull request.
- [Change Routes](pages/change-routes/) when you know what you want to change but not where it belongs.
- [Verification Guide](pages/verification-guide/) to choose the right checks.
- [Tiny Moddable Feature](pages/guides/tiny-moddable-feature/) for a slow, guided first implementation path.
- [Architecture Chapter](pages/architecture/) for the big picture first, then progressively deeper details.
- [Main Code Map](pages/main-code-map/) for a file-by-file reference to the main Rust files.
- [Assets And Packaging](pages/assets-and-packaging/) before changing runtime asset discovery or release packs.
- [Asset Pack Reference](pages/asset-pack-reference/) for the public pack API and read order.
- [CLI Tools](pages/cli-tools/) before using `asset_pack`, `sprite_cutter`, `mod_check`, or `choreo`.

## Contributor Promise

EchoWarrior is built around moddability, data-driven content, and a clean split between renderer-specific runtime code and pure gameplay/data code. A good contribution should make the game easier to understand, easier to mod, or more reliable to ship.

The fastest way to get oriented is to run the game once, read the contributor start page, then pick a small change with a clear verification command.

## Site Stack

This is a Vercel-hosted static site powered by [Astro](https://astro.build/) and
[Starlight](https://starlight.astro.build/). Pages are Markdown files under
`src/content/docs`, the navigation is configured in `astro.config.mjs`, and the
site builds to static HTML in `dist`.

Vercel builds the site with `npm run build` and serves `dist`. In the private
game repository, this repo is mounted as the `Docs/Wiki` submodule.

## Related Project Docs

The deployed wiki artifact contains only this public wiki repository. For deeper project notes in a private game checkout, read:

- `Docs/TECHNICAL_NOTES.md`
- `Docs/MODDING.md`
- `Docs/RELEASE.md`
- `Docs/CHOREO_FORMAT.md`
- `Docs/GAME_DESIGN_DOCUMENT.md`

## Local Preview

Run the Starlight dev server:

```powershell
npm run dev
```

Then open the local URL printed by Astro.
