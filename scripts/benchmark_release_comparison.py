#!/usr/bin/env python3
"""Generate static SVG charts for the release benchmark comparison page.

Run from either the EchoWiki submodule or the EchoWarrior repo root. The
default inputs are the benchmark CSVs referenced by the 2026-07-15 wiki page:

- old v0.73.4 Macroquad release/debug from the bench-builds workspace
- v0.74.8 release from AppData, the last pure-Macroquad release run before
  the newest pair
- v0.74.9 debug + speed_trace release executable runs from AppData

The output is intentionally static SVG + JSON so Vercel can serve the page
without client-side chart code.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
GAME_ROOT = Path(__file__).resolve().parents[3]
APPDATA = Path(os.environ.get("APPDATA", ""))


@dataclass
class SeriesSpec:
    key: str
    label: str
    path: Path
    color: str
    dash: str = ""


@dataclass
class Run:
    spec: SeriesSpec
    meta: dict[str, str]
    summary: dict[str, str]
    rows: list[dict[str, float]]


SPECS = [
    SeriesSpec(
        "old_release",
        "v0.73.4 old Macroquad release",
        GAME_ROOT
        / ".claude/skills/bench-builds-workspace/iteration-1/full-ladder-release-vs-debug/without_skill/outputs/release_stress-1783954142.csv",
        "#f1c56b",
    ),
    SeriesSpec(
        "old_debug",
        "v0.73.4 old Macroquad debug",
        GAME_ROOT
        / ".claude/skills/bench-builds-workspace/iteration-1/full-ladder-release-vs-debug/with_skill/outputs/stress-debug.csv",
        "#b792ff",
    ),
    SeriesSpec(
        "prior_pure_release",
        "v0.74.8 prior pure-Macroquad release",
        APPDATA / "EchoWarrior/benchmarks/stress-1784129892.csv",
        "#e08a48",
        "7 5",
    ),
    SeriesSpec(
        "new_debug",
        "v0.74.9 debug executable",
        APPDATA / "EchoWarrior/benchmarks/stress-1784140024.csv",
        "#78a8ff",
    ),
    SeriesSpec(
        "new_release",
        "v0.74.9 speed_trace release executable",
        APPDATA / "EchoWarrior/benchmarks/stress-1784140795.csv",
        "#64dcc5",
    ),
]


def parse_kv_comment(line: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for chunk in line.lstrip("#").split(","):
        if "=" in chunk:
            key, _, value = chunk.partition("=")
            key = key.strip()
            if ":" in key:
                key = key.rpartition(":")[2].strip()
            out[key] = value.strip()
    return out


def load_run(spec: SeriesSpec) -> Run:
    if not spec.path.exists():
        raise FileNotFoundError(spec.path)
    meta: dict[str, str] = {}
    summary: dict[str, str] = {}
    rows: list[dict[str, float]] = []
    with spec.path.open(encoding="utf-8", newline="") as handle:
        data_lines: list[str] = []
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                kv = parse_kv_comment(line)
                if "summary:" in line or "smooth_60_up_to" in kv:
                    summary.update(kv)
                else:
                    meta.update(kv)
            else:
                data_lines.append(line)
        reader = csv.DictReader(data_lines)
        for row in reader:
            rows.append(
                {
                    "entities": float(row["entities"]),
                    "avg_ms": float(row["avg_ms"]),
                    "p95_ms": float(row["p95_ms"]),
                    "p99_ms": float(row["p99_ms"]),
                    "avg_fps": float(row["avg_fps"]),
                    "draw_calls": float(row["draw_calls"]),
                }
            )
    return Run(spec, meta, summary, rows)


def log_scale(value: float, lo: float, hi: float, start: float, end: float) -> float:
    lvalue = math.log10(value)
    llo = math.log10(lo)
    lhi = math.log10(hi)
    return start + (lvalue - llo) / (lhi - llo) * (end - start)


def linear_scale(value: float, lo: float, hi: float, start: float, end: float) -> float:
    return start + (value - lo) / (hi - lo) * (end - start)


def svg_header(width: int, height: int, title: str, subtitle: str = "") -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        "<defs>",
        '<linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0" stop-color="#10181c"/>',
        '<stop offset="1" stop-color="#0d1118"/>',
        "</linearGradient>",
        '<filter id="glow" x="-25%" y="-25%" width="150%" height="150%">',
        '<feGaussianBlur stdDeviation="2.2" result="blur"/>',
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        "</filter>",
        "</defs>",
        '<rect width="100%" height="100%" rx="14" fill="url(#panel)"/>',
        '<rect x="0.5" y="0.5" width="99.9%" height="99.9%" rx="14" fill="none" stroke="#2d5552"/>',
        f'<text x="34" y="42" fill="#f7efe4" font-size="22" font-weight="700" font-family="Inter, Segoe UI, sans-serif">{title}</text>',
    ] + (
        [
            f'<text x="34" y="68" fill="#8aa09f" font-size="13" font-family="Inter, Segoe UI, sans-serif">{subtitle}</text>'
        ]
        if subtitle
        else []
    )


def add_legend(parts: list[str], runs: list[Run], x: int, y: int) -> None:
    for index, run in enumerate(runs):
        yy = y + index * 23
        dash = f' stroke-dasharray="{run.spec.dash}"' if run.spec.dash else ""
        parts.append(
            f'<line x1="{x}" y1="{yy}" x2="{x + 34}" y2="{yy}" stroke="{run.spec.color}" stroke-width="3"{dash}/>'
        )
        parts.append(
            f'<text x="{x + 44}" y="{yy + 4}" fill="#dce8e5" font-size="12" font-family="Inter, Segoe UI, sans-serif">{run.spec.label}</text>'
        )


def line_chart(
    runs: list[Run],
    metric: str,
    out: Path,
    title: str,
    subtitle: str,
    y_label: str,
    y_min: float,
    y_max: float,
    y_log: bool = False,
    thresholds: Iterable[tuple[float, str]] = (),
) -> None:
    width, height = 1160, 660
    left, right, top, bottom = 88, 930, 92, 565
    x_min, x_max = 1.0, 100_000.0
    parts = svg_header(width, height, title, subtitle)
    parts.append(f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" fill="#0b1215" stroke="#213a3b"/>')

    x_ticks = [1, 10, 100, 1000, 10000, 100000]
    y_ticks = [4, 8.33, 16.67, 33.33, 66.67, 120] if y_log else [0, 20, 40, 60, 80, 100, 120]
    for tick in x_ticks:
        x = log_scale(tick, x_min, x_max, left, right)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="#172b2e"/>')
        label = f"{tick//1000}k" if tick >= 1000 else str(tick)
        parts.append(f'<text x="{x:.1f}" y="{bottom+26}" fill="#8aa09f" font-size="12" text-anchor="middle" font-family="Inter, Segoe UI, sans-serif">{label}</text>')
    for tick in y_ticks:
        if tick < y_min or tick > y_max:
            continue
        y = (
            log_scale(tick, y_min, y_max, bottom, top)
            if y_log
            else linear_scale(tick, y_min, y_max, bottom, top)
        )
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#172b2e"/>')
        parts.append(f'<text x="{left-12}" y="{y+4:.1f}" fill="#8aa09f" font-size="12" text-anchor="end" font-family="Inter, Segoe UI, sans-serif">{tick:g}</text>')
    for value, label in thresholds:
        y = (
            log_scale(value, y_min, y_max, bottom, top)
            if y_log
            else linear_scale(value, y_min, y_max, bottom, top)
        )
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#d8a85d" stroke-width="1.3" stroke-dasharray="5 6"/>')
        parts.append(f'<text x="{right+12}" y="{y+4:.1f}" fill="#d8a85d" font-size="12" font-family="Inter, Segoe UI, sans-serif">{label}</text>')

    for run in runs:
        pts: list[str] = []
        for row in run.rows:
            x = log_scale(row["entities"], x_min, x_max, left, right)
            value = row[metric]
            y = (
                log_scale(value, y_min, y_max, bottom, top)
                if y_log
                else linear_scale(value, y_min, y_max, bottom, top)
            )
            pts.append(f"{x:.1f},{y:.1f}")
        dash = f' stroke-dasharray="{run.spec.dash}"' if run.spec.dash else ""
        parts.append(
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{run.spec.color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)"{dash}/>'
        )
        for row in run.rows:
            x = log_scale(row["entities"], x_min, x_max, left, right)
            value = row[metric]
            y = (
                log_scale(value, y_min, y_max, bottom, top)
                if y_log
                else linear_scale(value, y_min, y_max, bottom, top)
            )
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{run.spec.color}" stroke="#081014"/>')
        last = run.rows[-1]
        if last["entities"] < 100_000:
            x = log_scale(last["entities"], x_min, x_max, left, right)
            y = (
                log_scale(last[metric], y_min, y_max, bottom, top)
                if y_log
                else linear_scale(last[metric], y_min, y_max, bottom, top)
            )
            parts.append(f'<text x="{x+8:.1f}" y="{y-8:.1f}" fill="{run.spec.color}" font-size="12" font-family="Inter, Segoe UI, sans-serif">partial</text>')

    parts.append(f'<text x="{(left+right)/2}" y="{height-30}" fill="#bac9c8" font-size="13" text-anchor="middle" font-family="Inter, Segoe UI, sans-serif">enemy entities (log scale)</text>')
    parts.append(f'<text transform="translate(28 {(top+bottom)/2}) rotate(-90)" fill="#bac9c8" font-size="13" text-anchor="middle" font-family="Inter, Segoe UI, sans-serif">{y_label}</text>')
    add_legend(parts, runs, 950, 116)
    parts.append("</svg>")
    out.write_text("\n".join(parts), encoding="utf-8")


def ratio_chart(runs: list[Run], out: Path) -> None:
    baseline = next(run for run in runs if run.spec.key == "old_release")
    baseline_by_stage = {int(row["entities"]): row for row in baseline.rows}
    compare = [run for run in runs if run.spec.key in {"prior_pure_release", "new_release"}]
    width, height = 1160, 560
    left, right, top, bottom = 88, 930, 90, 470
    parts = svg_header(
        width,
        height,
        "Release Ratio To Old Macroquad Baseline",
        "1.0 is equal. Lower is faster than v0.73.4 old Macroquad release; higher is slower.",
    )
    parts.append(f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" fill="#0b1215" stroke="#213a3b"/>')
    x_min, x_max = 1.0, 100_000.0
    y_min, y_max = 0.55, 1.55
    for tick in [1, 10, 100, 1000, 10000, 100000]:
        x = log_scale(tick, x_min, x_max, left, right)
        label = f"{tick//1000}k" if tick >= 1000 else str(tick)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="#172b2e"/>')
        parts.append(f'<text x="{x:.1f}" y="{bottom+26}" fill="#8aa09f" font-size="12" text-anchor="middle" font-family="Inter, Segoe UI, sans-serif">{label}</text>')
    for tick in [0.6, 0.8, 1.0, 1.2, 1.4]:
        y = linear_scale(tick, y_min, y_max, bottom, top)
        color = "#d8a85d" if tick == 1.0 else "#172b2e"
        dash = ' stroke-dasharray="5 6"' if tick == 1.0 else ""
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{color}"{dash}/>')
        parts.append(f'<text x="{left-12}" y="{y+4:.1f}" fill="#8aa09f" font-size="12" text-anchor="end" font-family="Inter, Segoe UI, sans-serif">{tick:.1f}</text>')
    for run in compare:
        pts: list[str] = []
        for row in run.rows:
            entities = int(row["entities"])
            if entities not in baseline_by_stage:
                continue
            ratio = row["avg_ms"] / baseline_by_stage[entities]["avg_ms"]
            x = log_scale(entities, x_min, x_max, left, right)
            y = linear_scale(ratio, y_min, y_max, bottom, top)
            pts.append(f"{x:.1f},{y:.1f}")
        dash = f' stroke-dasharray="{run.spec.dash}"' if run.spec.dash else ""
        parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{run.spec.color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)"{dash}/>')
    add_legend(parts, [baseline] + compare, 950, 120)
    parts.append(f'<text x="{(left+right)/2}" y="{height-34}" fill="#bac9c8" font-size="13" text-anchor="middle" font-family="Inter, Segoe UI, sans-serif">enemy entities (log scale)</text>')
    parts.append("</svg>")
    out.write_text("\n".join(parts), encoding="utf-8")


def summary_chart(runs: list[Run], out: Path) -> None:
    width, height = 1160, 520
    parts = svg_header(width, height, "Smooth Ceilings And Top Stage", "Bars show the largest stage each run kept under 60 fps and 120 fps; labels show the last measured stage.")
    x0, y0 = 92, 120
    chart_w = 760
    row_h = 62
    max_entities = 100_000
    for index, run in enumerate(runs):
        y = y0 + index * row_h
        parts.append(f'<text x="{x0}" y="{y}" fill="#f7efe4" font-size="13" font-weight="700" font-family="Inter, Segoe UI, sans-serif">{run.spec.label}</text>')
        for lane, (key, color) in enumerate((("smooth_60_up_to", "#64dcc5"), ("smooth_120_up_to", "#f1c56b"))):
            value = run.summary.get(key, "?")
            try:
                numeric = float(value)
            except ValueError:
                numeric = 0.0
            bar_y = y + 10 + lane * 18
            width_px = max(2.0, math.log10(max(numeric, 1.0)) / math.log10(max_entities) * chart_w)
            parts.append(f'<rect x="{x0}" y="{bar_y}" width="{chart_w}" height="10" rx="5" fill="#111b20"/>')
            parts.append(f'<rect x="{x0}" y="{bar_y}" width="{width_px:.1f}" height="10" rx="5" fill="{color}" opacity="0.86"/>')
            parts.append(f'<text x="{x0 + chart_w + 12}" y="{bar_y + 9}" fill="#bac9c8" font-size="12" font-family="Inter, Segoe UI, sans-serif">{key.replace("_up_to", "").replace("_", " ")}: {value}</text>')
        last = run.rows[-1]
        parts.append(f'<text x="{x0 + chart_w + 12}" y="{y + 54}" fill="{run.spec.color}" font-size="12" font-family="Inter, Segoe UI, sans-serif">last: {int(last["entities"]):,} @ {last["avg_ms"]:.1f} ms</text>')
    parts.append('<text x="92" y="482" fill="#8aa09f" font-size="12" font-family="Inter, Segoe UI, sans-serif">Scale is logarithmic by entity count; partial runs are still useful but should not be compared at missing stages.</text>')
    parts.append("</svg>")
    out.write_text("\n".join(parts), encoding="utf-8")


def export_json(runs: list[Run], out: Path) -> None:
    payload = []
    for run in runs:
        payload.append(
            {
                "key": run.spec.key,
                "label": run.spec.label,
                "source": str(run.spec.path),
                "meta": run.meta,
                "summary": run.summary,
                "rows": run.rows,
            }
        )
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    runs = [load_run(spec) for spec in SPECS]
    out_dir = ROOT / "public/benchmarks"
    out_dir.mkdir(parents=True, exist_ok=True)
    export_json(runs, out_dir / "release-comparison-data.json")
    line_chart(
        runs,
        "avg_ms",
        out_dir / "release-comparison-avg-ms.svg",
        "Average Frame Time Across The Stress Ladder",
        "Debug/release old Macroquad baselines vs the newest executable stress runs.",
        "avg frame time (ms, log scale)",
        3.0,
        160.0,
        y_log=True,
        thresholds=((8.33, "120 fps"), (16.67, "60 fps"), (33.33, "30 fps")),
    )
    line_chart(
        runs,
        "p95_ms",
        out_dir / "release-comparison-p95-ms.svg",
        "P95 Frame Time",
        "Tail latency shows hitch risk; the newest release improves mid-ladder but still has a high 50k/100k tail.",
        "p95 frame time (ms, log scale)",
        3.0,
        180.0,
        y_log=True,
        thresholds=((8.33, "120 fps"), (16.67, "60 fps"), (33.33, "30 fps")),
    )
    ratio_chart(runs, out_dir / "release-comparison-ratio.svg")
    summary_chart(runs, out_dir / "release-comparison-summary.svg")


if __name__ == "__main__":
    main()
