---
title: "Logging And Perf Reference"
---

This page documents `src/logging.rs` and `src/perf.rs` as API surfaces.

## Logging Initialization

`logging::init()` installs the global tracing subscriber and returns a `LogBuffer`.

```rust
let logs = echo_warrior::logging::init();
```

The subscriber contains:

- `EnvFilter`, defaulting to `info`
- `fmt` stderr output
- `RingBufferLayer`, retaining the last 50 formatted events

Set logging verbosity with `RUST_LOG`:

```powershell
$env:RUST_LOG = "info,echo_warrior::perf=warn"
cargo run
```

## `LogBuffer`

`LogBuffer` is a cheap cloneable handle:

```rust
#[derive(Clone, Default)]
pub struct LogBuffer {
    lines: Arc<Mutex<VecDeque<String>>>,
}
```

Public methods:

| Method | Purpose |
| --- | --- |
| `snapshot()` | Returns retained lines oldest-first. |
| `last()` | Returns the newest retained line. |

Internal pushes drop the oldest line when the buffer reaches `LOG_CAPACITY`.

## Formatting

The ring layer stores messages as:

```text
[LEVEL] target: message fields...
```

Non-message tracing fields are appended as `key=value` debug fragments. The F1 overlay consumes these strings directly.

## Idempotent Startup

If another test or tool has already installed a global tracing subscriber, `logging::init()` swallows the `try_init` failure, prints a stderr note, and returns a detached `LogBuffer`.

That detached buffer will not receive tracing events, but startup will continue.

## Performance Scopes

Use the `perf_scope!` macro for debug-only timing:

```rust
perf_scope!("runtime.update");
perf_scope!("asset_pack.verify", 16.0);
```

The first form uses `perf::default_warn_after()`. The second form uses an explicit millisecond budget.

## Debug vs Release

In debug builds:

- scope creation records `Instant::now()`
- `Drop` compares elapsed time to the budget
- warnings are throttled per scope name for one second
- warnings go through `tracing::warn!` with target `echo_warrior::perf`

In release builds:

- `PerfScope` is empty
- `scope()` does no work
- `default_warn_after()` returns `Duration::ZERO`

This lets hot paths stay instrumented without shipping timing overhead.

## Environment Tuning

The default debug budget is 4 ms. Override it with:

```powershell
$env:ECHO_WARRIOR_PERF_WARN_MS = "10"
```

Invalid, non-finite, or non-positive values fall back to the default.
