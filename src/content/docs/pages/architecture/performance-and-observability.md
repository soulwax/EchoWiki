---
title: "14. Performance And Observability"
---

EchoWarrior aims for dense swarms, readable effects, hot-reloadable content, and fast iteration. Performance and observability are part of the architecture because contributors need to see problems early.

## Observability Stack

```mermaid
flowchart TB
    tracing[tracing events]
    stderr[stderr fmt layer]
    ring[LogBuffer ring, last 50]
    debug[F1 debug overlay]
    perf[perf_scope warnings]
    tools[CLI output]

    tracing --> stderr
    tracing --> ring --> debug
    perf --> tracing
    tools --> stderr
```

`logging::init()` sends logs to stderr and to the in-memory ring buffer used by the debug overlay.

## Ship Trace Profile

The dist scripts build shipped binaries with the `speed_trace` cargo profile: release-grade optimization plus out-of-line debug information for external profilers.

```mermaid
flowchart TB
    speed[speed_trace profile]
    release[release optimizations]
    debuginfo[full debug info]
    split[split debuginfo packed]
    binary[lean staged binary]
    symbols[PDB or DWARF side file]
    traces[ETW WPA Tracy Superluminal perf]

    speed --> release --> binary
    speed --> debuginfo --> split
    split --> symbols
    binary --> traces
    symbols --> traces
```

The symbol side files stay in `target/` on the build machine and are not staged into the zip packages. That keeps package size stable while preserving trace readability.

## Performance Scope Flow

```mermaid
sequenceDiagram
    participant Code as Instrumented code
    participant Scope as perf_scope
    participant Drop as Drop handler
    participant Trace as tracing warn
    participant Overlay as F1 logs

    Code->>Scope: create scope
    Code->>Code: run expensive block
    Scope->>Drop: elapsed on drop
    alt elapsed exceeds budget and throttle allows
        Drop->>Trace: warn target echo_warrior::perf
        Trace->>Overlay: retained in log buffer
    end
```

Scopes are debug-only. Release builds keep the API but do no timing work.

## Hot Paths To Treat Carefully

| Area | Typical risk |
| --- | --- |
| rendering loops | draw-call churn, texture switching, overdraw |
| spatial queries | repeated O(n) scans in dense swarms |
| pathfinding | per-companion allocation or excessive repathing |
| asset loading | blocking decode, repeated failed loads |
| Lua hooks | recompiling or re-executing too often |
| save writes | frequent disk I/O or non-atomic writes |
| weather/post-processing | oversized render targets or expensive shader passes |

## Performance Question Flow

```mermaid
flowchart TD
    slow[Something feels slow]
    visible{Visible in logs/F1?}
    scope[Add or inspect perf_scope]
    isolate[Reproduce with one feature/toggle]
    ownership{Runtime, pure logic, data, or asset?}
    fix[Make focused fix]
    verify[Run targeted command / smoke test]

    slow --> visible
    visible -- yes --> isolate
    visible -- no --> scope --> isolate
    isolate --> ownership --> fix --> verify
```

For release-performance investigations, use the packaged binary path:

```mermaid
flowchart TB
    dist[run dist script]
    package[launch shipped package]
    capture[capture ETW WPA Tracy or perf trace]
    symbolize[match trace with target side symbols]
    hot[identify the hot area]
    fix[focused fix]
    compare[rebuild and compare]

    dist --> package --> capture --> symbolize --> hot --> fix --> compare
```

## Contributor Guidance

When optimizing:

- keep behavior stable unless the task asks otherwise
- measure before and after when practical
- avoid broad rewrites as a first move
- prefer batching/caching/reuse over cleverness
- document the motivation if the optimization changes architecture

When adding expensive code:

- consider `perf_scope!`
- think about debug build cost
- keep allocations out of per-entity hot loops
- avoid repeated disk reads or script recompiles per frame
