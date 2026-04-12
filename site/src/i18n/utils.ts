import { ui } from './ui';
import { defaultLocale, isLocale, locales, type Locale } from './languages';

export { locales, defaultLocale };
export type { Locale };

/**
 * Return a `t(key)` function bound to the given locale. Falls back to the
 * default locale if a key is missing in the requested locale, and returns the
 * key itself if it is missing everywhere so the gap is visible in the output.
 */
export function useTranslations(locale: Locale) {
  return function t(key: string, vars?: Record<string, string | number>): string {
    const fromLocale = lookup(ui[locale], key);
    const resolved = fromLocale ?? lookup(ui[defaultLocale], key) ?? key;
    if (!vars) return resolved;
    return resolved.replace(/\{(\w+)\}/g, (_, name) =>
      name in vars ? String(vars[name]) : `{${name}}`
    );
  };
}

function lookup(dict: Record<string, string> | undefined, key: string): string | undefined {
  if (!dict) return undefined;
  return dict[key];
}

/**
 * Extract the locale prefix from a URL pathname. Returns the default locale
 * when no known prefix is present.
 */
export function getLangFromUrl(url: URL | string): Locale {
  const pathname = typeof url === 'string' ? url : url.pathname;
  const first = pathname.split('/').filter(Boolean)[0];
  if (first && isLocale(first)) return first;
  return defaultLocale;
}

/**
 * Prepend a locale prefix to an internal path. The default locale is
 * un-prefixed to match `i18n.routing.prefixDefaultLocale: false`.
 */
export function localePath(path: string, locale: Locale = defaultLocale): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;

  // Ensure trailing slash on page paths (skip fragments and file extensions).
  const [pathPart, ...fragmentParts] = normalized.split('#');
  const fragment = fragmentParts.length > 0 ? `#${fragmentParts.join('#')}` : '';
  const lastSegment = pathPart.split('/').pop() ?? '';
  const needsSlash = !pathPart.endsWith('/') && !lastSegment.includes('.');
  const withSlash = needsSlash ? `${pathPart}/` : pathPart;
  const result = `${withSlash}${fragment}`;

  if (locale === defaultLocale) return result;
  return `/${locale}${result}`;
}

/**
 * Given the current URL and a target locale, return the equivalent path in
 * that locale. Strips the current locale prefix (if any) before prepending
 * the target.
 */
export function switchLocalePath(currentUrl: URL | string, targetLocale: Locale): string {
  const pathname = typeof currentUrl === 'string' ? currentUrl : currentUrl.pathname;
  const parts = pathname.split('/').filter(Boolean);
  if (parts.length > 0 && isLocale(parts[0])) parts.shift();
  const unprefixed = '/' + parts.join('/') + (pathname.endsWith('/') && parts.length > 0 ? '/' : '');
  const cleaned = unprefixed === '//' ? '/' : unprefixed;
  return localePath(cleaned, targetLocale);
}
