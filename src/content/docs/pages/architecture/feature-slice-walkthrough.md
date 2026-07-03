---
title: "15. Feature Slice Walkthrough"
---

This page shows how a complete capability moves through EchoWarrior's architecture.

Example: add a new data-driven upgrade that triggers a small runtime effect and can be used by mods.

## Whole Slice

```mermaid
flowchart TD
    idea[Feature idea]
    data[Assets/Data schema or entry]
    serde[src/data model and defaults]
    command[GameCommand or pure rule]
    runtime[Runtime application / effect]
    fallback[Fallback behavior]
    validate[mod_check validation]
    pack[asset_pack discovery]
    docs[Docs/MODDING.md / Wiki]
    verify[checks and smoke test]

    idea --> data --> serde --> command --> runtime
    runtime --> fallback
    runtime --> validate
    runtime --> pack
    validate --> docs
    pack --> docs
    docs --> verify
```

## Step 1: Decide Ownership

```mermaid
flowchart LR
    feature[New feature]
    content{Modder controls it?}
    pure{Can rule be pure?}
    visual{Needs rendering?}

    feature --> content
    content -- yes --> data[Assets/Data + src/data]
    content -- no --> pure
    pure -- yes --> game[src/game]
    pure -- no --> visual
    visual -- yes --> runtime[src/runtime]
```

Most good features touch more than one layer. The important part is that each layer owns the right piece.

## Step 2: Choose A Communication Shape

If the feature is triggered by data, Lua, choreography, or upgrades, prefer a shared command or event.

```mermaid
flowchart LR
    data[Data/Lua/Choreography]
    command[GameCommand]
    runtime[Apply command safely]
    event[Optional GameEvent]
    logs[Debug/log/Lua hook feed]

    data --> command --> runtime
    runtime --> event --> logs
```

## Step 3: Make It Robust

```mermaid
flowchart TD
    load[Load feature data]
    invalid{Invalid?}
    fallback[Fallback or skip]
    report[Report useful diagnostic]
    ok[Apply feature]

    load --> invalid
    invalid -- yes --> report --> fallback
    invalid -- no --> ok
```

If a modder mistypes an id, the game should tell them what broke and keep going where practical.

## Step 4: Verify The Right Boundaries

| Feature touched | Check |
| --- | --- |
| Rust model or runtime | `cargo check` |
| pure logic | targeted `cargo test` |
| TOML/YAML/Lua/mod references | `cargo run --bin mod_check` |
| new asset/shader/audio path | `cargo run --bin asset_pack -- --dry-run --list` |
| visible runtime behavior | `cargo run` |
| choreography | `cargo run --bin choreo -- validate ...` |

## Step 5: Document The Surface

```mermaid
flowchart LR
    modder[Can a modder use it?]
    modding[Docs/MODDING.md]
    contributor[Does it affect architecture?]
    wiki[Docs/Wiki]
    release[User-visible change?]
    changelog[CHANGELOG.md]

    modder --> modding
    contributor --> wiki
    release --> changelog
```

## Final Slice Checklist

- The feature has a clear owner.
- Content values are data-driven where practical.
- Pure logic is testable where practical.
- Runtime code owns only runtime-specific application.
- Errors degrade gracefully.
- Tools validate the new surface.
- Release packs include required assets.
- Docs explain the contributor/modder-facing contract.
