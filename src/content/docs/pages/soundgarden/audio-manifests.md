---
title: "Soundgarden Audio Manifests"
---

Soundgarden is built around three data files the game already reads.

## SFX

`Assets/Data/sfx.toml` contains one-shot effects.

```toml
[[sfx]]
id = "gssounds-hit"
asset = "Audio/GSSounds/Hit.wav"
category = "rpg"
duration = 0.577
```

Fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable kebab-case id referenced from code, data, choreography, or dialogue commands. |
| `asset` | Path relative to `Assets/`, using forward slashes. |
| `category` | Coarse grouping such as `rpg`, `weather`, `voice`, `casino`, `digital`, or `undead`. |
| `duration` | Informational clip length in seconds. |

Runtime:

- loaded by `load_sfx_from`
- consumed by `SfxBank`
- formats currently guarded to `.ogg` and `.wav`

## Music

`Assets/Data/music.toml` contains long cues and loops.

```toml
[[track]]
id = "gssounds-babis-lighthouse"
asset = "Audio/GSSounds/Music/babis_lighthouse.ogg"
loop = true
duration = 165.029
```

Fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable track id. |
| `asset` | Path relative to `Assets/`. |
| `loop` | Whether the runtime should treat the track as looping. |
| `duration` | Informational track length in seconds. |

Runtime:

- loaded by `load_music_from`
- consumed by `LoopingTrack`
- used for intro music, gameplay music, and weather/ambience loops

## Voices

`Assets/Data/voices.toml` contains pseudo-speech profiles.

```toml
[[voice]]
id = "eve"
speaker = "Eve"
profile = "low_feminine_whisper"
enabled = true
pitch = 1.14
muffle = 0.72
roughness = 0.035
talk_speed = 4.5
volume = 0.86
```

Fields:

| Field | Meaning |
| --- | --- |
| `id` | Character or enemy id. |
| `speaker` | Display speaker name used by dialogue. |
| `profile` | Human-readable voice profile label. |
| `enabled` | Whether generated pseudo-speech is active for this speaker. |
| `pitch` | Voice pitch multiplier. |
| `muffle` | How muffled the generated voice is. |
| `roughness` | Breath/noise amount. |
| `talk_speed` | Speech cadence. |
| `volume` | Per-speaker volume multiplier. |

Runtime:

- loaded by `load_voices_from`
- consumed by `src/runtime/voice.rs`
- absent or malformed files fall back to an empty map rather than crashing

## Generator

`tools/gen_audio_manifests.py` can regenerate large audio manifests from on-disk files and durations.

Use it when adding or removing many audio clips. Use Soundgarden when curating entries, categories, ids, and manifest metadata interactively.

## Contributor Rules

- Add new playable sounds through manifests, not by hardcoding file paths.
- Keep ids stable once referenced.
- Use forward-slash `Assets/` relative paths.
- Keep runtime-played SFX to `.ogg` or `.wav` unless the backend guard changes.
- Do not store license text inside manifest entries; keep source license files beside asset packs.
- Run manifest validation once the `audio` CLI is restored.

## Overlay Shape

Soundgarden's mod mode is built around overlay manifests rather than direct edits to vanilla files.

```text
Mods/<mod_id>/Assets/Data/sfx.d/<mod_id>.toml
Mods/<mod_id>/Assets/Data/music.d/<mod_id>.toml
Mods/<mod_id>/Assets/Data/voices.d/<mod_id>.toml
```

An overlay can add new entries, override entries with matching ids, or hide vanilla ids with `remove`.

```toml
remove = ["ui-audio-click1"]

[[sfx]]
id = "ui-audio-click2"
asset = "Audio/MyMod/click_soft.ogg"
category = "ui"
duration = 0.21
```

The editor preserves that shape through `AudioDoc.remove` and the shared `{ kind, entries, remove }` manifest model.
