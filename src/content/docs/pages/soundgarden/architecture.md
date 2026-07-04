---
title: "Soundgarden Architecture"
---

Soundgarden mirrors Leitmotif's architectural idea: a focused editor talks to a game-owned CLI contract.

## Target Shape

```mermaid
flowchart TB
    manifests[Audio manifests]
    rust[Rust data structs]
    cli[audio CLI]
    tauri[Tauri shell]
    ui[Soundgarden UI]
    runtime[Game runtime]

    rust --> cli
    manifests --> cli
    cli --> tauri
    tauri --> ui
    manifests --> runtime
```

The target contract is:

- Rust data structs define the shape.
- `audio` parses, validates, converts, scans, and emits schema.
- Soundgarden edits JSON in memory and exports TOML through `audio`.
- The runtime reads the same TOML as before.

## Current Tool Layers

```mermaid
flowchart TB
    main[src/main.ts]
    doc[src/doc.ts<br/>AudioDoc]
    id[src/id.ts]
    bridge[src/bridge.ts]
    shell[src-tauri/src/main.rs]
    secrets[src-tauri/src/secrets.rs]
    cli[audio CLI<br/>missing in current main]

    main --> doc
    main --> id
    main --> bridge
    bridge --> shell
    shell --> secrets
    shell --> cli
```

Important boundary: `src/main.ts` renders and coordinates. It should not become the owner of manifest state. `AudioDoc` owns that.

## Bridge Calls

```mermaid
sequenceDiagram
    participant UI as TypeScript UI
    participant Bridge as src/bridge.ts
    participant Shell as Tauri shell
    participant CLI as audio CLI

    UI->>Bridge: validate(path)
    Bridge->>Shell: invoke("audio_validate")
    Shell->>CLI: audio validate path --json
    CLI-->>Shell: findings JSON
    Shell-->>Bridge: BridgeResult
    Bridge-->>UI: validation chip
```

Expected bridge commands:

| UI wrapper | Tauri command | CLI call |
| --- | --- | --- |
| `validate(path)` | `audio_validate` | `audio validate <path> --json` |
| `schema(kind)` | `audio_schema` | `audio schema --kind <kind>` |
| `assets()` | `audio_assets` | `audio assets` |
| `scan(dir)` | `audio_scan` | `audio scan [--dir]` |
| `loadManifest(path)` | `load_manifest` | `audio convert <path> <tmp.json>` |
| `saveManifest(path,json)` | `save_manifest` | `audio convert <tmp.json> <path>` |
| `exportManifest(path,json)` | `export_manifest` | validate first, then convert |

## Export Safety

Export should be validate-then-write:

```mermaid
sequenceDiagram
    participant User
    participant App
    participant CLI as audio
    participant File as Manifest file

    User->>App: Export to game
    App->>CLI: validate temp JSON
    alt clean
        App->>CLI: convert temp JSON to TOML
        CLI->>File: write manifest
    else errors
        App-->>User: show findings
    end
```

This prevents the editor from writing content the game cannot parse.

## Runtime Boundary

The runtime does not know Soundgarden exists.

```mermaid
flowchart LR
    toml[Manifest TOML]
    loader[src/data/mod_data.rs]
    audio[src/runtime/audio.rs]
    voice[src/runtime/voice.rs]
    game[Playable runtime]

    toml --> loader
    loader --> audio
    loader --> voice
    audio --> game
    voice --> game
```

That is the right boundary. Soundgarden should make data safer and easier to maintain, but the game should continue to run from the manifest files.

## Open Architectural Work

Before Soundgarden can be called complete in this checkout:

1. Add or restore `src/bin/audio.rs`.
2. Ensure `Cargo.toml` declares the `audio` binary if needed.
3. Make `audio validate`, `convert`, `schema`, `assets`, and `scan` pass against current manifests.
4. Fix the `tools/soundgarden` submodule mapping or intentionally vendor it.
5. Run `npm test`, `npm run build`, and the game-side `audio` CLI checks.

