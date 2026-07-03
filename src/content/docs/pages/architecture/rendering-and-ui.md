---
title: "10. Rendering And UI"
---

Rendering is the clearest place where EchoWarrior must keep boundaries tidy: world simulation, world rendering, post-processing, and screen-space UI all happen in one frame, but they do different jobs.

## Layer Stack

```mermaid
flowchart TB
    sim[Runtime simulation state]
    camera[World camera]
    terrain[Terrain and props]
    actors[Player, enemies, NPCs]
    worldfx[World VFX and particles]
    emissive[Emissive / bloom buffers]
    post[Ambient tint / post-process]
    overlays[Modal overlays]
    hud[HUD and UI]

    sim --> camera
    camera --> terrain --> actors --> worldfx
    worldfx --> emissive
    terrain --> post
    actors --> post
    emissive --> post
    post --> overlays --> hud
```

Exact implementation details change, but the conceptual stack stays useful for contributors.

## World Space vs Screen Space

```mermaid
flowchart LR
    world[World-space positions<br/>Y-up arena]
    helper[world_to_screen / camera helpers]
    screen[Screen-space UI<br/>Y-down pixels]

    world --> helper --> screen
```

Do not duplicate projection math for labels, hit tests, or overlays. Use existing runtime helpers.

## UI Ownership

```mermaid
flowchart TB
    data[Assets/Data/ui.toml and theme.toml]
    theme[src/ui/theme.rs]
    layout[src/ui/layout.rs]
    models[src/ui models]
    draw[src/ui/draw.rs, hud.rs, dialogue.rs]
    runtime[src/runtime calls draw paths]

    data --> theme
    data --> layout
    theme --> draw
    layout --> draw
    models --> draw
    runtime --> draw
```

UI should be data-driven where practical. Text, colors, budgets, and common layout values should not drift into random runtime constants.

## Shader And VFX Flow

```mermaid
flowchart TD
    manifest[Assets/Data/shaders.toml]
    sources[shader source files]
    loader[runtime/assets shader loader]
    material[Macroquad Material]
    effect[Runtime effect owner]
    fallback[Fallback shape if missing]

    manifest --> loader
    sources --> loader
    loader --> material
    material --> effect
    fallback --> effect
```

Missing shader materials should degrade gracefully. A visible fallback is better than a crash or invisible gameplay signal.

## Modal Modes

Some runtime modes pause or suppress world labels/effects to keep UI readable.

```mermaid
stateDiagram-v2
    Playing --> LevelUp
    Playing --> Paused
    Playing --> Inventory
    Playing --> DeathTransition
    Playing --> GameOver
    Playing --> Victory

    note right of LevelUp
      simulation paused
      modal panel owns focus
    end note
```

When adding world-space labels, damage numbers, or banter, check how they behave under modal overlays.

## Rendering Change Checklist

- Is the draw call world-space or screen-space?
- Does it need pixel snapping?
- Does it respect current runtime mode?
- Does it have data-driven colors/tuning where practical?
- Does a missing asset/shader have a fallback?
- Does any new runtime asset ship in `data.pak`?
- Did you smoke-test with `cargo run` if behavior changed?
