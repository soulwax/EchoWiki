---
title: "Runtime Data Command Pipeline"
---

This page follows one important idea through the system: authored data becomes typed Rust state, typed state creates commands/events, and the runtime applies only the effects it owns.

The pipeline matters because it is where moddability stays powerful without letting every content path mutate the game in a different way.

## Whole Pipeline

```mermaid
flowchart TB
    author[Author edits TOML / YAML / Lua]
    assetread[asset_pack read layer]
    parse[serde or Lua parse]
    defaults[defaults and fallback values]
    cache[runtime/data cache]
    tick[frame update]
    commands[GameCommand buffer]
    apply[apply_game_command]
    events[GameEvent journal]
    scripts[script event hooks]
    choreo[choreography event input]
    save[save/autosave]
    draw[draw finished state]

    author --> assetread --> parse --> defaults --> cache --> tick
    tick --> commands --> apply
    apply --> events
    events --> scripts --> commands
    events --> choreo --> commands
    apply --> save
    apply --> draw
```

There are loops here on purpose. A player hit can emit a `GameEvent`, Lua can react to that event, Lua can return a `GameCommand`, and the runtime can apply that command in the same shared place.

## Source Families

```mermaid
flowchart LR
    data[Assets/Data/*.toml]
    dialogue[Assets/Dialogue/*.yaml]
    scripts[Assets/Scripts/*.lua]
    scenes[Assets/Data/scenes/*.toml]
    mods[Mods/<id>/...]
    loaders[src/data loaders]
    scriptengine[src/scripting]
    choreography[src/game/choreography]
    runtime[PrototypeRuntime]

    data --> loaders
    dialogue --> loaders
    scenes --> choreography
    scripts --> scriptengine
    mods --> loaders
    mods --> scriptengine
    mods --> choreography
    loaders --> runtime
    scriptengine --> runtime
    choreography --> runtime
```

The runtime should not care whether ordinary content came from vanilla loose files, active mods, or `data.pak`. That decision is hidden behind `asset_pack::read()` and `asset_pack::read_to_string()`.

## Data Loader Shape

Most `src/data/mod_data.rs` loaders follow the same failure-tolerant shape:

```mermaid
flowchart TD
    loadCall[load_x_from path]
    read["asset_pack::read_to_string"]
    readok{"read ok?"}
    parse["toml/serde parse"]
    parseok{"parse ok?"}
    validate[light local normalization]
    loaded[return loaded config]
    warn1[print cannot read]
    warn2[print parse error]
    fallback["return default/fallback"]

    loadCall --> read --> readok
    readok -- yes --> parse --> parseok
    readok -- no --> warn1 --> fallback
    parseok -- yes --> validate --> loaded
    parseok -- no --> warn2 --> fallback
```

This is the graceful-degradation contract. Runtime content can be broken while a contributor is iterating, but the game should usually continue with a known fallback rather than crashing in an unrelated system.

## Lua Command Path

Lua is powerful, but the script engine still translates Lua tables into typed command variants before runtime application.

```mermaid
sequenceDiagram
    participant Runtime as PrototypeRuntime
    participant Scripts as ScriptEngine
    participant Lua as Lua callback
    participant Parser as script_command_from_table
    participant Apply as apply_game_command

    Runtime->>Scripts: call_event(event, ctx)
    Scripts->>Lua: callback(ctx)
    Lua-->>Scripts: table or list of tables
    Scripts->>Parser: parse cmd / command / legacy spawn fields
    Parser-->>Scripts: Vec<GameCommand>
    Scripts-->>Runtime: commands
    Runtime->>Apply: apply each command
```

`spawn_wave(ctx)` is narrower: it only executes spawn commands today. Generic event hooks can return the broader shared command vocabulary.

## Command Vocabulary

```mermaid
flowchart TB
    command[GameCommand]
    spawn[spawn_enemy]
    stat[modify_stat]
    xp[grant_xp]
    hp[heal / damage]
    status[apply_status]
    flag[set_flag]
    dialogue[queue_dialogue]
    sfx[play_sfx]
    weather[set_weather]
    fx[spawn_fx]
    sequence[play_sequence]

    command --> spawn
    command --> stat
    command --> xp
    command --> hp
    command --> status
    command --> flag
    command --> dialogue
    command --> sfx
    command --> weather
    command --> fx
    command --> sequence
```

`src/game/commands.rs` is renderer-agnostic. The type is intentionally broader than what every context can execute.

## Context Support Matrix

| Command | Runtime applies today | Pure run simulation applies today | Notes |
| --- | --- | --- | --- |
| `spawn_enemy` | yes | needs runtime | runtime owns live enemy actors |
| `modify_stat` | yes | yes | limited to `PLAYER_STAT_KEYS` |
| `grant_xp` | yes | yes | may emit level-up events |
| `heal` / `damage` | player target | player target | non-player targets need more runtime support |
| `apply_status` | typed command exists | needs runtime | currently validated more than applied |
| `set_flag` | yes | needs runtime | stored in choreography flag state |
| `queue_dialogue` | yes | needs runtime | full or mini dialogue |
| `play_sfx` | yes | needs runtime | audio handle lives in runtime |
| `set_weather` | yes | needs runtime | loads weather preset and updates weather/audio |
| `spawn_fx` | command exists in choreography output | needs runtime | world visual effect request |
| `play_sequence` | yes | needs runtime | routes to choreography request queue |

This table explains a recurring contributor decision: if a command affects pure player math, it may belong in `run_sim`. If it touches actors, audio, weather, dialogue, or visuals, runtime remains the owner.

## Event Feedback Loop

```mermaid
flowchart TD
    sim[player/enemy/runtime action]
    emit[emit_game_event]
    journal[run event journal]
    scripting[Lua event hook]
    choreo[choreography event mapper]
    commands[commands]
    apply[apply_game_command]
    moreevents[optional follow-up events]

    sim --> emit --> journal
    journal --> scripting --> commands
    journal --> choreo --> commands
    commands --> apply --> moreevents
    moreevents --> emit
```

Examples:

- enemy death emits `EnemyDied`, then Lua may grant XP or start a sequence
- player damage emits `PlayerDamaged`, then Lua may heal, play SFX, or set a flag
- level-up availability emits an event, then the runtime opens the level-up mode
- queueing dialogue emits `DialogueQueued`, then UI presentation reads the resulting state

## Choreography Command Path

```mermaid
sequenceDiagram
    participant RT as Runtime
    participant Engine as Choreography engine
    participant Snapshot as Read-only snapshot
    participant Intents as Pose move intents
    participant Commands as GameCommand output

    RT->>Snapshot: capture actors, flags, events, time
    RT->>Engine: update(snapshot)
    Engine-->>Intents: actor pose / movement intents
    Engine-->>Commands: world/state commands
    RT->>RT: apply intents to live actors
    RT->>RT: apply_game_command for commands
```

The choreography engine does not mutate the world directly. That is why authored scenes, Lua, and runtime systems can converge through one command application boundary.

## Validation Before Runtime

```mermaid
flowchart LR
    toml[TOML command tables]
    lua[Lua files]
    refs[known ids from data]
    modcheck[mod_check]
    errors[errors]
    warnings[warnings]
    runtime[launch runtime]

    toml --> modcheck
    lua --> modcheck
    refs --> modcheck
    modcheck --> errors
    modcheck --> warnings
    modcheck --> runtime
```

`mod_check` validates command payloads and cross-references before launch. It checks things like unknown enemy ids, unknown SFX ids, unknown weather presets, invalid player stat keys, non-finite numbers, and malformed Lua.

Runtime loaders still need fallbacks because development and modding are dynamic, but `mod_check` is the contributor gate that catches preventable content mistakes early.

## Adding A New Command

```mermaid
flowchart TD
    idea[new scriptable effect]
    pure{pure player/run math?}
    command[add GameCommand variant]
    serde[derive serde fields and defaults]
    runtime[apply in PrototypeRuntime]
    runsim[apply in run_sim if pure]
    lua[parse Lua table form]
    modcheck[validate command payload and refs]
    docs[document command]
    tests[add pure/parser tests]

    idea --> pure --> command --> serde --> runtime
    pure -- yes --> runsim
    command --> lua
    command --> modcheck
    command --> docs
    command --> tests
```

Do not add a command only to Lua, only to choreography, or only to upgrades if it is meant to be a shared gameplay verb. Add it to the shared command model, then teach each source how to produce it and each applicable runtime/pure context how to apply it.

## Debugging The Pipeline

```mermaid
flowchart TD
    bug[behavior missing]
    content{content loaded?}
    parse{schema parsed?}
    command{command emitted?}
    apply{runtime applies it?}
    mode{mode allows effect?}
    draw{draw reads resulting state?}

    bug --> content
    content -- no --> readpath[check asset read order and pack discovery]
    content -- yes --> parse
    parse -- no --> loader[check serde defaults and loader warning]
    parse -- yes --> command
    command -- no --> source[check Lua/choreography/event trigger]
    command -- yes --> apply
    apply -- no --> support[check apply_game_command support]
    apply -- yes --> mode
    mode -- no --> gate[check RuntimeMode gate]
    mode -- yes --> draw
    draw -- no --> visual[check draw layer/camera/UI]
```

This graph is usually faster than searching randomly. Follow the bytes, then the typed data, then the command, then the mode gate, then the draw path.
