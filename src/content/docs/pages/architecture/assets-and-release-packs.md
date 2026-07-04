---
title: "5. Assets And Release Packs"
---

Loose assets make development and modding easy. Packed assets make release builds reliable.

Both paths matter.

## Read Path

```mermaid
flowchart TD
    request[Runtime asks for path]
    modlayers{Active mod layer has file?}
    loose{Vanilla loose file exists?}
    pack{data.pak has file?}
    ok[return bytes]
    missing[missing asset fallback / error]

    request --> modlayers
    modlayers -- yes --> ok
    modlayers -- no --> loose
    loose -- yes --> ok
    loose -- no --> pack
    pack -- yes --> ok
    pack -- no --> missing
```

Identity media uses a separate path through `identity.pak` and is not part of the ordinary mod override chain.

## Release Discovery

`discover_used_asset_paths()` decides what ships in `data.pak`.

```mermaid
flowchart TB
    data[Assets/Data]
    metadata[Assets/Metadata]
    scripts[Assets/Scripts]
    dialogue[Assets/Dialogue]
    shader_manifest[shaders.toml refs]
    character_manifest[characters.toml refs]
    audio_manifest[sfx/music core ids]
    hardcoded[explicit runtime files]
    mods[Mods/<mod_id>]
    discover[discover_used_asset_paths]
    pack[data.pak]

    data --> discover
    metadata --> discover
    scripts --> discover
    dialogue --> discover
    shader_manifest --> discover
    character_manifest --> discover
    audio_manifest --> discover
    hardcoded --> discover
    mods --> discover
    discover --> pack
```

## Why Contributors Should Care

A new asset can work in `cargo run` but disappear in a packaged release if discovery misses it.

That usually happens when:

- code directly loads a path not listed in `HARDCODED_RUNTIME_FILES`
- a new core audio id is played but not included in `CORE_SFX_IDS`
- a shader or texture is not referenced from a manifest
- a new asset lives outside scanned directories

## Correct Asset Addition Pattern

```mermaid
flowchart LR
    newasset[New asset]
    manifest{Can a manifest own it?}
    manifest_yes[Reference from TOML/metadata]
    scanned{Is it in scanned dir?}
    scanned_yes[No asset_pack edit]
    explicit[Add explicit discovery entry]
    verify[asset_pack --dry-run --list]

    newasset --> manifest
    manifest -- yes --> manifest_yes --> verify
    manifest -- no --> scanned
    scanned -- yes --> scanned_yes --> verify
    scanned -- no --> explicit --> verify
```

## Verification Commands

List discovered paths:

```powershell
cargo run --bin asset_pack -- --dry-run --list
```

Build and verify `data.pak`:

```powershell
cargo run --bin asset_pack -- --out data.pak --inventory-out asset_inventory.md --verify
```

Build an encrypted `data.pak` explicitly:

```powershell
cargo run --bin asset_pack -- --key universal.key --out data.pak --inventory-out asset_inventory.md --verify
```

For full distribution, prefer the dist scripts because they also decide whether the release binary should embed `ECHO_WARRIOR_ASSET_KEY`.

```mermaid
flowchart TD
    dist[dist script]
    key{repo-root universal.key?}
    encrypted[encrypted data.pak]
    embedded[embed asset key in binary]
    plain[unencrypted data.pak]
    warn[warn distributor]
    verify[verify inventory and bytes]

    dist --> key
    key -- yes --> encrypted --> embedded --> verify
    key -- no --> warn --> plain --> verify
```

No key is allowed. `universal.key` is only required for encrypted `data.pak`;
omitting it produces a verified plain pack and a warning during distribution.
Use that knowingly, not by accident.

Validate mod/content references:

```powershell
cargo run --bin mod_check
```

## Identity Pack

`identity.pak` is for canonical studio media. It is always encrypted by release scripts with a fresh key embedded in that build.

```mermaid
flowchart LR
    frames[studio intro frames/audio]
    identity_discovery[discover_identity_asset_paths]
    key[fresh identity key]
    identity_pack[identity.pak]
    release[release binary embeds key]

    frames --> identity_discovery
    identity_discovery --> identity_pack
    key --> identity_pack
    key --> release
```

Mods may suppress the studio intro through manifest settings, but they do not replace identity media.
