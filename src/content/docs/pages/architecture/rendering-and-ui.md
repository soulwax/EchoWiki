---
title: "10. Rendering And UI"
---

Rendering is the clearest place where EchoWarrior must keep boundaries tidy: world simulation, world rendering, post-processing, and screen-space UI all happen in one frame, but they do different jobs.

<figure class="wide-figure">
  <img src="/shader_arena_1.png" alt="Shader arena with a nova preview, runtime HUD, VFX icon bar, and egui controls" />
  <figcaption>The shader arena makes the rendering/UI split visible: world-space effects, HUD, icon rows, and tuning panels all share a frame but belong to different layers.</figcaption>
</figure>

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

## Renderer Boundary

The game-facing draw contract is neutral, but its architectural destination is no longer undecided: [`soulwax/vk2d`](https://github.com/soulwax/vk2d) is the canonical 2D renderer. The Macroquad adapter remains because old paths still need a compatibility implementation while the route is completed.

```mermaid
flowchart LR
    feature[Runtime feature module]
    neutral[src/render.rs<br/>Renderer2d verbs]
    backend[src/runtime/renderer_backend.rs<br/>backend switch]
    mq[src/runtime/renderer_mq.rs<br/>compatibility adapter]
    vk[src/runtime/renderer_vk.rs<br/>VkRenderer recorder]
    crate[crates/vk2d<br/>canonical renderer submodule]
    probe[src/bin/wgpu_probe.rs<br/>consumer smoke surface]

    feature --> neutral
    neutral --> backend
    backend --> mq
    backend --> vk --> crate
    probe --> crate
```

For contributors, the practical rule is simple: new renderer slices should move draw intent toward `Renderer2d` verbs such as rectangles, sprites, text, lines, circles, targets, and materials. Gameplay and UI model code should not learn about `wgpu`, `winit`, or Macroquad resource types. When the verb is insufficient, extend `vk2d` first and then adapt the contract.

For the current target/view/bloom routing, read [vk2d Runtime Usage](vk2d-runtime-usage/). For the renderer crate internals, read [vk2d Renderer Internals](vk2d-renderer-internals/).

## Shader And VFX Flow

```mermaid
flowchart TD
    manifest[Assets/Data/shaders.toml]
    sources[shader source files]
    loader[backend-specific asset loader]
    material[vk2d MaterialId or compatibility material]
    effect[Runtime effect owner]
    fallback[Fallback shape if missing]

    manifest --> loader
    sources --> loader
    loader --> material
    material --> effect
    fallback --> effect
```

`vk2d` is the canonical material path and loads WGSL through its own API. Macroquad GLSL materials remain for compatibility, so shader work now has two important contracts:

- gameplay and UI choose *what* effect should be drawn
- the backend chooses *how* that material is loaded and presented

Missing shader materials should degrade gracefully. A visible fallback is better than a crash or invisible gameplay signal.

## Vulkan-Oriented Probe Path

`src/bin/wgpu_probe.rs` is a focused consumer smoke surface for Vulkan-facing renderer work. The canonical runtime surface is the winit/vk2d shell selected with `--vk`; the probe remains useful because it isolates library and material issues from game-state complexity.

```mermaid
flowchart TD
    shell[--vk runtime shell]
    probe[wgpu_probe consumer]
    consumer[src/wgpu_vulkan app glue]
    crate[crates/vk2d canonical library]
    gpu[wgpu backend]
    shader[WGSL material text]
    assets[raw texture/font bytes]

    shell --> consumer --> crate --> gpu
    probe --> crate
    shader --> crate
    assets --> crate
```

Use the probe for renderer library checks:

```powershell
cargo test -p vk2d
cargo run -p vk2d --example hello_sprite -- --frames 3
cargo run --bin wgpu_probe -- --frames 3
```

Use the game for integration checks:

```powershell
cargo run
```

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
- Can the draw intent go through `Renderer2d` instead of raw Macroquad calls?
- Does it have data-driven colors/tuning where practical?
- Does a missing asset/shader have a fallback?
- Does any new runtime asset ship in `data.pak`?
- Did you smoke-test with `cargo run` if behavior changed?
