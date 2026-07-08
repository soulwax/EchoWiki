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
      logo: {
        src: './public/favicon-symbol.png',
        alt: 'EchoWarrior',
      },
      customCss: ['./src/styles/custom.css'],
      components: {
        Head: './src/components/Head.astro',
      },
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
          tag: 'link',
          attrs: { rel: 'icon', href: '/favicon.ico', sizes: 'any' },
        },
        {
          tag: 'meta',
          attrs: { property: 'og:image', content: new URL('/Shisaku-2.png', site).toString() },
        },
        {
          tag: 'meta',
          attrs: { name: 'twitter:image', content: new URL('/Shisaku-2.png', site).toString() },
        },
      ],
      sidebar: [
        {
          label: 'Getting Started',
          items: [
            { label: 'Home', link: '/' },
            { label: 'Wiki Map', slug: 'pages/wiki-map' },
            { label: 'Start Here', slug: 'pages/new-contributor-start' },
            { label: 'Visual Orientation', slug: 'pages/visual-orientation' },
            { label: 'Change Routes', slug: 'pages/change-routes' },
          ],
        },
        {
          label: 'Tutorials',
          items: [
            {
              label: 'First Feature Path',
              collapsed: false,
              items: [
                { label: 'Tiny Moddable Feature', slug: 'pages/guides/tiny-moddable-feature' },
                { label: 'Tiny Rust-Backed Stat', slug: 'pages/guides/tiny-rust-backed-stat' },
                {
                  label: 'First Renderer Boundary Slice',
                  slug: 'pages/guides/first-renderer-boundary-slice',
                },
              ],
            },
            {
              label: 'Worked Examples',
              collapsed: false,
              items: [
                { label: 'Upgrade Card', slug: 'pages/guides/example-upgrade-card' },
                { label: 'Item Equipment', slug: 'pages/guides/example-item-equipment' },
                { label: 'Spawn Layer', slug: 'pages/guides/example-spawn-layer' },
                { label: 'Mini Dialogue', slug: 'pages/guides/example-mini-dialogue' },
                { label: 'Scene Beat', slug: 'pages/guides/example-scene-beat' },
                { label: 'Mod Check Diagnostic', slug: 'pages/guides/example-mod-check-diagnostic' },
              ],
            },
          ],
        },
        {
          label: 'Manual',
          items: [
            {
              label: 'Architecture Overview',
              collapsed: false,
              items: [
                { label: 'Chapter Home', slug: 'pages/architecture' },
                { label: '1. Fundamentals', slug: 'pages/architecture/fundamentals' },
                { label: '2. Module Boundaries', slug: 'pages/architecture/module-boundaries' },
                { label: '3. Runtime Loop', slug: 'pages/architecture/runtime-loop' },
                { label: '3A. Inside The Runtime', slug: 'pages/architecture/inside-the-runtime' },
                {
                  label: '3B. Runtime Data Command Pipeline',
                  slug: 'pages/architecture/runtime-data-command-pipeline',
                },
                {
                  label: '4. Data And Modding Flow',
                  slug: 'pages/architecture/data-and-modding-flow',
                },
                {
                  label: '5. Assets And Release Packs',
                  slug: 'pages/architecture/assets-and-release-packs',
                },
                {
                  label: '5A. Protection And Tamper Boundaries',
                  slug: 'pages/architecture/protection-and-tamper-boundaries',
                },
                {
                  label: '5B. Pack Integrity Deep Dive',
                  slug: 'pages/architecture/pack-integrity-deep-dive',
                },
              ],
            },
            {
              label: 'Runtime Systems',
              collapsed: false,
              items: [
                { label: 'Runtime Shell', slug: 'pages/runtime-shell' },
                { label: 'Asset Loading Pipeline', slug: 'pages/asset-loading-pipeline' },
                { label: 'Audio And Transitions', slug: 'pages/audio-and-transitions' },
                { label: '6. Choreography', slug: 'pages/architecture/choreography' },
                { label: '10. Rendering And UI', slug: 'pages/architecture/rendering-and-ui' },
                { label: '10A. Vulkan Renderer Path', slug: 'pages/architecture/vulkan-renderer-path' },
              ],
            },
            {
              label: 'Gameplay Systems',
              collapsed: false,
              items: [
                { label: '7. Extension Patterns', slug: 'pages/architecture/extension-patterns' },
                { label: '8. Commands And Events', slug: 'pages/architecture/commands-and-events' },
                { label: '9. Simulation And ECS', slug: 'pages/architecture/simulation-and-ecs' },
                { label: '9A. ECS Lifecycle Hot Lane', slug: 'pages/architecture/ecs-lifecycle-hot-lane' },
                { label: '11. Persistence And State', slug: 'pages/architecture/persistence-and-state' },
              ],
            },
            {
              label: 'Quality And Evolution',
              collapsed: true,
              items: [
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
                { label: '18. Migration Status', slug: 'pages/architecture/migration-status' },
                { label: '19. Anti-Patterns', slug: 'pages/architecture/anti-patterns' },
              ],
            },
          ],
        },
        {
          label: 'Leitmotif',
          items: [
            { label: 'Overview', slug: 'pages/leitmotif' },
            { label: 'Screenshots', slug: 'pages/leitmotif/screenshots' },
            { label: 'Getting Started', slug: 'pages/leitmotif/getting-started' },
            { label: 'Usage', slug: 'pages/leitmotif/usage' },
            { label: 'Moddability', slug: 'pages/leitmotif/moddability' },
            { label: 'Architecture', slug: 'pages/leitmotif/architecture' },
            { label: 'Contributor Slices', slug: 'pages/leitmotif/contributor-slices' },
          ],
        },
        {
          label: 'Soundgarden',
          items: [
            { label: 'Overview', slug: 'pages/soundgarden' },
            { label: 'Available Now', slug: 'pages/soundgarden/available-now' },
            {
              label: 'Authoring Workflows',
              collapsed: false,
              items: [
                { label: 'Manifest Studio', slug: 'pages/soundgarden/manifest-studio' },
                { label: 'Mod Authoring Mode', slug: 'pages/soundgarden/mod-authoring-mode' },
                { label: 'Audition And Clips', slug: 'pages/soundgarden/audition-and-clips' },
              ],
            },
            {
              label: 'Contracts And Data',
              collapsed: false,
              items: [
                { label: 'Audio Manifests', slug: 'pages/soundgarden/audio-manifests' },
                { label: 'CLI Contract', slug: 'pages/soundgarden/cli-contract' },
                { label: 'Architecture', slug: 'pages/soundgarden/architecture' },
                { label: 'Moddability', slug: 'pages/soundgarden/moddability' },
              ],
            },
            { label: 'Contributor Workflow', slug: 'pages/soundgarden/contributor-workflow' },
          ],
        },
        {
          label: 'Reference',
          items: [
            {
              label: 'Main Code',
              collapsed: false,
              items: [
                { label: 'Main Code Map', slug: 'pages/main-code-map' },
                { label: 'Entry Points', slug: 'pages/entry-points' },
                { label: 'App Shell And States', slug: 'pages/app-shell-and-states' },
                { label: 'Assets Reference', slug: 'pages/assets-reference' },
              ],
            },
            {
              label: 'Content And Packs',
              collapsed: false,
              items: [
                { label: 'Assets And Packaging', slug: 'pages/assets-and-packaging' },
                { label: 'Asset Pack Reference', slug: 'pages/asset-pack-reference' },
                { label: 'Modding Boundary', slug: 'pages/modding-boundary' },
                {
                  label: 'Protection And Tamper Boundaries',
                  slug: 'pages/architecture/protection-and-tamper-boundaries',
                },
              ],
            },
            {
              label: 'Diagnostics And Tools',
              collapsed: false,
              items: [
                { label: 'Logging And Perf Reference', slug: 'pages/logging-and-perf-reference' },
                { label: 'Observability', slug: 'pages/observability' },
                { label: 'CLI Tools', slug: 'pages/cli-tools' },
                { label: 'Architecture Glossary', slug: 'pages/architecture/glossary' },
              ],
            },
          ],
        },
        {
          label: 'Contributing And Operations',
          items: [
            { label: 'Contribution Workflow', slug: 'pages/contribution-workflow' },
            { label: 'Verification Guide', slug: 'pages/verification-guide' },
            { label: 'Wiki Automation', slug: 'pages/wiki-automation' },
            { label: 'Vercel Deployment', slug: 'pages/vercel-deployment' },
          ],
        },
      ],
    }),
  ],
});
