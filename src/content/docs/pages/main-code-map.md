---
title: "Main Code Map"
---

## Library Root

| File | Role |
| --- | --- |
| `src/lib.rs` | Public crate module declarations. Binaries and tests import shared code through this surface. |
| `src/app.rs` | Early app shell model: selected class, high-level app state, default asset manifest, run clock, and world bounds. |
| `src/states.rs` | Library-side `AppState` enum and simple input/pause policy helpers. |
| `src/assets.rs` | Stable asset identifiers, sprite/font manifest defaults, sprite metadata parsing, and spritesheet descriptor binding. |
| `src/asset_pack.rs` | Asset pack format, loose file reads, active mod overlay reads, default pack reads, identity pack reads, and release asset discovery. |
| `src/modding.rs` | `Mods/<mod_id>/mod.toml` discovery, dependency ordering, namespace selection, and save manifest conversion. |
| `src/render.rs` | Renderer-neutral 2D drawing contract, value types, handles, and material/uniform verbs used by the canonical vk2d adapter and Macroquad compatibility path. |
| `src/logging.rs` | `tracing` subscriber initialization and last-50-line ring buffer for the debug overlay. |
| `src/perf.rs` | Debug-only performance scope helper and `perf_scope!` macro. |

## Binary Front Doors

| File | Role |
| --- | --- |
| `src/main.rs` | Macroquad entry point. Configures the window and runs the prototype runtime. |
| `src/bin/asset_pack.rs` | CLI for building, verifying, inventorying, and unpacking `data.pak` and `identity.pak`. |
| `src/bin/sprite_cutter.rs` | CLI for cutting spritesheets described by `Assets/Metadata/spritesheets.toml`. |
| `src/bin/mod_check.rs` | Shipping gate for data, scripts, shaders, commands, mod packs, and cross-file references. |
| `src/bin/choreo.rs` | Contract CLI for choreography validation, JSON/TOML conversion, schema generation, preview sampling, graph export, and GUI picker ids. |
| `src/bin/wgpu_probe.rs` | Focused `winit` consumer smoke entry for `soulwax/vk2d`; useful for renderer checks without booting the full game-state shell. |

## Workspace Crates

| Path | Role |
| --- | --- |
| `crates/vk2d` | Git submodule checkout of [soulwax/vk2d](https://github.com/soulwax/vk2d), the standalone immediate-mode 2D renderer crate consumed by EchoWarrior's probe path. |

## What Is Not Covered Here

This page does not document every file under:

- `src/runtime/`
- `src/game/`
- `src/data/`
- `src/ui/`
- `src/save/`
- `src/scripting/`

Those folders are subsystem code, and should be documented in focused design notes or in their own wiki sections when they stabilize.
