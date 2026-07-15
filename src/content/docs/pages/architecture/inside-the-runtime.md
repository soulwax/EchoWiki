---
title: "Inside The Runtime"
---

This page is the slower, deeper walkthrough of how EchoWarrior actually runs from the inside.

Read this after [Runtime Loop](runtime-loop/) if you want to touch gameplay, input, scenes, audio, effects, or anything that happens once the window is open.

For the deeper data/event side of the same flow, continue with [Runtime Data Command Pipeline](runtime-data-command-pipeline/).

## Boot To Frame

The executable starts small:

```mermaid
sequenceDiagram
    participant Main as main entry
    participant Runtime as runtime module
    participant Pack as asset pack module
    participant Data as data loaders
    participant Loader as runtime assets
    participant Game as PrototypeRuntime
    participant Shell as selected runtime shell
    participant Vk as vk2d when --vk

    Main->>Runtime: select --vk shell or compatibility loop
    Runtime->>Runtime: init tracing + F1 ring buffer
    Runtime->>Pack: configure selected mod layers
    Runtime->>Data: load characters, voices, music, settings
    Runtime->>Loader: frame-driven asset loading
    Loader->>Pack: read loose/mod/packed assets
    Runtime->>Game: construct PrototypeRuntime
    loop every frame
        Shell->>Runtime: input + delta
        Runtime->>Game: handle_input()
        Runtime->>Game: update(delta)
        Runtime->>Game: draw()
        Runtime->>Shell: present selected backend
    end
```

`src/main.rs` selects the winit/vk2d shell for `--vk` and retains the
Macroquad loop as a compatibility path. If startup fails, the selected shell
reports the error. The shared application logic lives in `src/runtime`.

## Startup Phases

Startup is deliberately staged. The active renderer loader registers the
resources it can support, performs one load phase, presents again, then
continues. The Macroquad loader and `vk_assets` loader share the asset lookup
contract but create backend-specific handles.

```mermaid
flowchart TD
    start[run starts]
    logging[init logging]
    prefs[load start preferences]
    mods{play_modded?}
    layers[selected_mod_layers]
    settings[load settings]
    intro{studio intro enabled?}
    loader[AssetLoader or vk_assets phases]
    preload[StartupPreload]
    runtime[PrototypeRuntime::new]
    frame[enter frame loop]

    start --> logging --> prefs --> mods
    mods -- yes --> layers --> settings
    mods -- no --> settings
    settings --> intro
    intro --> loader
    loader --> preload --> runtime --> frame
```

At this point the runtime has already chosen the active mod layers and called `asset_pack::set_active_mod_layers()`. That matters because later data loaders use the same asset read gateway whether the bytes come from a mod, a loose development file, or `data.pak`.

## Runtime Ownership

`PrototypeRuntime` is still the live owner of the playable prototype. It owns player state, enemies, NPCs, effects, cameras, weather, dialogue, settings, saves, the choreography adapter, and the immediate draw paths.

That does not mean all rules should stay there.

```mermaid
flowchart TB
    runtime[PrototypeRuntime]
    player[player/enemies/NPC runtime structs]
    draw[draw intent and backend handles]
    audio[runtime audio handles]
    scripts[Lua runtime bridge]
    choreo[runtime choreography adapter]
    pure[src/game pure rules]
    data[src/data loaders]
    ui[src/ui view/layout models]
    save[src/save account/run files]

    runtime --> player
    runtime --> draw
    runtime --> audio
    runtime --> scripts
    runtime --> choreo
    runtime --> pure
    runtime --> data
    runtime --> ui
    runtime --> save
```

Use this rule of thumb:

| Work | Likely owner |
| --- | --- |
| texture handles, render targets, shader uniforms | `src/runtime` |
| input interpretation and mode gates | `src/runtime` |
| deterministic combat math | `src/game` |
| TOML/YAML schema and fallback loading | `src/data` |
| Lua command buffering | `src/scripting` plus runtime application |
| UI layout models and theme data | `src/ui` |
| save/account persistence | `src/save` |

## The Update Gate

The frame update is mode-gated. Some systems tick in every mode, some tick only on the start screen or arena, and most gameplay simulation only advances in `RuntimeMode::Playing`.

```mermaid
flowchart TD
    update[PrototypeRuntime::update]
    always[always: hot reload, mini-dialogue, settings persist, audio gain, music, fade]
    paused{Paused?}
    start{StartScreen?}
    transition{StartTransition?}
    arena{Arena?}
    scripted[scripted modes: intro/dialogue/choreography/weather]
    terminal{Death/GameOver/Victory/LevelUp?}
    playing{Playing?}
    sim[full gameplay simulation]
    autosave[autosave]

    update --> always --> paused
    paused -- yes --> stop1[weather audio only, return]
    paused -- no --> start
    start -- yes --> starttick[start ambience + lantern + weather, return]
    start -- no --> transition
    transition -- yes --> starttrans[start transition, return]
    transition -- no --> arena
    arena -- yes --> arenasim[arena sandbox update, return]
    arena -- no --> scripted --> terminal
    terminal -- yes --> terminaltick[timers/fades/death transition, return]
    terminal -- no --> playing
    playing -- no --> stop2[return]
    playing -- yes --> sim --> autosave
```

This is why contributors should be careful with "just update it every frame" changes. A system that advances during pause, level-up, death transition, or intro can break save state, animation timing, or player expectations.

## Playing Simulation Order

In `Playing`, the runtime applies a recognizable order:

```mermaid
sequenceDiagram
    participant RT as PrototypeRuntime
    participant Choreo as Choreography
    participant Director as Director
    participant Actors as Runtime actors
    participant Grid as Enemy grid
    participant Combat as Combat update helpers
    participant ECS as ECS lifecycle bridge
    participant Save as Autosave

    RT->>RT: stress benchmark tick
    RT->>RT: hitstop scales gameplay delta
    RT->>Choreo: update authored beats
    RT->>Director: update spawn/story director
    RT->>Actors: move NPCs, companions, player
    RT->>Actors: spawn and update enemies
    RT->>Grid: rebuild spatial grid
    RT->>Combat: attacks, abilities, XP, effects
    RT->>ECS: batch sync enemy dynamic state
    RT->>Actors: cull dead enemies
    RT->>Save: update autosave timer
```

The exact function list is long because the prototype is still live and feature-rich. The architectural point is simpler: input and timers happen before gameplay, gameplay mutates live actor state, ECS mirrors selected state, and drawing reads the finished frame state.

The enemy ECS mirror is not a per-enemy full rewrite. During ordinary frames, the runtime collects a reusable batch of `(EntityId, EnemyDynamicState)` pairs and lets `EcsLifecycleBridge` update `Transform`, `Motion`, and `Health` in component passes. See [ECS Lifecycle Hot Lane](ecs-lifecycle-hot-lane/) for the deeper contract.

## Commands Are The Runtime Boundary

Lua, choreography, dialogue, and some data-driven systems do not directly mutate every runtime field. They emit `GameCommand` values. The runtime applies those in `PrototypeRuntime::apply_game_command()`.

```mermaid
flowchart LR
    lua[Lua scripts]
    choreo[choreography steps]
    dialogue[dialogue/scene data]
    command[GameCommand]
    runtime[apply_game_command]
    state[player/enemies/world flags/weather/audio/dialogue]

    lua --> command
    choreo --> command
    dialogue --> command
    command --> runtime --> state
```

Current command effects include spawning enemies, changing player stats, granting XP, healing/damaging the player, queueing dialogue, playing SFX, setting story flags, starting choreography sequences, and changing weather presets.

When adding a new scriptable effect, prefer extending `GameCommand` and applying it in one place instead of giving each authoring path its own side effect.

## Asset Reads During Runtime

Most runtime content flows through `asset_pack::read()` or `asset_pack::read_to_string()`.

```mermaid
flowchart TD
    request[path requested]
    modlayer{active mod layer?}
    loose{loose file exists?}
    pack{data.pak entry?}
    ok[bytes returned]
    miss[loader fallback or error]

    request --> modlayer
    modlayer -- yes --> ok
    modlayer -- no --> loose
    loose -- yes --> ok
    loose -- no --> pack
    pack -- yes --> ok
    pack -- no --> miss
```

This is what lets a contributor run from loose files during development while release builds run from a pack. It is also what lets mods override ordinary content.

Canonical identity media is different. It uses `asset_pack::read_identity()`, which exists specifically to bypass the normal mod/loose replacement chain in release builds.

## Drawing Reads Finished State

Drawing happens after update. The runtime draws world-space layers first, then effects, then overlays and UI.

```mermaid
flowchart TB
    state[finished frame state]
    camera[camera transform]
    ground[ground and props]
    actors[player, enemies, NPCs]
    fx[attacks, sparks, glow, bloom]
    weather[weather and tint]
    hud[HUD, dialogue, panels]
    debug[F1 debug overlay]

    state --> camera --> ground --> actors --> fx --> weather --> hud --> debug
```

If a visual change needs simulation data, compute the data during update and let draw read it. Avoid draw-time gameplay mutations; they are hard to test and can behave differently when frame pacing changes.

## Practical Contributor Route

When you need to understand an unfamiliar feature from the inside:

1. Find the data owner in `Assets/Data`, `Assets/Dialogue`, `Assets/Scripts`, or `Assets/Metadata`.
2. Find the loader in `src/data` or the direct runtime load site.
3. Find the runtime owner in `PrototypeRuntime`.
4. Check whether a pure helper already exists in `src/game`.
5. Check whether the feature emits or applies `GameCommand`.
6. Check whether assets need release discovery in `src/asset_pack.rs`.
7. Run a targeted verification command.

The healthy direction is not "move everything out of runtime immediately." The healthy direction is to make each new slice cleaner than the last: data-driven where practical, pure where useful, runtime-bound only where rendering/input/audio genuinely require it.
