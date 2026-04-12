/**
 * Locale metadata for the site.
 * `nativeName` uses the self-naming convention recommended by W3C.
 */
export const languages = {
  en: { nativeName: 'English', shortCode: 'EN', htmlLang: 'en', ogLocale: 'en_US' },
  fr: { nativeName: 'Français', shortCode: 'FR', htmlLang: 'fr', ogLocale: 'fr_FR' },
  es: { nativeName: 'Español', shortCode: 'ES', htmlLang: 'es', ogLocale: 'es_ES' },
} as const;

export type Locale = keyof typeof languages;

export const locales = Object.keys(languages) as Locale[];
export const defaultLocale: Locale = 'en';

export function isLocale(value: string): value is Locale {
  return value in languages;
}
