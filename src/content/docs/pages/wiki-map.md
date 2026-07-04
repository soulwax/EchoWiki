---
title: "Wiki Map"
---

EchoWiki is organized like a contributor manual, not like a blog. The left sidebar is the main route through the material.

## How The Sidebar Works

The structure follows a documentation pattern used by mature engine manuals: first get oriented, then follow tutorials, then use the manual and reference sections when you need exact boundaries.

| Sidebar area | Use it when |
| --- | --- |
| Getting Started | You are new to the repository or trying to find the right door. |
| Tutorials | You want a guided feature slice or a concrete worked example. |
| Manual | You need the big-picture architecture and runtime system explanations. |
| Leitmotif | You want to work on the choreography authoring app and its screenshots. |
| Reference | You need exact file boundaries, tools, assets, and diagnostics. |
| Contributing And Operations | You are preparing a change, verifying it, or deploying the wiki. |

## Recommended Reading Paths

### First Hour

1. [Start Here](new-contributor-start/)
2. [Visual Orientation](visual-orientation/)
3. [Change Routes](change-routes/)
4. [Verification Guide](verification-guide/)

### First Tiny Feature

1. [Tiny Moddable Feature](guides/tiny-moddable-feature/)
2. [Data And Modding Flow](architecture/data-and-modding-flow/)
3. [Asset Loading Pipeline](asset-loading-pipeline/)
4. [Contribution Workflow](contribution-workflow/)

### Runtime Work

1. [Runtime Shell](runtime-shell/)
2. [Runtime Loop](architecture/runtime-loop/)
3. [Audio And Transitions](audio-and-transitions/)
4. [Rendering And UI](architecture/rendering-and-ui/)

### Tooling Or Release Work

1. [CLI Tools](cli-tools/)
2. [Assets And Packaging](assets-and-packaging/)
3. [Asset Pack Reference](asset-pack-reference/)
4. [Vercel Deployment](vercel-deployment/)

### Leitmotif Work

1. [Leitmotif Overview](leitmotif/)
2. [Leitmotif Screenshots](leitmotif/screenshots/)
3. [Leitmotif Getting Started](leitmotif/getting-started/)
4. [Leitmotif Usage](leitmotif/usage/)
5. [Leitmotif Moddability](leitmotif/moddability/)
6. [Leitmotif Architecture](leitmotif/architecture/)
7. [Leitmotif Contributor Slices](leitmotif/contributor-slices/)

## Page Granularity

Pages are intentionally small enough to answer one contributor question:

- "Where does this code live?"
- "What owns this behavior?"
- "Which data file should I edit?"
- "Which command verifies the change?"
- "What must degrade gracefully if content is missing?"

When adding a page, prefer a practical contributor route over a large essay. If a page starts covering more than one workflow, split it and add the new page under the right sidebar dropdown.
