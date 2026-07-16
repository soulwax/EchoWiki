---
title: "10F. vk2d Optional Features"
---

This continues [10D. vk2d Standalone Quickstart](vk2d-standalone-quickstart/) and [10E. vk2d Materials And Shaders](vk2d-standalone-materials/). It covers the two Cargo feature flags `vk2d` exposes for consumers who want more than raw draw calls, plus the logical-resolution behavior every consumer inherits by default.

Both features are **off by default** — the core crate's dependency surface stays small unless you opt in.

```toml
[dependencies]
vk2d = { git = "https://github.com/soulwax/vk2d", rev = "<commit-sha>", features = ["egui", "winit-input"] }
```

## Fixed Logical Size + Upscale (Always On, No Feature Needed)

Before either optional feature, understand the one behavior every `vk2d` consumer gets automatically: `ContextConfig::logical_size` fixes the resolution your draw calls think in, independent of the actual window size.

```rust,no_run
# use vk2d::{Backend, ContextConfig};
# let window = unimplemented!();
# let _: Result<(), ()> = (|| {
let cfg = ContextConfig {
    logical_size: (320, 180), // draw calls use these coordinates
    prefer_backend: Backend::Vulkan,
};
Ok(())
# })();
```

Internally, `vk2d` renders your frame into an offscreen target at `logical_size`, then blits that target to the real window surface with a **Nearest** upscale. Two consequences worth knowing before you pick a `logical_size`:

- Pixel-art projects get crisp integer-ish scaling for free — draw at your art's native resolution and let the window be any size.
- Non-pixel-art projects (rendering photographic content or wanting smooth scaling) should pick a `logical_size` close to the expected window size, since the final blit is always Nearest, never Linear/bilinear.

Call `ctx.resize(width, height)` on every `WindowEvent::Resized` — this resizes the window-side swapchain/surface, not the logical scene target. Your draw call coordinates never need to change when the window is resized.

## `winit-input`: A Minimal Input Snapshot

Enables `vk2d::InputState`, a small keyboard/mouse tracker fed directly from `winit::event::WindowEvent`s. It exists so a minimal consumer doesn't need to hand-roll key-state bookkeeping just to ask "is Space held right now."

```toml
[dependencies]
vk2d = { git = "...", rev = "...", features = ["winit-input"] }
```

```rust,no_run
# use vk2d::InputState;
# use winit::event::WindowEvent;
# fn go(input: &mut InputState, event: &WindowEvent) {
input.feed(event);

if input.is_key_down("w") {
    // move forward every frame the key is held
}
if input.is_key_pressed("space") {
    // fires once, on the frame the key transitions to pressed
}
let (mx, my) = input.mouse_position();
# let _ = (mx, my);

// Call once per frame, after your own input-reading logic runs, so
// "pressed" (edge) state doesn't leak into the next frame.
input.end_frame();
# }
```

The three-method shape (`is_key_down` for held state, `is_key_pressed` for the single-frame edge, `mouse_position` for cursor position) covers the common case without pulling in a full input-mapping crate. It is intentionally minimal — anything beyond held/pressed/mouse-position (gamepad, key remapping, input buffering) is left to your own application code or another crate.

## `egui`: An Overlay Pass Over The Scene

Enables `vk2d::EguiOverlay` plus `Frame::present_with_egui`, painting an [egui](https://github.com/emilk/egui) immediate-mode UI overlay on top of the rendered scene, composited together in the same present call.

```toml
[dependencies]
vk2d = { git = "...", rev = "...", features = ["egui"] }
```

`vk2d` **re-exports** `egui` itself (`vk2d::egui::*`) rather than letting you pull in your own copy — this matters because `egui-wgpu`/`egui-winit` are version-pinned against the exact `wgpu` version `vk2d` links, and a mismatched `egui` version at your call site would not compile against `EguiOverlay`. Always build your UI code against `vk2d::egui`, not a separately-added `egui` dependency.

```rust,no_run
# use vk2d::{Context, EguiOverlay};
# fn setup(ctx: &Context, window: &winit::window::Window) -> EguiOverlay {
EguiOverlay::new(ctx.device(), window, ctx.surface_format())
# }
```

Feed it window events (so egui sees clicks/typing/hover) and paint each frame:

```rust,no_run
# use vk2d::EguiOverlay;
# use winit::event::WindowEvent;
# fn go(overlay: &mut EguiOverlay, window: &winit::window::Window, event: &WindowEvent) {
let consumed = overlay.on_window_event(window, event);
// If `consumed` is true, egui wants this event — skip your own game-input
// handling for it so a click on a UI panel doesn't also register as a
// world-space click.
# let _ = consumed;
# }
```

Then, instead of `frame.present()`, use the egui-aware present call so the overlay composites in the same GPU submission as the scene:

```rust,no_run
# use vk2d::{Context, Color, EguiOverlay};
# fn go(ctx: &mut Context, overlay: &mut EguiOverlay, window: &winit::window::Window) -> Result<(), vk2d::Vk2dError> {
let mut frame = ctx.begin_frame(Color::BLACK)?;
// ... game draw calls on `frame` ...
frame.present_with_egui(overlay, window, |egui_ctx| {
    vk2d::egui::Window::new("Debug").show(egui_ctx, |ui| {
        ui.label("hello from vk2d + egui");
    });
});
# Ok(())
# }
```

This is the same overlay pattern EchoWarrior's own F1 debug panel uses internally, minus any EchoWarrior-specific panel content — the mechanism is identical for a from-scratch consumer.

## Choosing Which Features You Need

| You want | Enable |
| --- | --- |
| Just sprites/shapes/text/materials, no UI, roll your own input | neither (default) |
| Keyboard/mouse held/pressed queries without hand-rolling event bookkeeping | `winit-input` |
| An in-app debug/tool panel drawn over the scene | `egui` |
| Both | `features = ["egui", "winit-input"]` |

Enabling a feature you don't use costs a slightly larger dependency tree and compile time, nothing at runtime beyond the unused code paths — but the crate defaults to neither specifically so a minimal consumer (a shader demo, a small tool) never pays for `egui`'s dependency weight unless it asks for it.
