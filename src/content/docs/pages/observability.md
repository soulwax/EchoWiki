---
title: "Observability"
---

## `src/logging.rs`

EchoWarrior uses `tracing` for structured logging.

`logging::init()` installs:

- a stderr formatting layer controlled by `RUST_LOG`
- a custom ring-buffer layer that stores the last 50 formatted events

The returned `LogBuffer` is cheap to clone and is passed into the runtime so the F1 debug overlay can show recent messages.

## Log Buffer Behavior

`LogBuffer` stores lines in a `VecDeque` behind `Arc<Mutex<_>>`.

Important details:

- capacity is `LOG_CAPACITY = 50`
- `snapshot()` returns oldest-to-newest lines
- `last()` returns the newest line
- poisoned locks return empty/no value instead of panicking
- initializing logging twice prints a stderr notice but does not crash

This follows the project-wide graceful degradation rule: debug tooling must not take down the game.

## `src/perf.rs`

`src/perf.rs` provides debug-only timing scopes:

```rust
perf_scope!("runtime.update");
perf_scope!("asset_pack.discovery", 12.0);
```

In debug builds, a `PerfScope` logs a throttled warning through `tracing` when elapsed time exceeds the budget. In release builds, the same API compiles to no work.

The default budget is 4 ms and can be changed with:

```powershell
$env:ECHO_WARRIOR_PERF_WARN_MS = "8"
```

Warnings use the `echo_warrior::perf` target, so they appear in stderr and the F1 debug overlay.

## When To Add A Scope

Add `perf_scope!` around expensive debug paths such as:

- asset loading
- pack discovery or verification
- save load/write
- Lua dispatch
- weather/render preparation
- pathfinding or broadphase code

Keep scopes coarse enough to explain a slowdown without flooding logs.
