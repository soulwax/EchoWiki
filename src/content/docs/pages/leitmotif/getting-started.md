---
title: "Leitmotif Getting Started"
---

Leitmotif lives in the game repository as a submodule-style tool under:

```text
tools/leitmotif
```

It has two useful development modes.

## Web Shell

Use this when you are working on layout, forms, timeline behavior, keyboard shortcuts, or most TypeScript tests.

```powershell
cd tools/leitmotif
npm install
npm run dev
```

The web shell runs in a browser through Vite. It can render the editor without the Tauri desktop shell. Bridge calls that require native file dialogs or `choreo` report friendly "not running inside Tauri" messages instead of crashing.

## Desktop App

Use this when you need native file dialogs, real scene loading/saving, live preview from the game CLI, or export-to-game behavior.

```powershell
cargo build --bin choreo
cd tools/leitmotif
$env:CHOREO_BIN = "..\\..\\target\\debug\\choreo.exe"
npm run tauri:dev
```

`CHOREO_BIN` is the explicit path to the game's choreography CLI. If it is not set, the Tauri shell tries to run `choreo` from `PATH`.

## Verification

Use the smallest check that covers your change:

```powershell
npm test
npm run build
cargo check --manifest-path src-tauri/Cargo.toml
```

For bridge, export, or preview work, also verify the game-side CLI:

```powershell
cargo run --bin choreo -- validate Assets/Data/scenes
cargo run --bin choreo -- graph Assets/Data/scenes --json
```

## What To Open First

| Need | Read |
| --- | --- |
| Entry point and UI wiring | `src/main.ts` |
| Scene state and undo | `src/scene.ts` |
| Many-scene project behavior | `src/project.ts` |
| Tauri to `choreo` commands | `src-tauri/src/main.rs` |
| Browser-side bridge wrappers | `src/bridge.ts` |
| Timeline cards and add-beat picker | `src/timeline.ts` |
| Suggestions | `src/suggest.ts`, then `src/rules.ts` |

## First Run Checklist

1. Start with `npm run dev` and confirm the shell loads.
2. Press `?` in the app to see the keyboard shortcut overlay.
3. Run `npm test`.
4. Build `choreo`.
5. Run `npm run tauri:dev` with `CHOREO_BIN` set.
6. Open a scene file from `Assets/Data/scenes`.
7. Validate, preview, and export only after you understand where the target file will be written.

Next, read [Usage](../usage/) for the day-to-day authoring loop and [Moddability](../moddability/) before changing how Leitmotif treats ids, scene files, schema, or exported data.
