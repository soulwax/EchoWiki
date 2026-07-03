# 11. Persistence And State

EchoWarrior has several kinds of state. Keeping them separate prevents save files, settings, run state, and mod metadata from blurring together.

## State Categories

```mermaid
flowchart TB
    run[Current run state]
    account[Account progression]
    settings[User settings]
    content[Content defaults from Assets]
    mods[Active mod metadata]
    autosave[Run autosave]
    progression[Progression save]
    platform[Platform data folder]

    run --> autosave
    account --> progression
    settings --> platform
    content --> run
    mods --> autosave
    mods --> progression
    autosave --> platform
    progression --> platform
```

## Content Defaults vs User State

`Assets/Data/settings.toml` is a moddable default. User-changed settings persist outside `Assets/` in the platform data folder and win on later launches.

```mermaid
flowchart LR
    default[Assets/Data/settings.toml]
    user[Platform settings.toml]
    load[Settings load]
    runtime[Pause menu/runtime settings]
    save[Atomic user settings write]

    default --> load
    user --> load
    load --> runtime
    runtime --> save --> user
```

The architecture rule: do not write user state back into `Assets/`.

## Run Autosaves

Run autosaves preserve the current run profile and selected content context.

```mermaid
sequenceDiagram
    participant Runtime as Runtime
    participant Save as save module
    participant Disk as Platform data folder
    participant Start as Start screen

    Runtime->>Save: build run snapshot
    Save->>Disk: write autosave TOML
    Start->>Save: load matching profile
    Save->>Runtime: restore run/mode snapshot
```

Saved runs may resume into gameplay, pending level-up, victory, or game-over style states depending on the snapshot.

## Mod Metadata In Saves

Saves record active mod metadata so vanilla and modded profiles do not accidentally collide.

```mermaid
flowchart TB
    selected[Selected mod layers]
    namespace[content namespace]
    manifest[Mod manifest entries]
    save[Run/account save metadata]
    continue[Continue compatibility checks]

    selected --> namespace
    selected --> manifest
    namespace --> save
    manifest --> save
    save --> continue
```

When changing mod identity or save-sensitive ids, think about existing saves.

## Account Progression

Account progression is separate from a single run. It includes things like account level, skill points, inventory, and equipped items.

```mermaid
flowchart LR
    victory[Run result / rewards]
    progression[Account progression model]
    inventory[Inventory and equipment]
    disk[progression save]
    next[Next run start]

    victory --> progression
    inventory --> progression
    progression --> disk
    disk --> next
```

Equipped item effects currently apply at run start/restart, not mid-run.

## Persistence Change Checklist

- Is this run state, account state, user setting, or content default?
- Does it belong in `Assets/` or the platform data folder?
- Does it need backward-compatible defaults?
- Does it need mod namespace or manifest metadata?
- Does `mod_check` need to protect ids referenced by saves?
- Can missing or malformed saves fall back safely?
