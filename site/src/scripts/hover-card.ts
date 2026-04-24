/**
 * Hover-card script: attaches floating preview panels to every
 * [data-preview-key] link. One panel is rendered per page; its
 * contents are populated from /preview/{locale}.json on first hover.
 */

import {
  computePosition,
  flip,
  shift,
  offset,
  autoUpdate,
  type Placement,
} from "@floating-ui/dom";

interface PreviewEntry {
  label: string;
  kind: "concept" | "property" | "vocabulary";
  maturity: string;
  href: string;
  definition_excerpt: string;
  locale_used: string;
  domain?: string | null;
  abstract?: boolean;
  type?: string;
  vocabulary?: string | null;
}

interface HoverCardStrings {
  locale: string;
  requestedLocale: string;
  openLink: string;
  fallbackTag: string;
  propertyType: string;
  propertyVocabulary: string;
  badgeDraft: string;
  badgeCandidate: string;
  badgeStable: string;
  badgeAbstract: string;
}

const OPEN_DELAY_MS = 500;
const CLOSE_DELAY_MS = 200;
const POINTER_SETTLE_MS = 100;

let previewData: Record<string, PreviewEntry> | null = null;
let previewLoadPromise: Promise<Record<string, PreviewEntry>> | null = null;

let openTimer: number | null = null;
let closeTimer: number | null = null;
let activeAnchor: HTMLElement | null = null;
let pendingAnchor: HTMLElement | null = null;
let cleanupAutoUpdate: (() => void) | null = null;
let lastPointerMoveAt = 0;

function getStrings(container: HTMLElement): HoverCardStrings {
  const g = (name: string, fallback: string) =>
    container.dataset[name] ?? fallback;
  return {
    locale: g("locale", "en"),
    requestedLocale: g("locale", "en"),
    openLink: g("openLink", "Open →"),
    fallbackTag: g("fallbackTag", "shown in {locale}"),
    propertyType: g("propertyType", "Type"),
    propertyVocabulary: g("propertyVocabulary", "Vocabulary"),
    badgeDraft: g("badgeDraft", "draft"),
    badgeCandidate: g("badgeCandidate", "candidate"),
    badgeStable: g("badgeStable", "stable"),
    badgeAbstract: g("badgeAbstract", "abstract"),
  };
}

function localePath(path: string, locale: string): string {
  if (!path.startsWith("/")) return path;
  // Ensure trailing slash on page paths (mirrors site/src/i18n/utils.ts).
  const [pathPart, ...fragParts] = path.split("#");
  const fragment = fragParts.length > 0 ? `#${fragParts.join("#")}` : "";
  const lastSegment = pathPart.split("/").pop() ?? "";
  const needsSlash = !pathPart.endsWith("/") && !lastSegment.includes(".");
  const withSlash = needsSlash ? `${pathPart}/` : pathPart;
  const result = `${withSlash}${fragment}`;
  return locale === "en" ? result : `/${locale}${result}`;
}

function ensurePreviewLoaded(locale: string): Promise<Record<string, PreviewEntry>> {
  if (previewData) return Promise.resolve(previewData);
  if (previewLoadPromise) return previewLoadPromise;
  previewLoadPromise = fetch(`/preview/${locale}.json`)
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`preview ${r.status}`))))
    .then((data: Record<string, PreviewEntry>) => {
      previewData = data;
      return data;
    })
    .catch((err) => {
      console.warn("[hover-card] failed to load preview data", err);
      previewData = {};
      return previewData;
    });
  return previewLoadPromise;
}

function maturityLabel(
  maturity: string,
  strings: HoverCardStrings,
): string {
  if (maturity === "draft") return strings.badgeDraft;
  if (maturity === "candidate") return strings.badgeCandidate;
  return strings.badgeStable;
}

function buildCardHtml(
  entry: PreviewEntry,
  strings: HoverCardStrings,
): string {
  const parts: string[] = [];

  const showMaturity =
    entry.maturity !== "stable" && entry.maturity !== "normative";

  const badges: string[] = [];
  if (entry.domain) {
    badges.push(
      `<span class="hc-badge hc-badge-domain">${escapeHtml(entry.domain)}</span>`,
    );
  }
  if (entry.abstract) {
    badges.push(
      `<span class="hc-badge hc-badge-abstract">${escapeHtml(strings.badgeAbstract)}</span>`,
    );
  }
  if (showMaturity) {
    badges.push(
      `<span class="hc-badge hc-badge-maturity hc-badge-maturity-${entry.maturity}">${escapeHtml(maturityLabel(entry.maturity, strings))}</span>`,
    );
  }
  if (entry.locale_used !== strings.requestedLocale) {
    const localeTag = entry.locale_used.toUpperCase();
    const tagText = strings.fallbackTag.replace("{locale}", localeTag);
    badges.push(
      `<span class="hc-badge hc-badge-fallback" title="${escapeHtml(tagText)}">${escapeHtml(localeTag)}</span>`,
    );
  }

  parts.push(`<div class="hc-label">${escapeHtml(entry.label)}</div>`);
  if (badges.length > 0) {
    parts.push(`<div class="hc-badges">${badges.join("")}</div>`);
  }
  if (entry.definition_excerpt) {
    parts.push(`<div class="hc-def">${escapeHtml(entry.definition_excerpt)}</div>`);
  }

  if (entry.kind === "property") {
    const meta: string[] = [];
    if (entry.type) {
      meta.push(
        `<div><span class="hc-meta-key">${escapeHtml(strings.propertyType)}</span> <code>${escapeHtml(entry.type)}</code></div>`,
      );
    }
    if (entry.vocabulary) {
      meta.push(
        `<div><span class="hc-meta-key">${escapeHtml(strings.propertyVocabulary)}</span> <code>${escapeHtml(entry.vocabulary)}</code></div>`,
      );
    }
    if (meta.length > 0) {
      parts.push(`<div class="hc-meta">${meta.join("")}</div>`);
    }
  }

  const cardHref = localePath(entry.href, strings.locale);
  parts.push(`<a class="hc-cta" href="${escapeHtml(cardHref)}">${escapeHtml(strings.openLink)}</a>`);

  return parts.join("");
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function scheduleOpen(
  anchor: HTMLElement,
  container: HTMLElement,
  panel: HTMLElement,
  strings: HoverCardStrings,
) {
  if (activeAnchor === anchor) {
    cancelCloseTimer();
    return;
  }
  if (pendingAnchor === anchor && openTimer !== null) return;
  pendingAnchor = anchor;
  cancelOpenTimer();
  cancelCloseTimer();
  openTimer = window.setTimeout(async () => {
    const sincePointerMove = Date.now() - lastPointerMoveAt;
    if (sincePointerMove < POINTER_SETTLE_MS) {
      openTimer = window.setTimeout(
        () => openNow(anchor, container, panel, strings),
        POINTER_SETTLE_MS,
      );
      return;
    }
    openNow(anchor, container, panel, strings);
  }, OPEN_DELAY_MS);
}

async function openNow(
  anchor: HTMLElement,
  container: HTMLElement,
  panel: HTMLElement,
  strings: HoverCardStrings,
) {
  const key = anchor.dataset.previewKey;
  if (!key) return;

  const data = await ensurePreviewLoaded(strings.locale);
  const entry = data[key];
  if (!entry) return;
  if (activeAnchor && activeAnchor !== anchor) closeCard(container);
  activeAnchor = anchor;

  panel.innerHTML = buildCardHtml(entry, strings);
  container.classList.add("hc-open");
  container.removeAttribute("hidden");

  const anchorId = anchor.id || ensureAnchorId(anchor);
  const panelId = panel.id || "hover-card-panel";
  panel.id = panelId;
  anchor.setAttribute("aria-describedby", panelId);
  void anchorId;

  cleanupAutoUpdate = autoUpdate(anchor, panel, () => {
    computePosition(anchor, panel, {
      placement: "bottom" as Placement,
      strategy: "fixed",
      middleware: [offset(8), flip(), shift({ padding: 8 })],
    }).then(({ x, y }) => {
      Object.assign(panel.style, { left: `${x}px`, top: `${y}px` });
    });
  });
}

function ensureAnchorId(anchor: HTMLElement): string {
  if (anchor.id) return anchor.id;
  anchor.id = `hc-anchor-${Math.random().toString(36).slice(2, 10)}`;
  return anchor.id;
}

function scheduleClose(container: HTMLElement) {
  cancelCloseTimer();
  closeTimer = window.setTimeout(
    () => closeCard(container),
    CLOSE_DELAY_MS,
  );
}

function closeCard(container: HTMLElement) {
  cancelOpenTimer();
  cancelCloseTimer();
  pendingAnchor = null;
  if (activeAnchor) {
    activeAnchor.removeAttribute("aria-describedby");
    activeAnchor = null;
  }
  container.classList.remove("hc-open");
  container.setAttribute("hidden", "");
  if (cleanupAutoUpdate) {
    cleanupAutoUpdate();
    cleanupAutoUpdate = null;
  }
}

function cancelOpenTimer() {
  if (openTimer !== null) {
    window.clearTimeout(openTimer);
    openTimer = null;
  }
}

function cancelCloseTimer() {
  if (closeTimer !== null) {
    window.clearTimeout(closeTimer);
    closeTimer = null;
  }
}

function initHoverCard() {
  const container = document.querySelector<HTMLElement>(".hover-card-container");
  if (!container) return;

  const hoverCapable = window.matchMedia("(hover: hover)").matches;
  if (!hoverCapable) return;

  const panel = container.querySelector<HTMLElement>(".hover-card-panel");
  if (!panel) return;

  const strings = getStrings(container);

  document.addEventListener(
    "pointermove",
    () => {
      lastPointerMoveAt = Date.now();
    },
    { passive: true },
  );

  function findAnchor(target: EventTarget | null): HTMLElement | null {
    if (!(target instanceof Element)) return null;
    return target.closest<HTMLElement>("[data-preview-key]");
  }

  document.addEventListener(
    "pointerenter",
    (e) => {
      const anchor = findAnchor(e.target);
      if (!anchor) return;
      scheduleOpen(anchor, container, panel, strings);
    },
    true,
  );

  document.addEventListener(
    "pointerleave",
    (e) => {
      const anchor = findAnchor(e.target);
      if (!anchor) return;
      scheduleClose(container);
    },
    true,
  );

  document.addEventListener("focusin", (e) => {
    const anchor = findAnchor(e.target);
    if (!anchor) return;
    scheduleOpen(anchor, container, panel, strings);
  });

  document.addEventListener("focusout", (e) => {
    const anchor = findAnchor(e.target);
    if (!anchor) return;
    const next = (e as FocusEvent).relatedTarget as Node | null;
    if (next && container.contains(next)) return;
    scheduleClose(container);
  });

  panel.addEventListener("pointerenter", cancelCloseTimer);
  panel.addEventListener("pointerleave", () => scheduleClose(container));

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && activeAnchor) {
      closeCard(container);
    }
  });

  window.addEventListener(
    "scroll",
    () => {
      if (activeAnchor) closeCard(container);
    },
    { passive: true },
  );
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initHoverCard);
} else {
  initHoverCard();
}
