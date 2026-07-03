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

## Performance Scope Flow

```mermaid
sequenceDiagram
    participant Code as Instrumented code
    participant Scope as perf_scope
    participant Drop as Drop handler
    participant Trace as tracing::warn
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
