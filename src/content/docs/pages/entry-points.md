---
title: "Entry Points"
---

## `src/main.rs`

`src/main.rs` is intentionally tiny. It declares the binary-private `runtime` module, passes the runtime window configuration into Macroquad, and runs the async runtime.

```rust
mod runtime;

fn window_conf() -> macroquad::prelude::Conf {
    runtime::window_conf()
}

#[macroquad::main(window_conf)]
async fn main() {
    if let Err(error) = runtime::run().await {
        eprintln!("{error}");
        runtime::show_error(&error).await;
    }
}
```

The important behavior is the error path: startup/runtime failures are printed to stderr and also shown through `runtime::show_error`, so a player or tester gets visible feedback instead of a silent close.

## `src/lib.rs`

`src/lib.rs` exposes the reusable crate modules:

```rust
pub mod app;
pub mod asset_pack;
pub mod assets;
pub mod data;
pub mod game;
pub mod logging;
pub mod modding;
pub mod perf;
pub mod save;
pub mod scripting;
pub mod states;
pub mod ui;
```

This is the boundary used by the command-line tools in `src/bin/` and by library tests. The runtime itself is binary-private because it is tied to Macroquad and should not leak into pure gameplay modules.

## Adding A New Top-Level Module

Only add a new `pub mod` in `src/lib.rs` when the code is genuinely shared outside the runtime binary. If the code imports Macroquad or exists only for frame rendering, it probably belongs under `src/runtime/`.

When adding a shared module, check:

- Does it stay renderer-agnostic?
- Is it covered by focused tests where practical?
- Does it need to be documented in this wiki or an existing subsystem doc?
- Does it introduce any runtime asset references that must be discovered by `asset_pack`?
