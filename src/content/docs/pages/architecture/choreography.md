---
title: "6. Choreography"
---

Choreography is the single architecture path for authored beats: story staging, movement, gestures, camera nudges, dialogue-triggered moments, and small expressive actions.

Do not create a parallel scene or beat system.

<figure class="wide-figure">
  <img src="/dialogue_1.png" alt="Rainy gameplay scene with dialogue overlay, speaker portrait, and continuation prompt" />
  <figcaption>A scene beat in context: gameplay keeps its world state, while choreography and dialogue temporarily own presentation and input focus.</figcaption>
</figure>

## Concept Model

```mermaid
flowchart TB
    sequence[Sequence]
    trigger[Trigger]
    steps[Ordered steps]
    beats[Parallel beats inside a step]
    intents[BeatIntent values]
    runtime[Runtime apply layer]
    commands[GameCommand values]

    trigger --> sequence
    sequence --> steps
    steps --> beats
    beats --> intents
    intents --> runtime
    beats --> commands
    commands --> runtime
```

In plain language:

- a trigger starts a sequence
- a sequence runs steps in order
- each step can contain beats that happen together
- pure code produces intents
- runtime code applies those intents to live actors, camera, dialogue, or commands

## Pure Engine And Runtime Apply Layer

```mermaid
flowchart LR
    data[Assets/Data/choreography.toml<br/>Assets/Data/scenes/*.toml]
    engine[src/game/choreography.rs<br/>pure state machine]
    intents[BeatIntent]
    commands[GameCommand]
    apply[src/runtime/choreography.rs]
    world[Live actors, camera, state]

    data --> engine
    engine --> intents
    engine --> commands
    intents --> apply
    commands --> apply
    apply --> world
```

The split matters. The engine can be validated and previewed without Macroquad. The runtime decides how those intents affect textures, positions, camera, and live state.

## Scene Projects

Scene files live under:

```text
Assets/Data/scenes/*.toml
```

Each scene can declare sequences. Scene-qualified ids allow larger story arcs to chain across files.

```mermaid
flowchart LR
    sceneA[vale_meeting.toml]
    seqA[vale_meeting:intro]
    seqB[vale_meeting:depart]
    sceneB[vale_departure.toml]
    seqC[vale_departure:arrive]

    sceneA --> seqA --> seqB
    seqB --> sceneB --> seqC
```

## Invocation Sources

Sequences can start from multiple places:

```mermaid
flowchart TB
    time[time/mode trigger]
    event[game event trigger]
    dialogue[dialogue play_sequence]
    lua[Lua echo_warrior.play_sequence]
    chain[on_sequence_finished]
    engine[choreography engine]

    time --> engine
    event --> engine
    dialogue --> engine
    lua --> engine
    chain --> engine
```

This lets content authors connect story, combat, and tiny motion beats without new Rust verbs.

## Tooling

`src/bin/choreo.rs` is the contract CLI:

```mermaid
flowchart LR
    toml[TOML scenes]
    validate[choreo validate]
    convert[choreo convert]
    schema[choreo schema]
    preview[choreo preview]
    graph[choreo graph]
    gui[future authoring tools]

    toml --> validate
    toml --> convert
    toml --> preview
    toml --> graph
    schema --> gui
    convert --> gui
    preview --> gui
    graph --> gui
```

Useful commands:

```powershell
cargo run --bin choreo -- validate Assets/Data/scenes
cargo run --bin choreo -- schema --out choreography.schema.json
cargo run --bin choreo -- preview Assets/Data/scenes/example_scene.toml intro
cargo run --bin choreo -- graph Assets/Data/scenes --json
```

## Change Rule

If you need a new authored beat:

1. add it to the choreography schema/model
2. make the pure engine emit an intent or `GameCommand`
3. make the runtime apply layer handle it
4. validate it in `choreo` and `mod_check`
5. document it for modders

Do not wire a one-off cue directly into runtime unless it is truly runtime-only and not authored content.
