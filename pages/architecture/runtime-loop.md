# 3. Runtime Loop

The playable prototype runs through Macroquad. `src/main.rs` calls `runtime::run().await`, and the runtime owns the frame loop.

## Frame Shape

At the highest level, each frame is:

```mermaid
sequenceDiagram
    participant MQ as Macroquad
    participant RT as PrototypeRuntime
    participant Input as runtime/input
    participant Game as src/game helpers
    participant UI as src/ui
    participant Draw as runtime draw paths

    MQ->>RT: next frame
    RT->>Input: handle_input()
    RT->>RT: update timers and mode state
    RT->>Game: call pure helpers where available
    RT->>RT: apply commands, scripts, saves, audio
    RT->>Draw: draw world, actors, effects
    RT->>UI: draw HUD, cards, dialogue, overlays
    RT->>MQ: present frame
```

## Runtime Modes

The runtime has a richer mode model than the library-side `AppState`.

```mermaid
stateDiagram-v2
    [*] --> StartScreen
    StartScreen --> StartTransition: Start Game
    StartScreen --> Playing: Continue saved run
    StartTransition --> Intro
    Intro --> Playing: dialogue handoff
    Playing --> LevelUp: XP threshold
    LevelUp --> Playing: choose card
    Playing --> Inventory: I / Tab
    Inventory --> Playing: close
    Playing --> Paused: Esc / P / controller menu
    Paused --> Playing: resume
    Playing --> DeathTransition: HP <= 0
    DeathTransition --> GameOver
    GameOver --> Playing: restart
    Playing --> Victory: configured clear condition
    Victory --> Playing: restart
```

Exact mode names evolve, but the architectural rule stays the same: simulation should only advance in modes that permit it.

## Inputs Become Intent

Input code should answer what the player requested, not own gameplay rules.

```mermaid
flowchart LR
    keyboard[Keyboard]
    mouse[Mouse]
    gamepad[Gamepad]
    input[runtime/input]
    runtime[PrototypeRuntime]
    state[Mode/state checks]

    keyboard --> input
    mouse --> input
    gamepad --> input
    input --> runtime
    runtime --> state
```

Examples:

- movement vector can be read in runtime
- level-up selection can update runtime mode state
- pure upgrade application should route through shared rule/data paths where practical

## Update Responsibilities

Runtime update owns:

- live actor positions used by drawing
- transient effects and particles
- audio playback decisions
- hot-reload polling
- Lua event dispatch timing
- save/autosave timing
- applying `GameCommand` effects to live state

Pure modules should own:

- deterministic calculations
- data models
- validation-friendly logic
- compact simulations used in tests

## Draw Responsibilities

```mermaid
flowchart TB
    camera[World camera]
    terrain[terrain and props]
    actors[player enemies NPCs]
    fx[VFX, particles, bloom]
    overlays[screen overlays]
    ui[HUD / dialogue / cards]

    camera --> terrain
    terrain --> actors
    actors --> fx
    fx --> overlays
    overlays --> ui
```

Keep world-space and screen-space drawing clear. If a label or hit-test needs manual projection, use the existing helpers instead of duplicating coordinate math.

## Common Runtime Change Risks

| Risk | Why it matters |
| --- | --- |
| updating simulation during pause/level-up | breaks player expectations and save state |
| duplicating pure rules in runtime | makes tests and modding drift |
| hardcoding stats in actors | bypasses `Assets/Data` and modding |
| loading a direct asset without pack discovery | works loose, fails in release |
| adding a separate scene/beat mechanism | conflicts with choreography |
