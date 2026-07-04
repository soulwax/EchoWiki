---
title: "CLI Tools"
---

The `src/bin/` files are thin command-line shells over shared library code.

```mermaid
flowchart TB
    contributor[Contributor task]
    assetpack[asset_pack]
    cutter[sprite_cutter]
    modcheck[mod_check]
    choreo[choreo]
    shared[shared library modules]

    contributor --> assetpack --> shared
    contributor --> cutter --> shared
    contributor --> modcheck --> shared
    contributor --> choreo --> shared
```

## `asset_pack`

Builds, verifies, inventories, lists, and unpacks asset packs.

Common commands:

```powershell
cargo run --bin asset_pack -- --dry-run --list
cargo run --bin asset_pack -- --out data.pak --inventory-out asset_inventory.md --verify
cargo run --bin asset_pack -- --identity --key identity.key --out identity.pak --inventory-out identity_inventory.md --verify
cargo run --bin asset_pack -- --pack data.pak --unpack unpacked_assets
```

Responsibilities:

- discover runtime or identity assets
- build an `AssetPack`
- optionally encrypt with `UniversalKey`
- verify packed bytes against source files
- reject unsafe unpack paths

```mermaid
flowchart LR
    discover[discover]
    build[build]
    write[write]
    verify[verify]
    inventory[inventory]
    unpack[unpack]

    discover --> build --> write --> verify
    build --> inventory
    write --> unpack
```

## `sprite_cutter`

Cuts frames from sheets declared in `Assets/Metadata/spritesheets.toml`.

```powershell
cargo run --bin sprite_cutter -- --sheet player
cargo run --bin sprite_cutter -- --all --dry-run
cargo run --bin sprite_cutter -- --all
```

The cutter validates sheet dimensions against metadata before writing frames. Generated output goes under `Generated/Sprites/`, which is ignored by Git.

```mermaid
flowchart TD
    metadata[spritesheets metadata]
    source[source sheet image]
    validate[dimension validation]
    frames[cut frames]
    generated[Generated Sprites]

    metadata --> validate
    source --> validate --> frames --> generated
```

## `mod_check`

Validates moddable content without launching the game.

```powershell
cargo run --bin mod_check
cargo run --bin mod_check -- --root .
```

It checks TOML, YAML, Lua, schema versions, command buffers, shader uniforms, UI/theme values, asset-pack discoverability, save-sensitive ids, ability references, items, choreography, scene projects, and mod manifests.

Use it before shipping a mod or release package.

```mermaid
flowchart TB
    data[TOML and YAML]
    lua[Lua scripts]
    refs[Cross references]
    shaders[Shader contracts]
    packs[Pack discoverability]
    report[Warnings and errors]

    data --> report
    lua --> report
    refs --> report
    shaders --> report
    packs --> report
```

## `choreo`

The choreography contract CLI is the bridge between game data and authoring tools.

```powershell
cargo run --bin choreo -- validate Assets/Data/choreography.toml
cargo run --bin choreo -- validate Assets/Data/scenes
cargo run --bin choreo -- convert scene.toml scene.json
cargo run --bin choreo -- schema --out choreography.schema.json
cargo run --bin choreo -- preview Assets/Data/scenes/example_scene.toml intro
cargo run --bin choreo -- assets
cargo run --bin choreo -- graph Assets/Data/scenes --json
```

The CLI is intentionally thin: the data model and validation rules live in `echo_warrior::game::choreography`.

```mermaid
flowchart LR
    scenes[Scene files]
    validate[validate]
    schema[schema]
    convert[convert]
    preview[preview]
    graph[graph]
    model[choreography model]

    scenes --> validate --> model
    scenes --> convert --> model
    scenes --> preview --> model
    scenes --> graph --> model
    model --> schema
```
