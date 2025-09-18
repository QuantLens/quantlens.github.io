import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  integrations: [tailwind({ applyBaseStyles: true }), mdx()],
  output: 'static',
  server: { port: 4321 },
  site: 'https://quantlens.github.io',
  base: '/',
  markdown: {
    syntaxHighlight: 'shiki',
    shikiConfig: {
      theme: 'dracula'
    },
    remarkPlugins: [],
    rehypePlugins: [],
  }
});
