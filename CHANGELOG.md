# Changelog

## [v1.0.9] - 2026-07-08

Release type: PATCH

- Added a Vulkan renderer path chapter that explains the staged move from Macroquad draw calls toward `Renderer2d` and the standalone [soulwax/vk2d](https://github.com/soulwax/vk2d) renderer.
- Added a beginner tutorial for moving one small draw site behind the renderer boundary without touching Vulkan directly.
- Updated the architecture chapter, module boundaries, code map, glossary, and wiki map so contributors can discover `src/render.rs`, `src/runtime/renderer_mq.rs`, `src/bin/wgpu_probe.rs`, and the `crates/vk2d` checkout.

## [v1.0.8] - 2026-07-06

Release type: PATCH

- Refined Mermaid flowchart edge-label styling so small connector captions such as `yes` and `no` render as clean gold text instead of clipped background chips.
- Made Mermaid edge-label backgrounds transparent at both theme and CSS layers, with visible foreign-object overflow and a subtle diagram-surface halo for readability.

## [v1.0.7] - 2026-07-05

Release type: PATCH

- Added a dedicated ECS lifecycle hot-lane chapter that documents the current cold full snapshot path and batched dynamic enemy sync.
- Updated architecture, runtime, migration, performance, and glossary pages to reflect the new `sync_enemies_dynamic()` bridge contract.
- Clarified contributor rules for extending mirrored enemy state without reintroducing per-frame static-data cloning or duplicate entity ownership.

## [v1.0.6] - 2026-07-05

Release type: PATCH

- Restored Mermaid sequence participant label contrast by targeting generated actor `tspan` text nodes directly.
- Aligned Mermaid's actor, signal, and label seed colors with the dark wiki diagram surface so participant boxes do not render with hidden text.
- Kept wide diagram frames inside the article lane while allowing natural-width sequence diagrams to scroll inside the surface instead of overlapping side navigation.

## [v1.0.5] - 2026-07-05

Release type: PATCH

- Refined Mermaid flowchart rendering with broader wide-layout detection, contained scaling for medium graphs, and clearer connector-label styling.
- Reshaped the runtime data command pipeline diagrams that Mermaid previously rendered as oversized horizontal fans.

## [v1.0.4] - 2026-07-05

Release type: PATCH

- Improved Mermaid sequence diagram rendering so wide participant flows get a broader responsive surface and wrapped labels instead of cramped actor boxes.
- Split sequence actor text styling from actor box and lifeline styling to prevent hollow or visually empty participant labels.

## [v1.0.3] - 2026-07-05

Release type: PATCH

- Expanded the Soundgarden chapter with contributor-facing pages for the audio CLI contract, mod authoring overlays, audition playback, and safe first contribution slices.
- Updated the existing Soundgarden pages to reflect the current split between available Tauri/TypeScript editor code and the still-missing game-side `audio` CLI in this checkout.

## [v1.0.2] - 2026-07-05

Release type: PATCH

- Fixed sequence and flowchart diagrams whose identifiers or labels collided with Mermaid grammar keywords across the runtime, architecture, automation, and Leitmotif pages.
- Added reserved-identifier checks so Mermaid grammar collisions fail the wiki audit before deployment.

## [v1.0.1] - 2026-07-05

Release type: PATCH

- Restored Mermaid diagram readability by removing nested presentation frames and preserving each graph's natural dimensions inside a responsive scrolling surface.
- Refined both themes with restrained neon accents, subtle connector glow, and high-contrast node styling without overpowering the documentation.
