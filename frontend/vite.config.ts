import { loadEnv } from 'vite';
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

function normalizeBasePath(path: string) {
  const trimmed = path.trim();
  const prefixed = trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
  return prefixed.endsWith('/') ? prefixed : `${prefixed}/`;
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_');
  const base = normalizeBasePath(env.VITE_BASE_PATH || '/aiapimaker/');
  return {
    plugins: [react()],
    base,
    server: {
      host: '127.0.0.1',
      port: 19362,
      strictPort: true,
    },
    preview: {
      host: '127.0.0.1',
      port: 19362,
      strictPort: true,
    },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: ['./src/test-setup.ts'],
      exclude: ['node_modules/**', 'dist/**'],
    },
  };
});
