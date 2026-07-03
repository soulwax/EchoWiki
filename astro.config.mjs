import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import starlight from '@astrojs/starlight';

import remarkMermaid from './src/plugins/remark-mermaid.mjs';

const site =
  process.env.SITE ??
  (process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : process.env.VERCEL_URL
      ? `https://${process.env.VERCEL_URL}`
      : 'https://echo-wiki.vercel.app');

export default defineConfig({
  site,
  markdown: unified({
    remarkPlugins: [remarkMermaid],
  }),
  integrations: [
    starlight({
      title: 'EchoWarrior Wiki',
      description:
        'Contributor documentation for EchoWarrior architecture, modding routes, and main Rust code boundaries.',
      customCss: ['./src/styles/custom.css'],
      editLink: {
        baseUrl: 'https://github.com/soulwax/EchoWiki/edit/main/',
      },
      social: [
        {
          icon: 'github',
          label: 'EchoWiki on GitHub',
          href: 'https://github.com/soulwax/EchoWiki',
        },
      ],
      head: [
        {
          tag: 'script',
          attrs: { type: 'module' },
          content: `
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';

            mermaid.initialize({
              startOnLoad: false,
              theme: 'base',
              themeVariables: {
                primaryColor: '#fff7ed',
                primaryTextColor: '#172026',
                primaryBorderColor: '#c47a30',
                lineColor: '#5f6f73',
                secondaryColor: '#e9f5f1',
                tertiaryColor: '#f8fafc',
                fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif'
              }
            });

            async function renderMermaid() {
              const diagrams = document.querySelectorAll('.mermaid');
              if (!diagrams.length) return;
              await mermaid.run({ nodes: diagrams });
            }

            window.addEventListener('load', renderMermaid);
            document.addEventListener('astro:after-swap', renderMermaid);
          `,
        },
      ],
      sidebar: [
        {
          label: 'New Contributors',
          items: [
            { label: 'Start Here', slug: 'pages/new-contributor-start' },
            { label: 'Contribution Workflow', slug: 'pages/contribution-workflow' },
            { label: 'Change Routes', slug: 'pages/change-routes' },
            { label: 'Verification Guide', slug: 'pages/verification-guide' },
          ],
        },
        {
          label: 'Guided Implementation',
          items: [
            { label: 'Tiny Moddable Feature', slug: 'pages/guides/tiny-moddable-feature' },
            { label: 'Example: Upgrade Card', slug: 'pages/guides/example-upgrade-card' },
            { label: 'Example: Item Equipment', slug: 'pages/guides/example-item-equipment' },
            { label: 'Example: Spawn Layer', slug: 'pages/guides/example-spawn-layer' },
            { label: 'Example: Mini Dialogue', slug: 'pages/guides/example-mini-dialogue' },
            { label: 'Example: Scene Beat', slug: 'pages/guides/example-scene-beat' },
            {
              label: 'Example: Mod Check Diagnostic',
              slug: 'pages/guides/example-mod-check-diagnostic',
            },
            { label: 'Tiny Rust-Backed Stat', slug: 'pages/guides/tiny-rust-backed-stat' },
          ],
        },
        {
          label: 'Architecture',
          items: [
            { label: 'Chapter Home', slug: 'pages/architecture' },
            { label: '1. Fundamentals', slug: 'pages/architecture/fundamentals' },
            { label: '2. Module Boundaries', slug: 'pages/architecture/module-boundaries' },
            { label: '3. Runtime Loop', slug: 'pages/architecture/runtime-loop' },
            {
              label: '4. Data And Modding Flow',
              slug: 'pages/architecture/data-and-modding-flow',
            },
            {
              label: '5. Assets And Release Packs',
              slug: 'pages/architecture/assets-and-release-packs',
            },
            { label: '6. Choreography', slug: 'pages/architecture/choreography' },
            { label: '7. Extension Patterns', slug: 'pages/architecture/extension-patterns' },
            { label: '8. Commands And Events', slug: 'pages/architecture/commands-and-events' },
            { label: '9. Simulation And ECS', slug: 'pages/architecture/simulation-and-ecs' },
            { label: '10. Rendering And UI', slug: 'pages/architecture/rendering-and-ui' },
            { label: '11. Persistence And State', slug: 'pages/architecture/persistence-and-state' },
            {
              label: '12. Verification Architecture',
              slug: 'pages/architecture/verification-architecture',
            },
            {
              label: '13. Graceful Degradation',
              slug: 'pages/architecture/graceful-degradation',
            },
            {
              label: '14. Performance And Observability',
              slug: 'pages/architecture/performance-and-observability',
            },
            {
              label: '15. Feature Slice Walkthrough',
              slug: 'pages/architecture/feature-slice-walkthrough',
            },
            { label: '16. Design Principles', slug: 'pages/architecture/design-principles' },
            { label: '17. Architecture Glossary', slug: 'pages/architecture/glossary' },
            { label: '18. Migration Status', slug: 'pages/architecture/migration-status' },
            { label: '19. Anti-Patterns', slug: 'pages/architecture/anti-patterns' },
          ],
        },
        {
          label: 'Main Code',
          items: [
            { label: 'Main Code Map', slug: 'pages/main-code-map' },
            { label: 'Entry Points', slug: 'pages/entry-points' },
            { label: 'App Shell And States', slug: 'pages/app-shell-and-states' },
            { label: 'Assets Reference', slug: 'pages/assets-reference' },
            { label: 'Assets And Packaging', slug: 'pages/assets-and-packaging' },
            { label: 'Asset Pack Reference', slug: 'pages/asset-pack-reference' },
            { label: 'Modding Boundary', slug: 'pages/modding-boundary' },
            { label: 'Logging And Perf Reference', slug: 'pages/logging-and-perf-reference' },
            { label: 'Observability', slug: 'pages/observability' },
            { label: 'CLI Tools', slug: 'pages/cli-tools' },
            { label: 'Vercel Deployment', slug: 'pages/vercel-deployment' },
          ],
        },
      ],
    }),
  ],
});
