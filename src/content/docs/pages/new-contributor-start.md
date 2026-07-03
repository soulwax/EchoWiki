---
title: "New Contributor Start"
---

Welcome. EchoWarrior is a Rust-native 2D survivors-like prototype with a strong bias toward moddable, data-driven gameplay.

This page is the first-hour path for a new contributor.

## First Hour

1. Install Rust and confirm Cargo works:

```powershell
cargo --version
rustc --version
```

2. From the repository root, check that the project builds:

```powershell
cargo check
```

3. Run the prototype once:

```powershell
cargo run
```

4. Read the short project map:

- `README.md`
- `AI_CONTEXT.md`
- `Docs/TECHNICAL_NOTES.md`
- `TODO.md`

5. Pick one small contribution and find the right route in [Change Routes](../change-routes/).

## What Kind Of Project Is This?

EchoWarrior is not only a playable prototype. It is also an architecture experiment for a moddable action roguelite.

That means code changes should usually support at least one of these goals:

- make game behavior data-driven
- keep pure gameplay logic testable without a renderer
- keep runtime rendering/input/audio contained in `src/runtime`
- make release asset packaging reliable
- make modding easier to understand
- improve readability, feedback, or first-run feel

## Mental Model

```text
Assets/ and Mods/
  -> data, dialogue, scripts, shaders, audio, metadata

src/data, src/game, src/ui, src/save, src/scripting
  -> shared library code, ideally renderer-agnostic

src/runtime
  -> Macroquad-specific playable prototype

src/bin
  -> tools contributors run before shipping content or releases
```

## Good First Changes

Good first contributions are usually:

- documentation fixes
- small mod data examples
- `mod_check` diagnostics improvements
- focused tests around pure `src/game` or `src/data` behavior
- small UI text/layout fixes driven from `Assets/Data/ui.toml`
- asset-pack discoverability fixes

Avoid starting with:

- broad rewrites of `src/runtime/mod.rs`
- new dependencies
- new renderer frameworks
- new choreography systems
- hardcoded stats or content that should live in `Assets/`

## Project Rules That Matter Early

- Gameplay values belong in data files when practical.
- `src/game` and `src/data` must not import Macroquad.
- Missing/malformed content should degrade gracefully.
- Runtime-loaded assets must be included by asset-pack discovery.
- One YAML file per NPC.
- Use the existing choreography engine for scene beats.

## Where To Ask "Where Does This Go?"

Use [Change Routes](../change-routes/). If a change does not fit any route, it may need a design note before code.
