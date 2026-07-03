---
title: "8. Commands And Events"
---

EchoWarrior uses shared command and event shapes to keep data-authored behavior from reaching directly into live runtime internals.

The short version:

- commands ask the runtime to do something
- events describe what happened
- the runtime owns invariants when applying either one

## Command Sources

```mermaid
flowchart TB
    lua[Lua scripts and hooks]
    choreo[Choreography beats]
    dialogue[Dialogue lines]
    upgrades[Upgrade/item command lists]
    tools[mod_check validation]
    commands[GameCommand]
    runtime[Runtime command application]
    world[Live run state]

    lua --> commands
    choreo --> commands
    dialogue --> commands
    upgrades --> commands
    commands --> runtime --> world
    commands --> tools
```

The shared command model lets authoring surfaces reuse a small vocabulary instead of inventing one-off runtime calls.

## Why Commands Exist

Commands protect these boundaries:

| Boundary | Why it matters |
| --- | --- |
| Lua to Rust | scripts request behavior, Rust enforces invariants |
| Choreography to runtime | authored scenes stay data-driven |
| Upgrades/items to player state | modded content can reuse stat/effect verbs |
| Tools to content | `mod_check` can validate command payloads before launch |

## Typical Command Flow

```mermaid
sequenceDiagram
    participant Source as Lua / Choreography / Data
    participant Command as GameCommand
    participant Runtime as PrototypeRuntime
    participant Systems as Runtime systems
    participant Journal as Run event journal

    Source->>Command: produce command payload
    Command->>Runtime: queued/applied at safe boundary
    Runtime->>Systems: spawn, heal, damage, dialogue, sfx, flags
    Systems->>Journal: emit structured event when relevant
```

## Event Flow

Events are structured facts about a run: enemy killed, player hit, level-up offer, upgrade picked, mode changed, and similar moments.

```mermaid
flowchart LR
    runtime[Runtime systems]
    pure[run_sim pure kernel]
    journal[run_events journal]
    debug[F1/debug feed]
    lua[Lua hook context]
    future[analytics/replay/tooling]

    runtime --> journal
    pure --> journal
    journal --> debug
    journal --> lua
    journal --> future
```

The same event vocabulary should be useful to tests, debug UI, scripts, and future tooling.

## Command Validation

`mod_check` walks TOML command tables and tries to deserialize them as `GameCommand`.

```mermaid
flowchart TD
    toml[Data TOML]
    find[Find command tables]
    deserialize[Deserialize GameCommand]
    refs[Check references and ranges]
    report[Human-readable diagnostics]

    toml --> find --> deserialize --> refs --> report
```

That means adding a new command should usually include:

- data shape
- runtime application
- validation rules
- modding docs
- tests where practical

## Safe Extension Rule

If a new data/Lua/choreography feature needs to affect the world, first ask:

> Can this be a `GameCommand` or event instead of a direct runtime special case?

Often the answer is yes, and the resulting feature becomes easier to validate, test, and author.
