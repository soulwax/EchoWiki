---
title: "Menage Screenshots"
---

These captures come from the current Menage web shell at `http://127.0.0.1:5174/`, with `MENAGE_GAME_ROOT` pointed at the EchoWarrior checkout. They are meant to orient contributors before they open the code.

## Selected Sheet

<figure class="wide-figure">
  <img src="/menage/sheet-selected.png" alt="Menage selected sheet view" />
  <figcaption>The selected `player` sheet shows the Library on the left, animation bands over the source sheet in the center, editable cutting facts on the right, and live lint at the bottom.</figcaption>
</figure>

## End Product Preview

<figure class="wide-figure">
  <img src="/menage/atlas-product.png" alt="Menage end-product contact sheet view" />
  <figcaption>The end-product tab shows the crops the cutter will produce, grouped by animation. This is the quickest visual check for off-by-one grid and frame-count mistakes.</figcaption>
</figure>

## Initial Shell

<figure class="wide-figure">
  <img src="/menage/overview.png" alt="Menage initial shell after loading metadata" />
  <figcaption>The initial shell loads `spritesheets.toml`, lists registered sheets, tilesets, atlas descriptors, and provides the toolbar actions. In web mode, native actions still show why the desktop shell is required.</figcaption>
</figure>

## Compact View

<figure class="wide-figure">
  <img src="/menage/compact.png" alt="Menage compact browser viewport" />
  <figcaption>The compact viewport preserves the contributor loop: pick an asset, inspect the stage, edit metadata, then use the ribbon/report to understand validation.</figcaption>
</figure>

## How These Were Captured

The screenshots were captured from web-only mode:

```powershell
cd tools/menage
$env:MENAGE_GAME_ROOT = "D:\Workspace\Rust\EchoWarrior"
npm run dev
```

The selected-sheet and end-product captures used a headless Chromium DevTools script to click the first sheet and switch tabs. No repository files were changed during capture.
