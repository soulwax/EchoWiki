---
title: "18. Migration Status"
---

EchoWarrior is intentionally evolving from a playable prototype toward cleaner pure systems. This page describes the current seams so contributors know what is stable and what is transitional.

## Migration Map

```mermaid
flowchart LR
    runtime[Runtime-owned prototype state]
    bridged[Bridged systems]
    pure[Pure reusable systems]
    tools[Tooling contracts]

    runtime --> bridged --> pure --> tools
```

The goal is not to erase runtime. The goal is to keep runtime focused on rendering/input/audio/application while pure code owns rules and validation-friendly models.

## Current Buckets

| Area | Status | Notes |
| --- | --- | --- |
| enemy/player/NPC live actors | runtime-owned | Drawing and per-frame Macroquad state still live in runtime actors. |
| enemy ECS lifecycle | bridged | Spawn/despawn/restore mirror through `EcsLifecycleBridge`; ordinary frames use batched dynamic sync for `Transform`, `Motion`, and `Health`. |
| run level / XP curve | mostly pure | Runtime delegates more arithmetic to shared run-level/run-sim code. |
| level-up offers | pure | Offer director is deterministic and testable. |
| dialogue model/loading | split | YAML loading is pure-ish; runtime owns presentation. |
| Lua hooks | split | Lua returns commands; runtime applies them. |
| choreography | split by design | Pure engine emits intents; runtime apply layer moves actors/camera/state. |
| rendering/VFX/audio | runtime-owned | Should remain Macroquad-side, with data-driven manifests. |
| saves/progression | shared | Save models are library-side; runtime triggers writes/restores. |
| mod validation | tooling | `mod_check` is the shipping gate for content references. |

## Transitional Pattern

```mermaid
sequenceDiagram
    participant Runtime as Runtime owner
    participant Bridge as Narrow bridge
    participant Pure as Pure model system
    participant Tests as Tests and tools

    Runtime->>Bridge: expose minimal state
    Bridge->>Pure: update/query pure model
    Pure->>Tests: can be tested without window
    Pure->>Runtime: return result/intent/command
```

If you are migrating a behavior, prefer this pattern over moving entire runtime files.

## Stable Direction

Stable architectural direction:

- more validation in tools
- more rules in `src/game`
- more content in `Assets/`
- more authoring through choreography/commands
- runtime focused on application, drawing, audio, input, and Macroquad integration

Not stable yet:

- final ECS ownership model beyond the current lifecycle bridge hot/cold lanes
- final UI architecture
- final scene/prop authoring model
- final inventory/skill-tree UI shape
- future GUI authoring workflows

## Contributor Advice

When touching transitional code:

1. preserve behavior first
2. identify the smallest pure rule to extract
3. keep adapter code close to current runtime owner
4. add tests around the pure piece
5. avoid creating new parallel ownership models
