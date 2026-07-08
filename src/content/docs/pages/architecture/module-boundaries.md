---
title: "2. Module Boundaries"
---

This page goes one layer deeper than the fundamentals and shows how the crate is divided.

## Top-Level Shape

```mermaid
flowchart TB
    main[src/main.rs]
    runtime[src/runtime]
    lib[src/lib.rs]
    app[src/app.rs]
    states[src/states.rs]
    assets[src/assets.rs]
    assetpack[src/asset_pack.rs]
    modding[src/modding.rs]
    render[src/render.rs]
    logging[src/logging.rs]
    perf[src/perf.rs]
    game[src/game]
    data[src/data]
    ui[src/ui]
    save[src/save]
    scripting[src/scripting]
    bins[src/bin]
    vk2d[crates/vk2d<br/>soulwax/vk2d]

    main --> runtime
    runtime --> lib
    lib --> app
    lib --> states
    lib --> assets
    lib --> assetpack
    lib --> modding
    lib --> render
    lib --> logging
    lib --> perf
    lib --> game
    lib --> data
    lib --> ui
    lib --> save
    lib --> scripting
    bins --> lib
    bins --> vk2d
```

## Boundary Table

| Area | Owns | Should avoid |
| --- | --- | --- |
| `src/main.rs` | Macroquad entry and error display path | game logic |
| `src/runtime` | draw/input/audio/window/live actor presentation | reusable pure rules |
| `src/game` | pure gameplay models and systems | Macroquad, file I/O where avoidable |
| `src/data` | serde models, TOML loading, fallbacks | rendering, live runtime state |
| `src/ui` | UI models, theme/layout helpers, some draw helpers | gameplay ownership |
| `src/render.rs` | backend-neutral 2D renderer vocabulary | Macroquad, wgpu, winit, game-specific asset paths |
| `src/runtime/renderer_mq.rs` | adapter from `Renderer2d` verbs to Macroquad drawing | pure gameplay rules, renderer feature design |
| `crates/vk2d` | local checkout of `soulwax/vk2d`, the standalone renderer crate | EchoWarrior gameplay assumptions or hardcoded `Assets/` paths |
| `src/save` | account/run save models and paths | rendering decisions |
| `src/scripting` | Lua API and command buffers | direct rendering side effects |
| `src/asset_pack.rs` | loose/packed reads and discovery | gameplay rules |
| `src/modding.rs` | mod manifest discovery/layer ordering | content behavior |
| `src/bin` | command-line tools over shared APIs | duplicated game logic |

## "Where Should This Go?"

```mermaid
flowchart TD
    change[New change]
    dataq{Is it content or tuning?}
    pureq{Can it be tested without rendering?}
    renderq{Does it need Macroquad types or draw calls?}
    toolq{Is it a contributor/release tool?}
    assetq{Is it about file inclusion or packs?}

    change --> dataq
    dataq -- yes --> assets[Assets/Data, Dialogue, Scripts, Metadata]
    dataq -- no --> pureq
    pureq -- yes --> game_or_data[src/game or src/data]
    pureq -- no --> renderq
    renderq -- yes --> runtime[src/runtime]
    renderq -- no --> toolq
    toolq -- yes --> bins[src/bin]
    toolq -- no --> assetq
    assetq -- yes --> assetpack[src/asset_pack.rs]
    assetq -- no --> design[Write a short design note first]
```

## Public Library Surface

`src/lib.rs` exposes modules for tools and tests. Adding a top-level `pub mod` is an architectural choice: it means the module is part of the shared crate surface.

Good candidates:

- pure logic needed by tests or tools
- data models used by multiple bins
- save/modding/packaging helpers

Poor candidates:

- one-off runtime helpers
- Macroquad-only drawing state
- temporary experiment code

## Renderer Boundary Rule

Renderer work now has its own boundary. `src/render.rs` describes what a frame wants to draw; backend adapters decide how to draw it.

```mermaid
flowchart LR
    game[Runtime or UI code]
    boundary[src/render.rs<br/>Renderer2d]
    mq[src/runtime/renderer_mq.rs<br/>Macroquad today]
    vk[crates/vk2d<br/>soulwax/vk2d path]

    game --> boundary
    boundary --> mq
    boundary -. migration target .-> vk
```

Do not pass backend types upward. If a helper takes `macroquad::Texture2D`, `wgpu::Device`, or `winit` window state, it belongs in a backend adapter or probe, not in gameplay, data, or UI model code.

## Runtime Is Still A Bridge

The live prototype still owns a lot of per-frame state in `PrototypeRuntime`. Some of that state is mirrored into pure systems through bridges, such as the ECS lifecycle bridge.

That means a contributor should not assume every gameplay concept has fully migrated to `src/game`. When in doubt:

1. find the live runtime owner
2. extract only the pure rule if useful
3. keep rendering/input/audio at the runtime boundary
