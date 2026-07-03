# 12. Verification Architecture

Verification in EchoWarrior is layered like the codebase. The right check depends on what boundary changed.

## Verification Map

```mermaid
flowchart TB
    change[Change]
    rust[Rust code]
    content[Assets / Mods content]
    assets[Runtime asset paths]
    choreo[Choreography scenes]
    runtime[Runtime behavior]
    release[Release packaging]

    check[cargo check]
    fmt[cargo fmt --check]
    tests[cargo test / scoped tests]
    modcheck[cargo run --bin mod_check]
    pack[cargo run --bin asset_pack -- --dry-run --list]
    choreocli[cargo run --bin choreo -- validate]
    run[cargo run]
    dist[scripts/dist]

    change --> rust --> check
    rust --> fmt
    rust --> tests
    change --> content --> modcheck
    change --> assets --> pack
    change --> choreo --> choreocli
    change --> runtime --> run
    change --> release --> dist
```

## Boundary-To-Check Table

| Boundary changed | Minimum useful check | Stronger check |
| --- | --- | --- |
| Rust compile surface | `cargo check` | `cargo test` |
| Rust formatting | `cargo fmt --check` | `cargo fmt --check && cargo clippy --all-targets -- -D warnings` |
| pure game/data logic | targeted `cargo test --lib` | full `cargo test` |
| runtime behavior | `cargo check` | `cargo run` smoke test |
| TOML/YAML/Lua content | `cargo run --bin mod_check` | run game with content loaded |
| asset discovery | `asset_pack --dry-run --list` | `asset_pack --verify` |
| choreography | `choreo validate` | `choreo preview` plus runtime smoke |
| release scripts | pack verify | `scripts/dist.ps1` or `scripts/dist.sh` |

## Why There Is No Single Check

```mermaid
flowchart LR
    cargo[cargo check/test]
    content[Content validation]
    pack[Pack discovery]
    runtime[Manual runtime smoke]

    cargo -. misses .-> content
    content -. misses .-> pack
    pack -. misses .-> runtime
    runtime -. misses .-> cargo
```

Each check sees a different failure class. A compile pass does not prove a mod data reference is valid. A mod check does not prove the VFX is readable. A runtime smoke test does not prove release assets ship.

## Tool Roles

```mermaid
flowchart TB
    modcheck[mod_check]
    assetpack[asset_pack]
    choreo[choreo]
    sprite[sprite_cutter]
    cargo[Cargo]

    modcheck --> toml[TOML/YAML/Lua/schema/reference sanity]
    assetpack --> release[release asset inventory and bytes]
    choreo --> scenes[choreography semantics and tooling contracts]
    sprite --> metadata[spritesheet metadata and generated frames]
    cargo --> rust[Rust compile, tests, formatting, lints]
```

## Contributor Rule

When reporting a change, include:

- command run
- pass/fail result
- if failed, whether the failure is related
- any environment caveat

Do not say a check passed unless you ran it.
