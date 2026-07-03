---
title: "Visual Orientation"
---

This page gives new contributors a quick visual map before they dive into code. Screenshots live in `public/`, so future captures can be added without changing the private game repository.

## Current Screens

<div class="visual-grid">
  <figure>
    <img src="/start_screen.png" alt="EchoWarrior start screen with rain, title, and menu options" />
    <figcaption>Start screen: the first contributor-facing frame for mood, menu flow, background atmosphere, and modded/unmodded entry state.</figcaption>
  </figure>
  <figure>
    <img src="/assets/readme-window.png" alt="Main EchoWarrior prototype screen with HUD and companions" />
    <figcaption>Main runtime: world simulation, companion labels, HUD, input hints, and gameplay stats in the Macroquad prototype.</figcaption>
  </figure>
  <figure>
    <img src="/shader_arena_1.png" alt="Shader arena showing a nova VFX preview and parameter sliders" />
    <figcaption>Shader arena: the clearest screen for VFX iteration, uniform sliders, effect icons, and runtime debug controls.</figcaption>
  </figure>
  <figure>
    <img src="/dialogue_1.png" alt="Dialogue overlay during a rainy scene with a speaker portrait" />
    <figcaption>Dialogue and choreography: authored scene beats over live gameplay, with speaker portraits and input prompts.</figcaption>
  </figure>
  <figure class="mark-figure">
    <img src="/Shisaku-2.png" alt="EchoWarrior combat identity mark" />
    <figcaption>Primary mark: useful for site identity, social previews, favicons, and future contributor-facing screenshots.</figcaption>
  </figure>
  <figure class="mark-figure">
    <img src="/Shisaku.png" alt="EchoWarrior lore identity mark" />
    <figcaption>Lore mark: a quieter library/candle variant that fits design notes, worldbuilding pages, and modding reference material.</figcaption>
  </figure>
</div>

## How To Read A Screenshot

When you add or review a screenshot, name the system it teaches. Good contributor screenshots usually clarify one of these:

| Screenshot focus | Relevant docs |
| --- | --- |
| HUD, overlays, labels, and effect draw order | [Rendering And UI](architecture/rendering-and-ui/) |
| Dialogue, story beats, gestures, and camera cues | [Choreography](architecture/choreography/) |
| Runtime asset loading and fallback behavior | [Assets And Packaging](assets-and-packaging/) |
| Mod-authored data changing visible gameplay | [Modding Boundary](modding-boundary/) |
| Debug panels, logs, counters, or diagnostics | [Observability](observability/) |

## Adding More Captures

Put public screenshots in:

```text
public/
```

Prefer short, descriptive lowercase names:

```text
public/shader_arena_2.png
public/dialogue_choice_1.png
public/start_screen_2.png
public/level_up_cards_1.png
```

Then reference them from Markdown with absolute paths:

```html
<img src="/shader_arena_2.png" alt="Shader arena showing chain lightning tuning controls" />
```

Use captions to explain why the screenshot matters to a contributor. A useful caption says which system is visible and what code or data boundary the reader should remember.
