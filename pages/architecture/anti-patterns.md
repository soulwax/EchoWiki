# 19. Anti-Patterns

This page lists architectural moves that usually make EchoWarrior harder to maintain, mod, or ship.

## Hardcoding Content In Runtime

```mermaid
flowchart LR
    bad[Hardcoded runtime value]
    problem[Modder cannot change it]
    drift[Data and code drift]
    fix[Move to Assets/Data when practical]

    bad --> problem --> drift --> fix
```

Examples:

- enemy stats in actor constructors
- upgrade numbers in UI code
- fixed dialogue text in runtime
- shader/audio paths not owned by a manifest or discovery rule

## Parallel Systems

```mermaid
flowchart TD
    need[Need a new behavior]
    existing[Existing system]
    parallel[New parallel system]
    confusion[Two places to author/debug]

    need --> parallel --> confusion
    existing -. should extend .-> need
```

Avoid parallel systems for:

- choreography/scene beats
- entity lifecycle ownership
- command vocabularies
- mod layering
- save metadata

## Runtime-Only Rules

Rules embedded directly in draw/update code are hard to test.

```mermaid
flowchart LR
    update[Runtime update code]
    rule[Hidden gameplay rule]
    notest[No pure test]
    extract[Extract rule to src/game or src/ui]

    update --> rule --> notest --> extract
```

If the rule does not need Macroquad, consider extracting it.

## Asset Works Loose, Fails Packed

```mermaid
flowchart TD
    loose[Loose file exists]
    run[cargo run works]
    missing[Not discovered by asset_pack]
    release[Release build missing asset]

    loose --> run --> missing --> release
```

Every runtime-loaded asset needs a discovery path.

## Silent Failure

Silent failure is worse than noisy fallback.

```mermaid
flowchart LR
    error[Content/load error]
    silent[No message]
    mystery[Contributor/modder guesses]
    diagnostic[Log or mod_check diagnostic]

    error --> silent --> mystery
    error --> diagnostic
```

If the game falls back, say why through stderr/tracing or tool output.

## Big-Bang Refactors

Broad rewrites are especially risky while the prototype is moving.

Prefer:

- one bridge
- one pure extraction
- one tool validation pass
- one data schema surface
- one focused runtime adapter

Then verify and commit the slice.
