---
title: "Leitmotif Architecture"
---

Leitmotif is a thin authoring app around the game's choreography contract. Its best design property is that the UI never becomes a second game engine.

## Big Picture

```mermaid
flowchart LR
    app[Leitmotif app]
    schema[choreography.schema.json]
    choreo[choreo CLI]
    scenes[Scene files]
    runtime[EchoWarrior runtime]

    schema --> app
    app --> choreo
    choreo --> scenes
    scenes --> runtime
    choreo --> app
```

The app reads schema metadata, edits a scene document, and asks `choreo` for authoritative operations:

- `validate`
- `validate --json`
- `convert`
- `schema`
- `preview`
- `assets`
- `graph`

## Main Layers

```mermaid
flowchart TB
    main[src/main.ts<br/>UI coordinator]
    scene[src/scene.ts<br/>SceneDoc]
    project[src/project.ts<br/>many scenes]
    timeline[src/timeline.ts<br/>steps and beats]
    forms[src/form.ts + src/trigger.ts<br/>schema forms]
    stage[src/stage.ts + src/preview.ts<br/>live preview shell]
    suggest[src/suggest.ts + src/rules.ts<br/>authoring aids]
    bridge[src/bridge.ts<br/>web wrappers]
    tauri[src-tauri/src/main.rs<br/>native commands]
    cli[choreo CLI]

    main --> scene
    main --> project
    main --> timeline
    main --> forms
    main --> stage
    main --> suggest
    main --> bridge
    bridge --> tauri
    tauri --> cli
```

`src/main.ts` is deliberately busy because it is the editor coordinator. The important boundary is that it routes mutations into `SceneDoc` instead of letting each component own divergent scene state.

## Document Model

`SceneDoc` mirrors the choreography contract:

```mermaid
flowchart TB
    scene[ChoreographyScene]
    sequences[Sequence list]
    steps[Step list]
    beats[Beat list]
    edit[SceneDoc.edit]
    history[Undo / redo stacks]

    scene --> sequences
    sequences --> steps
    steps --> beats
    edit --> scene
    edit --> history
```

Contributor rule: every meaningful content mutation should go through `SceneDoc.edit()` or a helper that calls it, such as `addBeat`, `replaceBeat`, `moveBeat`, `addStep`, or `moveStep`.

This keeps dirty tracking, undo/redo, and UI refreshes predictable.

## Bridge Boundary

```mermaid
sequenceDiagram
    participant UI as TypeScript UI
    participant Bridge as TypeScript bridge
    participant Tauri as Tauri shell
    participant CLI as choreo
    participant Files as scene files

    UI->>Bridge: validate(path)
    Bridge->>Tauri: invoke("choreo_validate")
    Tauri->>CLI: choreo validate path
    CLI->>Files: read scene data
    CLI-->>Tauri: report
    Tauri-->>Bridge: Result string
    Bridge-->>UI: BridgeResult
```

The browser-side bridge degrades when Tauri is unavailable. The native side degrades when `CHOREO_BIN` is missing by returning a clear error string. Both choices matter: authors should see a problem, not lose work.

## Suggestions

```mermaid
flowchart LR
    ctx[SuggestContext]
    engine[suggestions()]
    providers[SuggestionProvider list]
    rules[RuleProvider]
    merged[deduped ranked suggestions]
    doc[SceneDoc apply()]

    ctx --> engine
    engine --> providers
    providers --> rules
    rules --> merged
    merged --> doc
```

The current suggestion layer is deterministic and offline. `src/suggest.ts` owns the provider contract, timeout behavior, de-duplication, and ranking. `src/rules.ts` registers the rule provider and creates valid-by-construction suggestions from known beat vocabulary, actors, sfx ids, and validation findings.

An LLM provider can be added later behind the same provider interface, but the rules-only floor must remain useful.

## Story Graph

Project mode loads a folder of scene files:

```mermaid
flowchart TB
    folder[Scene folder]
    project[Project.open]
    list[listSceneDir]
    docs[SceneDoc map]
    graph[choreo graph --json]
    canvas[story canvas]
    sidecar[.leitmotif/layout.json]

    folder --> project
    project --> list
    list --> docs
    project --> graph
    graph --> canvas
    sidecar --> canvas
```

`Project` composes `SceneDoc` instances. It does not add a second mutation model for scene internals. The graph canvas can create, rename, duplicate, delete, and arrange scene nodes, while individual scene edits still belong to `SceneDoc`.

## Contributor Checklist

Before changing architecture-sensitive code, ask:

- Does this keep `choreo` as the source of truth?
- Does this mutation go through `SceneDoc`?
- Does this degrade cleanly in web-only mode?
- Does this stay testable without the desktop shell?
- Does the UI still make invalid export hard?
