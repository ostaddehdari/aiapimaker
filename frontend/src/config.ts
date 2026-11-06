/** Paths are relative to the deploy host; no domain is hardcoded. */
export function normalizeBasePath(raw: string): string {
  const value = raw.trim();
  if (!value || value === '/') return '/';
  return '/' + value.replace(/^\/+|\/+$/g, '') + '/';
}

export const appBasePath = normalizeBasePath(import.meta.env.BASE_URL || '/aiapimaker/');
export const apiBasePath = normalizeBasePath(
  import.meta.env.VITE_API_BASE_PATH || appBasePath + 'api/v1/',
);
