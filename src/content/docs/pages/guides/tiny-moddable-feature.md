---
title: "Tiny Moddable Feature"
---

This chapter eases you into implementing a tiny moddable feature. The first goal is not to write clever Rust. The first goal is to learn the path a small idea takes through EchoWarrior.

We start with the safest possible feature: a new level-up card that uses existing data fields and existing commands.

## The Tiny Feature Shape

```mermaid
flowchart LR
    idea[Idea]
    data[Assets/Data entry]
    existing[Existing loader and command]
    validate[mod_check]
    pack[asset_pack list]
    run[cargo run smoke test]

    idea --> data --> existing --> validate --> pack --> run
```

This is the best first contribution shape because it teaches the architecture without changing the architecture.

## The Question To Ask First

Can the feature be expressed with existing data?

```mermaid
flowchart TD
    feature[Feature idea]
    existing{Existing schema or command supports it?}
    dataonly[Data-only contribution]
    rust[Small Rust-backed contribution]
    docs[Document the surface]

    feature --> existing
    existing -- yes --> dataonly --> docs
    existing -- no --> rust --> docs
```

For a first feature, prefer "yes".

## Good First Tiny Features

| Feature idea | Likely path |
| --- | --- |
| new level-up card using existing stats | `Assets/Data/upgrades.toml` |
| new item using existing stat effects | `Assets/Data/items.toml` |
| new companion banter line | `Assets/Data/companions.toml` |
| small spawn tweak | `Assets/Scripts/spawn.d/*.lua` |
| new scene beat using existing choreography verbs | `Assets/Data/scenes/*.toml` |
| clearer mod_check error wording | `src/bin/mod_check.rs` |

## When Rust Becomes Necessary

Rust is needed when the idea asks for a new rule, not just new content.

```mermaid
flowchart TD
    idea[New idea]
    newstat{New stat/effect key?}
    newcommand{New command verb?}
    newbeat{New choreography beat?}
    data[Data-only]
    rust[Rust model + apply layer + validation]

    idea --> newstat
    newstat -- yes --> rust
    newstat -- no --> newcommand
    newcommand -- yes --> rust
    newcommand -- no --> newbeat
    newbeat -- yes --> rust
    newbeat -- no --> data
```

If Rust is needed, the slice grows:

1. add or update the data model
2. load with defaults
3. apply in pure code or runtime
4. validate with `mod_check`
5. document in `Docs/MODDING.md`
6. verify asset-pack discovery if assets changed

## First Exercise

Read these in order:

1. [Example: Upgrade Card](../example-upgrade-card/) for a data-only level-up card.
2. [Example: Item Equipment](../example-item-equipment/) for a persistent gear entry.
3. [Example: Spawn Layer](../example-spawn-layer/) for a tiny additive Lua layer.
4. [Example: Mini Dialogue](../example-mini-dialogue/) for a lightweight narrative cue.
5. [Example: Scene Beat](../example-scene-beat/) for a manual choreography scene.
6. [Example: Mod Check Diagnostic](../example-mod-check-diagnostic/) for improving contributor tooling.
7. [Tiny Rust-Backed Stat](../tiny-rust-backed-stat/) for the first moment when existing data is not enough.

Keep the first attempt tiny. A small clean slice teaches more than a large half-finished one.
