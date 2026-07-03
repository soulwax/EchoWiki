# Change Routes

Use this page when you know the kind of contribution you want to make, but not where to start.

## I Want To Fix A Bug

1. Reproduce it.
2. Identify whether it is pure logic, runtime behavior, data loading, or content.
3. Add the smallest test possible if the bug is in `src/game`, `src/data`, `src/save`, `src/scripting`, or a CLI.
4. Run `cargo check` and the targeted test.

Common starting points:

| Bug type | Start here |
| --- | --- |
| wrong stats or values | `Assets/Data/*.toml`, `src/data/mod_data.rs` |
| wrong enemy/player rule | `src/game/*` or `src/runtime/mod.rs` depending on ownership |
| save issue | `src/save/mod.rs` |
| dialogue issue | `Assets/Dialogue/*.yaml`, `src/game/dialogue_loader.rs`, `src/runtime/npc_dialogue.rs` |
| Lua issue | `Assets/Scripts`, `src/scripting/mod.rs` |
| rendering issue | `src/runtime`, shaders, `Assets/Data/shaders.toml` |
| asset missing in release | `src/asset_pack.rs`, `src/bin/asset_pack.rs` |

## I Want To Add Or Tune Content

Start in `Assets/`, not Rust.

| Content | Data path |
| --- | --- |
| enemies | `Assets/Data/enemies.toml` |
| spawn waves | `Assets/Scripts/spawn.lua` or `Assets/Scripts/spawn.d/*.lua` |
| upgrades | `Assets/Data/upgrades.toml` |
| items | `Assets/Data/items.toml` |
| abilities | `Assets/Data/abilities.toml` |
| companions | `Assets/Data/companions.toml` |
| dialogue | `Assets/Dialogue/*.yaml` |
| UI text/theme | `Assets/Data/ui.toml`, `Assets/Data/theme.toml` |
| weather | `Assets/Data/weather_presets.toml` |
| choreography | `Assets/Data/choreography.toml`, `Assets/Data/scenes/*.toml` |

Then run:

```powershell
cargo run --bin mod_check
cargo run --bin asset_pack -- --dry-run --list
```

## I Want To Add A Modding Surface

A modding surface is any new field, command, hook, schema, or file a modder can use.

Checklist:

1. Add the data model and defaults.
2. Load it gracefully.
3. Apply it in the correct runtime or pure layer.
4. Validate it in `mod_check` where practical.
5. Document it in `Docs/MODDING.md`.
6. Confirm release-pack discovery.

Avoid adding a Rust-only shortcut if the goal is modder control.

## I Want To Improve The Runtime

Runtime work usually lives under `src/runtime`.

Before editing, identify whether the logic can be pushed into a pure module:

- targeting/math/rules often belong in `src/game`
- layout descriptions often belong in `src/ui/layout.rs`
- renderer calls and Macroquad types belong in `src/runtime`

Run:

```powershell
cargo check
cargo run
```

For visual changes, verify in-game. Screenshot or describe what you checked.

## I Want To Improve Tooling

Tool front doors live in `src/bin`.

| Tool | Purpose |
| --- | --- |
| `asset_pack` | release asset pack build/verify/unpack |
| `mod_check` | content/mod validation |
| `sprite_cutter` | spritesheet cutting |
| `choreo` | choreography validation/conversion/schema/preview |

Tooling changes should return clear human-readable errors. When possible, add a test around the parser or validator helper.

## I Want To Work On Choreography

Do not create a second choreography system.

Start with:

- `Docs/CHOREO_FORMAT.md`
- `Assets/Data/scenes/*.toml`
- `src/game/choreography.rs`
- `src/runtime/choreography.rs`
- `src/bin/choreo.rs`

Validate with:

```powershell
cargo run --bin choreo -- validate Assets/Data/scenes
cargo run --bin mod_check
```

## I Want To Update This Wiki

Edit Markdown in the wiki repository. In a game checkout, this repository is mounted at `Docs/Wiki`; inside the wiki repo itself, the site root is the repository root.

If you add a page:

1. Put it under `pages`.
2. Add it to `_sidebar.md`.
3. Serve locally:

```powershell
py -m http.server 8000
```

4. Check the page at `http://localhost:8000`.
