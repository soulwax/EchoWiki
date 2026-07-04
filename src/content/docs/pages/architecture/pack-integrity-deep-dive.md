---
title: "Pack Integrity Deep Dive"
---

This page goes below the asset-pack overview and explains the mechanics that protect release packs from accidental drift and casual tampering.

The important mental model: pack integrity is mostly a build-time guarantee, while pack encryption is a lightweight runtime obfuscation layer.

## Build-Time Integrity Pipeline

```mermaid
flowchart TD
    source[repo source assets]
    discover[discover paths]
    build[build AssetPack entries]
    write[write pack]
    reread[read pack back]
    comparepaths[compare expected vs actual paths]
    comparebytes[compare packed bytes vs source bytes]
    payloadcheck[validate payload by kind]
    inventory[write inventory]
    release[release artifact]

    source --> discover --> build --> write --> reread
    reread --> comparepaths --> comparebytes --> payloadcheck
    payloadcheck --> inventory --> release
```

`asset_pack --verify` is the key step. It proves that the just-written pack still contains exactly the discovered paths, with byte-identical payloads, and with parseable payloads for known asset kinds.

## Discovery Split

```mermaid
flowchart LR
    ordinary[ordinary runtime content]
    identity[identity media]
    used[discover_used_asset_paths]
    identityused[discover_identity_asset_paths]
    datapak[data.pak]
    identitypak[identity.pak]

    ordinary --> used --> datapak
    identity --> identityused --> identitypak
```

The split is deliberate. Ordinary runtime content is part of the moddable data surface. Identity media is canonical studio media and has a separate read path.

## Ordinary Discovery Graph

```mermaid
flowchart TB
    data[Assets/Data]
    metadata[Assets/Metadata]
    scripts[Assets/Scripts]
    mods[Mods]
    dialogue[Assets/Dialogue]
    character[characters.toml sprite metadata]
    shaders[shaders.toml source refs]
    fonts[fonts.toml paths]
    audio[sfx/music core ids]
    descriptor[metadata image/source/path refs]
    hardcoded[HARDCODED_RUNTIME_FILES]
    pack[data.pak]

    data --> pack
    metadata --> pack
    scripts --> pack
    mods --> pack
    dialogue --> pack
    character --> pack
    shaders --> pack
    fonts --> pack
    audio --> pack
    descriptor --> pack
    hardcoded --> pack
```

If a runtime asset can be manifest-owned, prefer that over adding a hardcoded path. Hardcoded discovery is for files that have no better data owner.

## Identity Discovery Graph

```mermaid
flowchart TD
    frames[Assets/Cinematics/Generated/frames]
    prefix{filename starts with intro_cinematics_?}
    audio[Generated intro audio OGG]
    identitypaths[identity path set]
    pack[identity.pak]

    frames --> prefix
    prefix -- yes --> identitypaths
    prefix -- no --> ignored[ignored stale/generated file]
    audio --> identitypaths
    identitypaths --> pack
```

The prefix filter is a stale-file guard. Generated folders can accumulate old media; identity discovery only takes the expected current frame family plus the generated intro audio.

## Pack File Shape

```mermaid
flowchart LR
    file[pack file]
    header[32 byte header]
    payload[payload bytes]
    magic[PACK_MAGIC]
    version[format version]
    flags[encrypted flag]
    len[payload length]
    sum[checksum64 plain payload]
    entries[entry stream]

    file --> header
    file --> payload
    header --> magic
    header --> version
    header --> flags
    header --> len
    header --> sum
    payload --> entries
```

The decoded payload starts with its own payload magic, then an entry count, then entries. Each entry stores:

| Field | Purpose |
| --- | --- |
| kind byte | data, dialogue, script, texture, audio, font, shader, metadata, other |
| path bytes | normalized forward-slash path |
| byte length | payload length for this entry |
| bytes | original source file bytes |

## Write Path State Machine

```mermaid
stateDiagram-v2
    [*] --> CollectPaths
    CollectPaths --> BuildEntries
    BuildEntries --> EncodePayload
    EncodePayload --> ComputeChecksum
    ComputeChecksum --> MaybeEncrypt
    MaybeEncrypt --> WriteHeader
    WriteHeader --> WritePayload
    WritePayload --> VerifyRequested
    VerifyRequested --> Done: no --verify
    VerifyRequested --> ReadBack: --verify
    ReadBack --> Compare
    Compare --> Done: exact match
    Compare --> Fail: missing/stale/different/corrupt
```

The checksum is calculated over the plain encoded payload. If the pack is encrypted, the checksum also acts as part of the keystream nonce.

## Read Path State Machine

```mermaid
stateDiagram-v2
    [*] --> FindPack
    FindPack --> ReadBytes
    ReadBytes --> CheckMagic
    CheckMagic --> LegacyFallback: version mismatch
    CheckMagic --> CheckFlags: current version
    CheckFlags --> NeedKey: encrypted
    CheckFlags --> DecodePayload: plain
    NeedKey --> Decrypt: key found
    NeedKey --> Fail: no key
    Decrypt --> CheckChecksum
    DecodePayload --> CheckChecksum
    LegacyFallback --> CheckChecksum
    CheckChecksum --> DecodeEntries: matches
    CheckChecksum --> Fail: wrong key or corrupt pack
    DecodeEntries --> Ready
```

Wrong key and corrupt payload both land at checksum mismatch. The runtime should treat that as "pack unavailable" and continue with loose/fallback behavior where possible.

## Key Resolution

```mermaid
flowchart TB
    datapak[data.pak read]
    identity[identity.pak read]
    universal[universal.key]
    legacy[legacy hwdruntime]
    embeddedasset[ECHO_WARRIOR_ASSET_KEY]
    embeddedidentity[ECHO_WARRIOR_IDENTITY_KEY]
    readpack[read_pack]

    datapak --> universal
    datapak --> legacy
    datapak --> embeddedasset
    universal --> readpack
    legacy --> readpack
    embeddedasset --> readpack
    identity --> embeddedidentity --> readpack
```

`data.pak` supports key files for development and embedded asset keys for packaged release builds. New release packaging uses `universal.key`; `hwdruntime` remains only as a legacy runtime fallback so older local encrypted packs can still be read.

## Release Encryption Decision

```mermaid
flowchart TD
    release[release packaging]
    key{universal.key present?}
    encrypt[encrypt data.pak with UniversalKey]
    embed[embed same key in ECHO_WARRIOR_ASSET_KEY]
    plain[write unencrypted data.pak]
    warning[print distribution warning]
    verify[verify pack contents]
    ship[ship package]

    release --> key
    key -- yes --> encrypt --> embed --> verify
    key -- no --> warning --> plain --> verify
    verify --> ship
```

This means encryption is optional for `data.pak`, but integrity is not optional. Both branches still run `asset_pack --verify`.

## What Verification Catches

```mermaid
flowchart TD
    verify[asset_pack --verify]
    missing[missing discovered path]
    stale[extra stale pack entry]
    changed[source bytes differ]
    empty[empty payload]
    invalid[invalid typed payload]
    wrongkey[wrong key / corrupt pack]
    ok[pack accepted]

    verify --> missing
    verify --> stale
    verify --> changed
    verify --> empty
    verify --> invalid
    verify --> wrongkey
    verify --> ok
```

Typed payload checks include:

| Kind | Verification |
| --- | --- |
| data / metadata | valid UTF-8 and TOML |
| dialogue | valid UTF-8 and YAML |
| script / shader | valid UTF-8 |
| texture | image decoder can read bytes |
| audio / font / other | non-empty, plus byte identity |

This is not a full semantic validation pass. Pair it with `mod_check` for cross-references and command/data contracts.

## Runtime Read Layering

```mermaid
sequenceDiagram
    participant Runtime as Runtime loader
    participant Mods as Active mod layers
    participant Loose as Loose vanilla files
    participant Pack as data pack
    participant Fallback as Loader fallback

    Runtime->>Mods: read requested path
    alt found in active mod
        Mods-->>Runtime: bytes
    else not found
        Runtime->>Loose: read loose file
        alt loose file exists
            Loose-->>Runtime: bytes
        else not found
            Runtime->>Pack: read packed entry
            alt pack entry exists
                Pack-->>Runtime: bytes
            else missing
                Runtime->>Fallback: default/error path
            end
        end
    end
```

This is why release verification is necessary: development can hide discovery mistakes because loose files are earlier in the read order.

## Identity Read Layering

```mermaid
sequenceDiagram
    participant Runtime as Identity reader
    participant Loose as Loose identity file
    participant Pack as identity pack

    Runtime->>Runtime: read_identity(path)
    alt debug build
        Runtime->>Loose: try repository file
        Loose-->>Runtime: bytes if present
    end
    Runtime->>Pack: read identity.pak entry
    alt present
        Pack-->>Runtime: bytes
    else unavailable
        Pack-->>Runtime: not found
    end
```

There is no active-mod check here. That absence is the protection boundary.

## Where To Automate More

The current automation already handles the highest-risk release questions, but useful next checks would be:

```mermaid
flowchart TD
    current[current automation]
    manifest[manifest reference coverage]
    identitycount[identity expected frame count]
    modlayers[active mod merge simulation]
    audio[audio manifest asset decode]
    shader[shader include graph]
    ci[CI workflow]

    current --> manifest
    current --> identitycount
    current --> modlayers
    current --> audio
    current --> shader
    manifest --> ci
    identitycount --> ci
    modlayers --> ci
    audio --> ci
    shader --> ci
```

Prefer adding automation at the boundary where mistakes become expensive:

- before launch: `mod_check`
- before release: `asset_pack --verify`
- before publishing docs: `npm run build` and `npm run wiki:audit`
