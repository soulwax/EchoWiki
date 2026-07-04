---
title: "Leitmotif Screenshots"
---

These screenshots are generated from the current Leitmotif web shell using a small sample scene. They are meant to orient contributors before they open the code.

## Editor Overview

<figure class="wide-figure">
  <img src="/leitmotif/editor-overview.png" alt="Leitmotif editor overview" />
  <figcaption>The loaded scene shows chained sequences, selected beat state, the stage shell, trigger editor, timeline steps, and schema-driven inspector fields.</figcaption>
</figure>

## Action Picker

<figure class="wide-figure">
  <img src="/leitmotif/action-picker.png" alt="Leitmotif action picker opened from a timeline step" />
  <figcaption>The timeline's add-beat picker offers a natural next beat first, then the broader verb list. Suggestions are deterministic today and route through `SceneDoc`.</figcaption>
</figure>

## Keyboard Overlay

<figure class="wide-figure">
  <img src="/leitmotif/shortcuts.png" alt="Leitmotif keyboard shortcuts overlay" />
  <figcaption>The `?` overlay is generated from the same binding table that handles the shortcuts, so the help surface and behavior stay in sync.</figcaption>
</figure>

## Compact View

<figure class="wide-figure">
  <img src="/leitmotif/editor-compact.png" alt="Leitmotif compact viewport editor screenshot" />
  <figcaption>The compact viewport keeps the three-column model visible: sequence list, stage/timeline, and inspector.</figcaption>
</figure>

## How These Were Captured

The screenshots were captured from `npm run dev` at `http://127.0.0.1:8780/` using the development-only `window.__lmLoad(json)` seam in `src/main.ts`.

That seam is intentionally dev-only. It lets contributors and screenshot automation load a scene into the browser without native file dialogs. Production builds compile it away through `import.meta.env.DEV`.

