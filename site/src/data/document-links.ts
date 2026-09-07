import { defaultLocale, locales, type Locale } from '../i18n/languages';
import { localePath } from '../i18n/utils';
import { draftDownloadUrl } from './draft-downloads';
import { docs } from './docs';
import { handbook } from './handbook';

const sharedAssetPrefix = /^\/(images|v|_astro|ctx|registry-draft|favicon|sitemap|robots\.txt)(\/|$|\.)/;
const documentPages = new Map<string, string>();
for (const [directory, entries, route] of [
  ['docs', docs, '/docs'],
  ['docs/handbook', handbook, '/handbook'],
] as const) {
  for (const [slug, entry] of Object.entries(entries)) {
    for (const language of locales) {
      const translated = language === defaultLocale ? '' : `${language}/`;
      documentPages.set(`${directory}/${translated}${entry.file}`, `${route}/${slug}/`);
    }
  }
}

/** Resolve authored repository links before adding a locale to site pages. */
export function documentationLink(href: string, sourcePath: string, locale: Locale): string {
  if (/^(?:[a-z][a-z0-9+.-]*:|\/\/|#)/i.test(href)) return href;
  const target = new URL(href, `https://publicschema.org/${sourcePath}`);
  const repositoryPath = target.pathname.slice(1);
  const download = draftDownloadUrl(repositoryPath);
  if (download) return `${download}${target.search}${target.hash}`;
  if (repositoryPath === 'CONTRIBUTING.md') {
    return `https://github.com/PublicSchema/publicschema.org/blob/main/CONTRIBUTING.md${target.hash}`;
  }
  const documentPage = documentPages.get(repositoryPath);
  if (documentPage) return `${localePath(documentPage, locale)}${target.search}${target.hash}`;
  // Unrecognized relative paths are not promoted to public file downloads.
  if (!href.startsWith('/') || sharedAssetPrefix.test(target.pathname)) return href;
  if (locale === defaultLocale || target.pathname.startsWith(`/${locale}/`)) return href;
  return `${localePath(target.pathname, locale)}${target.search}${target.hash}`;
}

export function rewriteDocumentationLinks(html: string, sourcePath: string, locale: Locale): string {
  return html.replace(/href="([^"]*)"/g, (_, href) =>
    `href="${documentationLink(href, sourcePath, locale)}"`);
}
