import { describe, expect, it } from 'vitest';
import { normalizeBasePath } from './config';

describe('public base path', () => {
  it('supports deployment to an independent domain root or a subpath', () => {
    expect(normalizeBasePath('/')).toBe('/');
    expect(normalizeBasePath('/aiapimaker')).toBe('/aiapimaker/');
    expect(normalizeBasePath('future-name/')).toBe('/future-name/');
  });
});
