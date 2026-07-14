---
title: "Menage Getting Started"
---

Menage lives in the `tools/menage` submodule. It has two useful launch modes:

| Mode | Command | Use it for |
| --- | --- | --- |
| Web-only | `npm run dev` | Reading metadata, browsing PNGs, checking layout, taking screenshots. |
| Tauri desktop | `npm run tauri:dev` | Saving metadata, running `sprite_cutter`, running `sheets validate`, and auditing with `asset_pack`. |

## Build The Game-Side Tools

From the EchoWarrior repo root:

```powershell
cargo build --bin sprite_cutter --bin asset_pack --bin sheets
```

Those binaries are the authority. Menage is the editor; the game CLIs decide whether a file is valid and what a cut would write.

## Run The Web Shell

From `tools/menage`:

```powershell
$env:MENAGE_GAME_ROOT = "D:\Workspace\Rust\EchoWarrior"
npm install
npm run dev
```

Open `http://127.0.0.1:5174/`.

Web mode is intentionally read-only. The Vite dev server serves the game repo through `/@game/...`, so images and TOML can load in a normal browser. Save, cut, check, and audit actions that need native process access require the Tauri shell.

## Run The Desktop Shell

From `tools/menage`:

```powershell
$env:MENAGE_GAME_ROOT = "D:\Workspace\Rust\EchoWarrior"
$env:MENAGE_SPRITE_CUTTER_BIN = "D:\Workspace\Rust\EchoWarrior\target\debug\sprite_cutter.exe"
$env:MENAGE_ASSET_PACK_BIN = "D:\Workspace\Rust\EchoWarrior\target\debug\asset_pack.exe"
$env:MENAGE_SHEETS_BIN = "D:\Workspace\Rust\EchoWarrior\target\debug\sheets.exe"
npm run tauri:dev
```

If the environment variables are absent, Menage tries `sprite_cutter`, `asset_pack`, and `sheets` on `PATH`. If no game root is configured in Tauri mode, click the path area in the toolbar and pick the EchoWarrior repo root.

## First Sanity Check

After launch, check the report panel:

- it should say `Loaded Assets/Metadata/spritesheets.toml`
- the Library should list sheets, tilesets, atlases, and unregistered PNGs
- selecting `player` should show a 6 by 10 sheet with animation bands
- `Check` should use `sheets validate --json --images` in Tauri mode
- `Dry-run` should run `sprite_cutter --dry-run` in Tauri mode

## Verification

For Menage-only changes:

```powershell
cd tools/menage
npm test
npm run build
cd src-tauri
cargo test
```

For changes that affect the game-side metadata or cutters, also run from the game repo root:

```powershell
cargo run --bin sprite_cutter -- --all --dry-run
cargo run --bin asset_pack -- --dry-run --list
```
