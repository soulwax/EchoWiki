# 4. Data And Modding Flow

EchoWarrior is designed so a large amount of behavior can change without recompiling Rust.

## Content Sources

```mermaid
flowchart TB
    toml[Assets/Data/*.toml]
    yaml[Assets/Dialogue/*.yaml]
    lua[Assets/Scripts/*.lua]
    shaders[shaders/*.frag / *.vert]
    metadata[Assets/Metadata/*.toml]
    mods[Mods/<mod_id>/Assets/...]

    toml --> loaders[src/data]
    yaml --> dialogue[src/game/dialogue_loader.rs]
    lua --> scripting[src/scripting]
    shaders --> runtime_assets[src/runtime/assets.rs]
    metadata --> assets[src/assets.rs]
    mods --> assetpack[src/asset_pack read overlay]
```

## Loader Contract

Data loaders should:

- parse serde structs from TOML/YAML
- provide defaults for missing optional fields
- degrade gracefully on missing or malformed files
- keep content values out of runtime code when practical
- expose enough structure for `mod_check` to validate references

## TOML Flow

```mermaid
sequenceDiagram
    participant File as Assets/Data/*.toml
    participant Pack as asset_pack::read_to_string
    participant Loader as src/data loader
    participant Runtime as PrototypeRuntime
    participant Tool as mod_check

    File->>Pack: loose or packed read
    Pack->>Loader: text
    Loader->>Runtime: config structs and defaults
    Tool->>Loader: same structs for validation
```

This shared loader path is important: tools should validate the same shapes the runtime consumes.

## Lua Flow

Lua scripts do not directly mutate arbitrary runtime state. They return commands.

```mermaid
flowchart LR
    lua[Lua hook or spawn_wave]
    ctx[read-only context snapshot]
    commands[GameCommand buffer]
    runtime[Runtime command application]
    world[Live run state]

    ctx --> lua
    lua --> commands
    commands --> runtime
    runtime --> world
```

This keeps Rust in charge of invariants while still letting mods add behavior.

## Dialogue Flow

```mermaid
flowchart TB
    yaml[Assets/Dialogue/npc.yaml]
    watcher[ScriptWatcher hot reload]
    script[NpcScript]
    dialogue[DialogueScript runner]
    runtime[Runtime dialogue UI]
    commands[optional play_sequence / sfx]

    yaml --> watcher
    watcher --> script
    script --> dialogue
    dialogue --> runtime
    dialogue --> commands
```

One NPC should have one YAML file. Dialogue may trigger choreography with `play_sequence`.

## Mod Layering

Selectable mods are declared by `Mods/<mod_id>/mod.toml`.

```mermaid
flowchart TB
    base[Vanilla Assets]
    dep[Dependency mod layer]
    selected[Selected mod layer]
    read[asset_pack::read]
    runtime[Runtime]

    base --> read
    dep --> read
    selected --> read
    read --> runtime
```

Dependency layers are collected first; selected layers override earlier layers.

## Modding Surface Checklist

When adding a new thing a modder can use:

```mermaid
flowchart TD
    field[New data field / hook / command]
    model[Serde model and defaults]
    load[Graceful loader]
    apply[Runtime or pure application]
    validate[mod_check validation]
    docs[Docs/MODDING.md]
    pack[asset_pack discovery]

    field --> model --> load --> apply
    apply --> validate
    apply --> docs
    apply --> pack
```

If any box is missing, the surface is probably not ready.
