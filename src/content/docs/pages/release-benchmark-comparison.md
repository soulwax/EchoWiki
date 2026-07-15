---
title: "Release Benchmark Comparison"
---

This entry compares the old Macroquad stress baseline against the newest executable stress runs found from the benchmark search on 2026-07-15.

It is intentionally narrower than [Performance Benchmarks](benchmarks/). The goal here is not to rewrite the whole history; it is to answer one contributor question: "Did the newest debug and speed_trace release executables move the stress-ladder shape compared with the prior Macroquad baselines?"

## Source Selection

The local search for CSV files newer than `CLAUDE.md`, excluding `node_modules` and `target`, resolves to the bench-builds workspace:

| Role | CSV |
| --- | --- |
| old Macroquad debug | `.claude/skills/bench-builds-workspace/iteration-1/full-ladder-release-vs-debug/with_skill/outputs/stress-debug.csv` |
| old Macroquad release | `.claude/skills/bench-builds-workspace/iteration-1/full-ladder-release-vs-debug/without_skill/outputs/release_stress-1783954142.csv` |
| sibling old release check | `.claude/skills/bench-builds-workspace/iteration-1/full-ladder-release-vs-debug/with_skill/outputs/stress-release.csv` |

The AppData benchmark folder then supplies the newest executable runs:

| Role | CSV | Notes |
| --- | --- | --- |
| prior pure-Macroquad release | `%APPDATA%/EchoWarrior/benchmarks/stress-1784129892.csv` | v0.74.8 release, partial to 50k |
| newest debug executable | `%APPDATA%/EchoWarrior/benchmarks/stress-1784140024.csv` | v0.74.9 debug, partial to 50k |
| newest speed_trace release executable | `%APPDATA%/EchoWarrior/benchmarks/stress-1784140795.csv` | v0.74.9 release, full 100k ladder |

All selected CSVs report `vsync_suspected=false`, `render_scale 2.0`, bloom on, MSAA 4, and vsync off. Resolutions differ slightly: old v0.73.4 runs are `1584x861`, while the newest AppData runs are `1568x822`.

## Average Frame Time

<figure class="wide-figure">
  <img src="/benchmarks/release-comparison-avg-ms.svg" alt="Average frame time stress benchmark comparison across old Macroquad and new executable runs" />
  <figcaption>Average frame time over the stress ladder. The y axis is logarithmic so low-stage fixed GPU cost and high-stage horde cost are visible in the same graph.</figcaption>
</figure>

Reading the release lines:

- v0.74.9 speed_trace release is **24.5% faster than the v0.74.8 pure-Macroquad release at 10k**, **17.0% faster at 20k**, and **18.9% faster at 50k**.
- Compared with the older v0.73.4 release baseline, v0.74.9 release is roughly equal at 10k, then slower at the top: **+10.7% avg ms at 50k** and **+11.9% at 100k**.
- The newest debug executable is slower than the old debug baseline in the high common stages: **+13.1% at 10k**, **+12.8% at 20k**, and **+6.2% at 50k**.

That is the honest shape: the newest release looks clearly better than the immediately preceding pure-Macroquad release run, but not better than the older v0.73.4 release baseline at the heaviest stages. The code and rendering surface changed between these dates, so this page treats that as a tracking signal, not a final verdict.

## P95 Frame Time

<figure class="wide-figure">
  <img src="/benchmarks/release-comparison-p95-ms.svg" alt="P95 frame time stress benchmark comparison across old Macroquad and new executable runs" />
  <figcaption>P95 frame time shows hitch risk. The newest release improves the 10k to 20k mid-ladder against v0.74.8, but its 50k and 100k tail remains high.</figcaption>
</figure>

P95 is the more conservative read because the player feels hitches, not averages. The v0.74.9 release reaches 100k, but its tail is wider than the old v0.73.4 release baseline at the top of the ladder.

## Release Ratio

<figure class="wide-figure">
  <img src="/benchmarks/release-comparison-ratio.svg" alt="Release ratio chart comparing v0.74.8 and v0.74.9 release runs against the v0.73.4 old Macroquad release baseline" />
  <figcaption>Ratio against the old v0.73.4 Macroquad release. Below 1.0 is faster than the old baseline; above 1.0 is slower.</figcaption>
</figure>

This view makes the tradeoff sharper:

- v0.74.9 release crosses below 1.0 in the 10k region, then rises above the old baseline from 20k upward.
- v0.74.8 partial release was much slower than the old baseline at the 10k to 50k stages.
- The newest release recovered much of that v0.74.8 regression, but did not beat the old v0.73.4 top-end release row.

## Smooth Ceilings

<figure class="wide-figure">
  <img src="/benchmarks/release-comparison-summary.svg" alt="Smooth 60 and 120 fps ceiling comparison for selected stress benchmark runs" />
  <figcaption>All selected runs keep the 60 fps ceiling through at least 2k entities. Most release runs keep 120 fps through 1k; old debug only reports 500.</figcaption>
</figure>

The smooth-ceiling summary is reassuring for normal playtesting: every selected run holds 60 fps through 2,000 entities. The heavy-ladder differences matter for regression tracking and headroom, not because 50k to 100k enemies is expected gameplay density.

## Run Table

| run | build | stages | last stage | last avg ms | last p95 ms | smooth 60 | smooth 120 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| old Macroquad release | v0.73.4 release | 16 | 100,000 | 56.0 | 84.0 | 2,000 | 1,000 |
| old Macroquad debug | v0.73.4 debug | 16 | 100,000 | 95.1 | 113.0 | 2,000 | 500 |
| prior pure-Macroquad release | v0.74.8 release | 15 | 50,000 | 62.1 | 124.8 | 2,000 | 1,000 |
| newest debug executable | v0.74.9 debug | 15 | 50,000 | 77.5 | 89.5 | 2,000 | 1,000 |
| newest speed_trace release executable | v0.74.9 release | 16 | 100,000 | 62.7 | 113.7 | 2,000 | 1,000 |

Partial runs are not discarded here because they are exactly the files under investigation, but they are marked as partial in the charts and table. Do not compare missing 100k rows by interpolation.

## Rebuilding The Graphs

The generated assets are static files in `public/benchmarks/`:

- `release-comparison-avg-ms.svg`
- `release-comparison-p95-ms.svg`
- `release-comparison-ratio.svg`
- `release-comparison-summary.svg`
- `release-comparison-data.json`

Regenerate them from the wiki submodule when the same source files are present:

```powershell
cd Docs/Wiki
python3 scripts/benchmark_release_comparison.py
```

The script emits static SVG rather than JavaScript charts so Vercel can serve the page without a client-side plotting dependency.
