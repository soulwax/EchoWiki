---
title: "Architecture Chapter"
---

This chapter explains EchoWarrior from the outside in. Start with the big picture, then move down through module boundaries, runtime flow, data loading, release packaging, choreography, and extension patterns.

The goal is not to memorize every file. The goal is to know where a change belongs and what contracts it must preserve.

## Chapter Path

```mermaid
flowchart TD
    basics[Basics]
    runtime[Runtime internals]
    data[Data and commands]
    packs[Assets, packs, protection]
    systems[Gameplay systems]
    quality[Quality and evolution]

    basics --> runtime --> data --> packs --> systems --> quality
```

1. [Fundamentals](fundamentals/): the shortest possible architecture map.
2. [Module Boundaries](module-boundaries/): which folder owns which kind of work.
3. [Runtime Loop](runtime-loop/): how the Macroquad prototype advances a frame.
3A. [Inside The Runtime](inside-the-runtime/): the deeper boot, mode, update, command, and draw flow.
3B. [Runtime Data Command Pipeline](runtime-data-command-pipeline/): how data, Lua, choreography, events, and commands converge.
4. [Data And Modding Flow](data-and-modding-flow/): how TOML, YAML, and Lua become game behavior.
5. [Assets And Release Packs](assets-and-release-packs/): why loose files and `data.pak` both matter.
5A. [Protection And Tamper Boundaries](protection-and-tamper-boundaries/): what the game protects, what remains moddable, and why this is not DRM.
5B. [Pack Integrity Deep Dive](pack-integrity-deep-dive/): the pack format, key resolution, verification checks, and failure paths.
6. [Choreography](choreography/): the single authored-beat engine.
7. [Extension Patterns](extension-patterns/): where to add new behavior safely.
8. [Commands And Events](commands-and-events/): how scripts, scenes, upgrades, runtime, and logs communicate.
9. [Simulation And ECS](simulation-and-ecs/): how pure run logic and the ECS bridge coexist with runtime actors.
9A. [ECS Lifecycle Hot Lane](ecs-lifecycle-hot-lane/): how the runtime mirrors enemy state through cold full sync and batched dynamic sync.
10. [Rendering And UI](rendering-and-ui/): how world rendering, effects, post-processing, and UI layers stack.
10A. [Vulkan Renderer Path](vulkan-renderer-path/): how `Renderer2d`, Macroquad, `wgpu_probe`, and `soulwax/vk2d` fit together.
11. [Persistence And State](persistence-and-state/): how saves, settings, progression, and mod metadata are separated.
12. [Verification Architecture](verification-architecture/): how checks map to code and content boundaries.
13. [Graceful Degradation](graceful-degradation/): how missing or broken content should fail without taking down the game.
14. [Performance And Observability](performance-and-observability/): how contributors find slow or noisy paths.
15. [Feature Slice Walkthrough](feature-slice-walkthrough/): how a new capability crosses data, runtime, tools, docs, and release packaging.
16. [Design Principles](design-principles/): how to choose between valid approaches.
17. [Architecture Glossary](glossary/): shared terms used across the wiki and codebase.
18. [Migration Status](migration-status/): what is already pure, what is bridged, and what is still runtime-owned.
19. [Anti-Patterns](anti-patterns/): common moves that fight the architecture.

## One-Screen Map

```mermaid
flowchart TB
    contributor[Contributor]
    assets[Assets and Mods]
    bins[src/bin tools]
    lib[src/lib shared crate]
    runtime[src/runtime Macroquad runtime]
    game[src/game pure gameplay]
    data[src/data loaders]
    ui[src/ui UI models]
    save[src/save persistence]
    script[src/scripting Lua]
    pack[data.pak / identity.pak]

    contributor --> assets
    contributor --> bins
    contributor --> lib
    lib --> game
    lib --> data
    lib --> ui
    lib --> save
    lib --> script
    runtime --> lib
    data --> assets
    script --> assets
    bins --> lib
    assets --> pack
    runtime --> pack
```

## North Star

EchoWarrior is built to keep content easy to modify while keeping core rules testable:

- content lives in `Assets/` and `Mods/` when practical
- pure rules live in `src/game`
- data schemas and fallback loading live in `src/data`
- Macroquad rendering/input/audio live in `src/runtime`
- release asset discovery lives in `src/asset_pack.rs`
- shipping confidence comes from `mod_check`, `asset_pack`, tests, and `cargo check`

## Quick Decisions

| If you are changing... | Read next |
| --- | --- |
| any code for the first time | [Fundamentals](fundamentals/) |
| where a module belongs | [Module Boundaries](module-boundaries/) |
| frame update/drawing behavior | [Runtime Loop](runtime-loop/) |
| understanding how the game really runs inside | [Inside The Runtime](inside-the-runtime/) |
| tracing data into commands and runtime effects | [Runtime Data Command Pipeline](runtime-data-command-pipeline/) |
| TOML/YAML/Lua content | [Data And Modding Flow](data-and-modding-flow/) |
| release asset inclusion | [Assets And Release Packs](assets-and-release-packs/) |
| tamper/protection boundaries | [Protection And Tamper Boundaries](protection-and-tamper-boundaries/) |
| pack format and verification mechanics | [Pack Integrity Deep Dive](pack-integrity-deep-dive/) |
| story beats, movement beats, scenes | [Choreography](choreography/) |
| adding a new capability | [Extension Patterns](extension-patterns/) |
| adding Lua/choreography/upgrades behavior | [Commands And Events](commands-and-events/) |
| touching actors, ECS, or pure run tests | [Simulation And ECS](simulation-and-ecs/) |
| changing enemy ECS frame sync or mirrored components | [ECS Lifecycle Hot Lane](ecs-lifecycle-hot-lane/) |
| changing draw order, effects, or HUD | [Rendering And UI](rendering-and-ui/) |
| moving draw calls toward the owned renderer | [Vulkan Renderer Path](vulkan-renderer-path/) |
| changing saves, settings, or account progress | [Persistence And State](persistence-and-state/) |
| deciding which checks to run | [Verification Architecture](verification-architecture/) |
| adding fallbacks or loader behavior | [Graceful Degradation](graceful-degradation/) |
| chasing frame time or logs | [Performance And Observability](performance-and-observability/) |
| planning a complete capability | [Feature Slice Walkthrough](feature-slice-walkthrough/) |
| deciding between two designs | [Design Principles](design-principles/) |
| decoding architecture vocabulary | [Architecture Glossary](glossary/) |
| understanding current migration seams | [Migration Status](migration-status/) |
| checking whether an approach is risky | [Anti-Patterns](anti-patterns/) |
