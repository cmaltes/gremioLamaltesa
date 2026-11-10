import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import remarkBloques from './src/plugins/remark-bloques.mjs';

export default defineConfig({
  site: 'https://gremio.lamaltesa.dev',
  integrations: [sitemap()],
  markdown: { remarkPlugins: [remarkBloques] },
  build: { format: 'directory' },
});
