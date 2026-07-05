#!/usr/bin/env python3
"""Audit EchoWiki structure, sidebar coverage, and graph density.

The script is intentionally dependency-free so it can run in a fresh checkout.
It does not try to replace Astro/Starlight validation. It catches contributor
documentation workflow issues that are easy to miss by eye:

- pages without frontmatter titles
- sidebar slugs that do not resolve to docs pages
- docs pages that are not present in the sidebar
- complex architecture pages with too few Mermaid diagrams

By default warnings do not fail the command. Use --strict when the wiki is ready
to enforce warning-free graph coverage.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


DOCS_ROOT = Path("src/content/docs")
SIDEBAR_FILE = Path("astro.config.mjs")
COMPLEX_TERMS = {
    "architecture",
    "runtime",
    "asset",
    "pack",
    "mod",
    "command",
    "choreography",
    "simulation",
    "ecs",
    "release",
    "protection",
    "tamper",
    "pipeline",
    "integrity",
}
RISKY_SEQUENCE_LABEL_CHARS = re.compile(r"[/:*().<>]")
MERMAID_SEQUENCE_KEYWORDS = {
    "activate",
    "actor",
    "alt",
    "and",
    "autonumber",
    "break",
    "critical",
    "deactivate",
    "else",
    "end",
    "loop",
    "note",
    "opt",
    "option",
    "par",
    "participant",
    "rect",
}
MERMAID_FLOWCHART_KEYWORDS = {
    "call",
    "class",
    "classdef",
    "click",
    "direction",
    "end",
    "flowchart",
    "graph",
    "linkstyle",
    "style",
    "subgraph",
}


@dataclass
class PageReport:
    slug: str
    path: str
    title: str | None
    diagrams: int
    headings: int
    internal_links: int
    complex_score: int
    in_sidebar: bool


@dataclass
class AuditReport:
    pages: list[PageReport]
    errors: list[str]
    warnings: list[str]


def slug_for_path(path: Path, docs_root: Path) -> str:
    relative = path.relative_to(docs_root).with_suffix("")
    parts = list(relative.parts)
    if parts == ["index"]:
        return ""
    if parts[-1] == "index":
        parts = parts[:-1]
    return "/".join(parts).replace("\\", "/")


def frontmatter_title(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    frontmatter = text[3:end]
    match = re.search(r"(?m)^title:\s*[\"']?(.+?)[\"']?\s*$", frontmatter)
    return match.group(1).strip() if match else None


def sidebar_slugs(config_text: str) -> set[str]:
    slugs = set(re.findall(r"slug:\s*['\"]([^'\"]+)['\"]", config_text))
    links = re.findall(r"link:\s*['\"]([^'\"]+)['\"]", config_text)
    for link in links:
        if link == "/":
            slugs.add("")
        elif link.startswith("/"):
            slugs.add(link.strip("/"))
    return slugs


def internal_link_count(text: str) -> int:
    count = 0
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip()
        if (
            target.startswith("http://")
            or target.startswith("https://")
            or target.startswith("mailto:")
            or target.startswith("#")
        ):
            continue
        count += 1
    return count


def complex_score(slug: str, title: str | None, text: str) -> int:
    haystack = f"{slug} {title or ''} {text[:4000]}".lower()
    return sum(1 for term in COMPLEX_TERMS if term in haystack)


def risky_sequence_participants(text: str) -> list[tuple[int, str, str]]:
    findings: list[tuple[int, str, str]] = []
    in_mermaid = False
    in_sequence = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_mermaid and stripped == "```mermaid":
                in_mermaid = True
                in_sequence = False
                continue
            if in_mermaid:
                in_mermaid = False
                in_sequence = False
                continue
        if not in_mermaid:
            continue
        if stripped == "sequenceDiagram":
            in_sequence = True
            continue
        if not in_sequence or not stripped.startswith("participant "):
            continue
        declaration = stripped.removeprefix("participant ").strip()
        identifier, separator, label = declaration.partition(" as ")
        if identifier.lower() in MERMAID_SEQUENCE_KEYWORDS:
            findings.append((line_number, identifier, "reserved identifier"))
        if separator:
            display_label = label.strip().strip('"')
            if RISKY_SEQUENCE_LABEL_CHARS.search(display_label):
                findings.append((line_number, display_label, "risky label punctuation"))
    return findings


def risky_flowchart_nodes(text: str) -> list[tuple[int, str, str]]:
    findings: list[tuple[int, str, str]] = []
    in_mermaid = False
    in_flowchart = False
    node_pattern = re.compile(r"^([A-Za-z_][\w-]*)\s*([\[{])(.*)([\]}])$")
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_mermaid and stripped == "```mermaid":
                in_mermaid = True
                in_flowchart = False
                continue
            if in_mermaid:
                in_mermaid = False
                in_flowchart = False
                continue
        if not in_mermaid:
            continue
        if stripped.startswith(("flowchart ", "graph ")):
            in_flowchart = True
            continue
        if not in_flowchart:
            continue
        match = node_pattern.match(stripped)
        if not match:
            continue
        identifier, _, label, _ = match.groups()
        if identifier.lower() in MERMAID_FLOWCHART_KEYWORDS:
            findings.append((line_number, identifier, "reserved identifier"))
        if "(" in label and not label.startswith('"'):
            findings.append((line_number, label, "unquoted grammar punctuation"))
    return findings


def audit(root: Path, min_complex_diagrams: int) -> AuditReport:
    docs_root = root / DOCS_ROOT
    sidebar_file = root / SIDEBAR_FILE
    errors: list[str] = []
    warnings: list[str] = []

    if not docs_root.exists():
        return AuditReport([], [f"missing docs root: {docs_root}"], [])
    if not sidebar_file.exists():
        return AuditReport([], [f"missing sidebar config: {sidebar_file}"], [])

    sidebar = sidebar_slugs(sidebar_file.read_text(encoding="utf-8"))
    pages: list[PageReport] = []
    page_slugs: set[str] = set()

    for path in sorted(docs_root.rglob("*")):
        if path.suffix not in {".md", ".mdx"}:
            continue
        text = path.read_text(encoding="utf-8")
        slug = slug_for_path(path, docs_root)
        page_slugs.add(slug)
        title = frontmatter_title(text)
        diagrams = len(re.findall(r"```mermaid\b", text))
        headings = len(re.findall(r"(?m)^#{2,6}\s+", text))
        links = internal_link_count(text)
        score = complex_score(slug, title, text)
        in_sidebar = slug in sidebar
        pages.append(
            PageReport(
                slug=slug or "/",
                path=str(path.relative_to(root)).replace("\\", "/"),
                title=title,
                diagrams=diagrams,
                headings=headings,
                internal_links=links,
                complex_score=score,
                in_sidebar=in_sidebar,
            )
        )

        if title is None:
            errors.append(f"{slug or '/'}: missing frontmatter title")
        for line_number, label, reason in risky_sequence_participants(text):
            errors.append(
                f"{slug or '/'}:{line_number}: sequence participant '{label}' "
                f"uses Mermaid-{reason}"
            )
        for line_number, label, reason in risky_flowchart_nodes(text):
            errors.append(
                f"{slug or '/'}:{line_number}: flowchart node '{label}' "
                f"uses Mermaid-{reason}"
            )
        if slug.startswith("pages/architecture") and score >= 3 and diagrams < min_complex_diagrams:
            warnings.append(
                f"{slug}: complex architecture page has {diagrams} diagram(s); "
                f"target is {min_complex_diagrams}+"
            )

    for slug in sorted(sidebar - page_slugs):
        errors.append(f"sidebar slug has no page: {slug or '/'}")

    for slug in sorted(page_slugs - sidebar):
        # Some pages are intentionally reachable only from local page links, but
        # surfacing them keeps the sidebar chapter structure honest.
        if slug.startswith("pages/"):
            warnings.append(f"page is not in sidebar: {slug}")

    return AuditReport(pages, errors, warnings)


def print_human(report: AuditReport) -> None:
    total_diagrams = sum(page.diagrams for page in report.pages)
    print(f"EchoWiki audit: {len(report.pages)} page(s), {total_diagrams} Mermaid diagram(s)")
    print()

    if report.errors:
        print("Errors")
        for error in report.errors:
            print(f"  - {error}")
        print()

    if report.warnings:
        print("Warnings")
        for warning in report.warnings:
            print(f"  - {warning}")
        print()

    densest = sorted(report.pages, key=lambda page: page.diagrams, reverse=True)[:8]
    print("Most graphed pages")
    for page in densest:
        print(f"  - {page.slug}: {page.diagrams} diagram(s)")

    no_graphs = [
        page
        for page in report.pages
        if page.slug.startswith("pages/architecture")
        and page.complex_score >= 3
        and page.diagrams == 0
    ]
    if no_graphs:
        print()
        print("Architecture pages with no diagrams")
        for page in no_graphs[:12]:
            print(f"  - {page.slug}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit EchoWiki contributor docs.")
    parser.add_argument("--root", default=".", help="wiki root, default: current directory")
    parser.add_argument(
        "--min-complex-diagrams",
        type=int,
        default=2,
        help="target diagram count for complex architecture pages",
    )
    parser.add_argument("--json", action="store_true", help="print JSON report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as failures in addition to errors",
    )
    args = parser.parse_args()

    report = audit(Path(args.root).resolve(), args.min_complex_diagrams)
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print_human(report)

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
