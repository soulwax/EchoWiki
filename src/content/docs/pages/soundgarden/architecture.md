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
- `audio` also owns mod listing, effective overlay views, and mod scaffolding.
- Soundgarden edits JSON in memory and exports TOML through `audio`.
- The runtime reads the same TOML as before.

## Current Tool Layers

```mermaid
flowchart TB
    main[src/main.ts]
    doc[src/doc.ts<br/>AudioDoc]
    id[src/id.ts]
    overlay[src/overlay.ts<br/>mod rows]
    modmode[src/modmode.ts<br/>overlay paths]
    bridge[src/bridge.ts]
    shell[src-tauri/src/main.rs]
    secrets[src-tauri/src/secrets.rs]
    cli[audio CLI<br/>missing in current main]

    main --> doc
    main --> id
    main --> overlay
    main --> modmode
    main --> bridge
    bridge --> shell
    shell --> secrets
    shell --> cli
```

Important boundary: `src/main.ts` renders and coordinates. It should not become the owner of manifest state. `AudioDoc` owns that.

## Packaging Boundary

Soundgarden is now part of the dist suite, but the packaged app still depends on the same CLI boundary as the desktop shell.

```mermaid
flowchart TB
    dist[dist script]
    app[soundgarden app]
    cli[audio CLI]
    missing{CLI present}
    package[soundgarden zip]
    warning[warning and AUDIO_BIN hint]

    dist --> app
    dist --> cli
    cli --> missing
    missing -- yes --> package
    missing -- no --> warning --> package
```

The package can exist before the full authoring loop is ready. Contributors should still treat `audio validate`, `convert`, `schema`, `assets`, and `scan` as the completion contract.

## Bridge Calls

```mermaid
sequenceDiagram
    participant UI as TypeScript UI
    participant Bridge as TypeScript bridge
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
| `mods()` | `audio_mods` | `audio mods` |
| `effective(kind, modId)` | `audio_effective` | `audio effective --kind <kind> [--mod <id>]` |
| `initMod(id, name)` | `audio_init_mod` | `audio init-mod <id> [--name <name>]` |
| `readClip(path, modId)` | `read_clip` | Shell resolves bytes from mod/vanilla `Assets/` |
| `loadManifest(path)` | `load_manifest` | `audio convert <path> <tmp.json>` |
| `saveManifest(path,json)` | `save_manifest` | `audio convert <tmp.json> <path>` |
| `exportManifest(path,json)` | `export_manifest` | validate first, then convert |

## Mod Mode Boundary

```mermaid
sequenceDiagram
    participant UI as Soundgarden UI
    participant Shell as Tauri shell
    participant AudioCli as audio CLI
    participant Doc as AudioDoc

    UI->>Shell: audio_effective kind
    Shell->>AudioCli: effective --kind kind
    AudioCli-->>Shell: vanilla effective entries
    Shell-->>UI: entries JSON
    UI->>Shell: load overlay path
    Shell->>AudioCli: convert overlay TOML to JSON
    Shell-->>UI: overlay JSON or missing-file report
    UI->>Doc: create overlay document
```

In mod mode, `doc` is the overlay document. Vanilla rows are a read-only base rendered behind it. Editing a vanilla row forks it into the overlay with `forkEntry()`.

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
4. Add the Phase 1.5 commands the current Tauri shell already calls: `mods`, `effective`, `init-mod`, and the file read path needed by audition playback.
5. Fix the `tools/soundgarden` submodule mapping or intentionally vendor it.
6. Run `npm test`, `npm run build`, and the game-side `audio` CLI checks.
