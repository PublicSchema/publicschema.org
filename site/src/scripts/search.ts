import MiniSearch from "minisearch";

interface SearchDocument {
  id: string;
  type: string;
  title: string;
  body: string;
  path: string;
  meta: string;
  keywords: string;
}

interface SearchStrings {
  locale: string;
  placeholder: string;
  minChars: string;
  noResults: string;
  browseHint: string;
  resultsStatus: string;
  noResultsStatus: string;
  navConcepts: string;
  navProperties: string;
  navVocabularies: string;
  navDocs: string;
  ariaLabel: string;
  close: string;
}

function readStrings(container: Element): SearchStrings {
  const g = (name: string, fallback: string) =>
    (container as HTMLElement).dataset[name] ?? fallback;
  return {
    locale: g("locale", "en"),
    placeholder: g("searchPlaceholder", "Search concepts, properties..."),
    minChars: g("searchMinChars", "Type at least 2 characters to search"),
    noResults: g("searchNoResults", "No results for"),
    browseHint: g("searchBrowseHint", "Browse"),
    resultsStatus: g("searchResultsStatus", "{count} result(s) found"),
    noResultsStatus: g("searchNoResultsStatus", "No results found"),
    navConcepts: g("navConcepts", "Concepts"),
    navProperties: g("navProperties", "Properties"),
    navVocabularies: g("navVocabularies", "Vocabularies"),
    navDocs: g("navDocs", "Docs"),
    ariaLabel: g("searchAriaLabel", "Search"),
    close: g("searchClose", "Close search"),
  };
}

function localePrefix(locale: string): string {
  return locale === "en" ? "" : `/${locale}`;
}

// Strip diacritics so "menage" matches "Ménage", "elegibilite" matches "Éligibilité", etc.
function foldDiacritics(term: string): string {
  return term.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function indexUrlFor(locale: string): string {
  return `${localePrefix(locale)}/search-index.json`;
}

// Shared index promise: ensures only one fetch + build happens
let indexPromise: Promise<MiniSearch<SearchDocument>> | null = null;

function ensureIndex(locale: string): Promise<MiniSearch<SearchDocument>> {
  if (indexPromise) return indexPromise;
  indexPromise = fetch(indexUrlFor(locale))
    .then((res) => {
      if (!res.ok) throw new Error(`Search index fetch failed: ${res.status}`);
      return res.json();
    })
    .then((docs: SearchDocument[]) => {
      const ms = new MiniSearch<SearchDocument>({
        fields: ["title", "body", "keywords"],
        storeFields: ["type", "title", "body", "path", "meta", "keywords"],
        processTerm: (term) => foldDiacritics(term.toLowerCase()),
        searchOptions: {
          boost: { title: 3, body: 1, keywords: 0.5 },
          prefix: true,
          fuzzy: 0.2,
          processTerm: (term) => foldDiacritics(term.toLowerCase()),
        },
      });
      ms.addAll(docs);
      return ms;
    })
    .catch((err) => {
      indexPromise = null;
      throw err;
    });
  return indexPromise;
}

const TYPE_ORDER: Record<string, number> = {
  concept: 0,
  property: 1,
  vocabulary: 2,
  doc: 3,
};

function typeLabels(s: SearchStrings): Record<string, string> {
  return {
    concept: s.navConcepts,
    property: s.navProperties,
    vocabulary: s.navVocabularies,
    doc: s.navDocs,
  };
}

const DEBOUNCE_MS = 120;
const MIN_QUERY_LENGTH = 2;
const MAX_RESULTS = 8;
const MAX_PER_GROUP = 3;

// Highlight matched substring in a title, accent-insensitive.
// Walks the folded (no-diacritics) version to find match positions,
// then maps those positions back to the original string.
function highlightMatch(title: string, query: string): string {
  const safe = escapeHtml(title);
  const folded = foldDiacritics(safe.toLowerCase());
  const foldedQuery = foldDiacritics(query.toLowerCase());
  const start = folded.indexOf(foldedQuery);
  if (start === -1) return safe;
  const end = start + foldedQuery.length;
  return safe.slice(0, start) + "<mark>" + safe.slice(start, end) + "</mark>" + safe.slice(end);
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen).trimEnd() + "...";
}

// Find which vocabulary value label matched the query.
// Keywords are tab-separated in the search index to preserve multi-word labels.
// Comparison is accent-insensitive.
function findMatchedValue(keywords: string, query: string): string | null {
  if (!keywords) return null;
  const q = foldDiacritics(query.toLowerCase());
  const labels = keywords.split("\t");
  for (const label of labels) {
    if (foldDiacritics(label.toLowerCase()).includes(q)) return label.trim();
  }
  return null;
}

interface GroupedResults {
  type: string;
  label: string;
  items: Array<{
    result: SearchDocument;
    matchedValue: string | null;
  }>;
}

function groupResults(
  results: Array<MiniSearch.SearchResult & SearchDocument>,
  query: string,
  labels: Record<string, string>
): GroupedResults[] {
  const groups: Record<string, GroupedResults> = {};

  // First pass: collect up to MAX_PER_GROUP per type (ensures type diversity)
  for (const result of results) {
    const type = result.type;
    if (!groups[type]) {
      groups[type] = {
        type,
        label: labels[type] || type,
        items: [],
      };
    }
    if (groups[type].items.length >= MAX_PER_GROUP) continue;

    let matchedValue: string | null = null;
    // MiniSearch's match maps query terms to arrays of field names where they matched.
    // Check if any matched term was found in the "keywords" field.
    if (type === "vocabulary" && result.match) {
      const matchedViaKeywords = Object.values(result.match).some(
        (fields) => Array.isArray(fields) && fields.includes("keywords")
      );
      if (matchedViaKeywords) {
        matchedValue = findMatchedValue(result.keywords || "", query);
      }
    }

    groups[type].items.push({ result, matchedValue });

    // Check total across all groups
    const total = Object.values(groups).reduce((sum, g) => sum + g.items.length, 0);
    if (total >= MAX_RESULTS) break;
  }

  return Object.values(groups).sort(
    (a, b) => (TYPE_ORDER[a.type] ?? 99) - (TYPE_ORDER[b.type] ?? 99)
  );
}

function renderResults(
  container: HTMLElement,
  groups: GroupedResults[],
  query: string,
  locale: string,
  idPrefix: string = "desktop"
): void {
  let optionIndex = 0;
  let html = "";
  const prefix = localePrefix(locale);

  for (const group of groups) {
    html += `<div class="search-group-header" role="presentation">${escapeHtml(group.label)}</div>`;
    for (const { result, matchedValue } of group.items) {
      const highlighted = highlightMatch(result.title, query);
      let context = escapeHtml(truncate(result.body || "", 80));
      if (matchedValue) {
        context = `Matched: "${escapeHtml(matchedValue)}"`;
      } else if (result.meta) {
        context = escapeHtml(truncate(result.meta, 80));
      }
      const rawPath = result.path.endsWith("/") ? result.path : `${result.path}/`;
      const href = `${prefix}${rawPath}`;
      html += `<a class="search-result" href="${escapeHtml(href)}" role="option" id="search-opt-${idPrefix}-${optionIndex}" aria-selected="false">
        <span class="badge badge-${escapeHtml(result.type)}">${escapeHtml(result.type)}</span>
        <span class="search-result-content">
          <span class="search-result-title">${highlighted}</span>
          <span class="search-result-context">${context}</span>
        </span>
      </a>`;
      optionIndex++;
    }
  }

  container.innerHTML = html;
}

function renderNoResults(container: HTMLElement, query: string, s: SearchStrings): void {
  const prefix = localePrefix(s.locale);
  container.innerHTML = `<div class="search-no-results">
    ${escapeHtml(s.noResults)} "${escapeHtml(truncate(query, 60))}"
    <div style="margin-top: var(--space-sm)">
      ${escapeHtml(s.browseHint)}: <a href="${prefix}/concepts/">${escapeHtml(s.navConcepts)}</a> &middot; <a href="${prefix}/properties/">${escapeHtml(s.navProperties)}</a> &middot; <a href="${prefix}/vocab/">${escapeHtml(s.navVocabularies)}</a>
    </div>
  </div>`;
}

function renderMinChars(container: HTMLElement, s: SearchStrings): void {
  container.innerHTML = `<div class="search-min-chars">${escapeHtml(s.minChars)}</div>`;
}

// Substitute {count} placeholder in a status template string.
function formatCount(template: string, count: number): string {
  return template.replace(/\{count\}/g, String(count));
}

// Detect platform for keyboard shortcut display
const isMac =
  typeof navigator !== "undefined" &&
  ((navigator as any).userAgentData?.platform === "macOS" ||
    /Mac|iPhone|iPad/.test(navigator.platform || ""));

function initSearch(): void {
  const searchContainer = document.querySelector(".search-container");
  const searchInput = searchContainer?.querySelector(
    ".search-input"
  ) as HTMLInputElement | null;
  const resultsContainer = searchContainer?.querySelector(
    "#search-results"
  ) as HTMLElement | null;
  const srStatus = searchContainer?.querySelector(
    ".search-sr-status"
  ) as HTMLElement | null;
  const shortcutHint = searchContainer?.querySelector(
    ".search-shortcut"
  ) as HTMLElement | null;
  const mobileToggle = document.querySelector(
    ".search-mobile-toggle"
  ) as HTMLButtonElement | null;

  if (!searchInput || !resultsContainer || !searchContainer) return;

  const strings = readStrings(searchContainer);
  const labels = typeLabels(strings);

  // Set keyboard shortcut hint text
  if (shortcutHint) {
    shortcutHint.textContent = isMac ? "\u2318K" : "Ctrl+K";
  }

  let activeIndex = -1;
  let debounceTimer: ReturnType<typeof setTimeout> | null = null;
  let currentQuery = "";

  function showResults(): void {
    if (!resultsContainer) return;
    resultsContainer.hidden = false;
    searchInput!.setAttribute("aria-expanded", "true");
  }

  function hideResults(): void {
    if (!resultsContainer) return;
    resultsContainer.hidden = true;
    searchInput!.setAttribute("aria-expanded", "false");
    searchInput!.removeAttribute("aria-activedescendant");
    activeIndex = -1;
  }

  function setActiveOption(index: number): void {
    if (!resultsContainer) return;
    const options = resultsContainer.querySelectorAll('[role="option"]');
    // Clear previous
    options.forEach((opt) => opt.setAttribute("aria-selected", "false"));
    activeIndex = index;
    if (index >= 0 && index < options.length) {
      const opt = options[index];
      opt.setAttribute("aria-selected", "true");
      searchInput!.setAttribute("aria-activedescendant", opt.id);
      opt.scrollIntoView({ block: "nearest" });
    } else {
      searchInput!.removeAttribute("aria-activedescendant");
    }
  }

  function getOptionCount(): number {
    return resultsContainer?.querySelectorAll('[role="option"]').length ?? 0;
  }

  async function doSearch(query: string): Promise<void> {
    currentQuery = query;
    if (query.length < MIN_QUERY_LENGTH) {
      if (query.length > 0) {
        showResults();
        renderMinChars(resultsContainer!, strings);
      } else {
        hideResults();
      }
      if (srStatus) srStatus.textContent = "";
      return;
    }

    // Truncate very long queries
    const q = query.length > 100 ? query.slice(0, 100) : query;

    try {
      const ms = await ensureIndex(strings.locale);
      // Check that query hasn't changed during async wait
      if (currentQuery !== query) return;
      const results = ms.search(q) as Array<
        MiniSearch.SearchResult & SearchDocument
      >;

      if (results.length === 0) {
        showResults();
        renderNoResults(resultsContainer!, q, strings);
        if (srStatus) srStatus.textContent = strings.noResultsStatus;
        return;
      }

      const groups = groupResults(results, q, labels);
      showResults();
      renderResults(resultsContainer!, groups, q, strings.locale);
      activeIndex = -1;

      const totalShown = groups.reduce((sum, g) => sum + g.items.length, 0);
      if (srStatus) {
        srStatus.textContent = formatCount(strings.resultsStatus, totalShown);
      }
    } catch {
      hideResults();
    }
  }

  // Debounced input handler
  searchInput.addEventListener("input", () => {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      doSearch(searchInput.value.trim());
    }, DEBOUNCE_MS);
  });

  // Trigger index preload on focus
  searchInput.addEventListener("focus", () => {
    ensureIndex(strings.locale);
    if (searchInput.value.trim().length >= MIN_QUERY_LENGTH) {
      doSearch(searchInput.value.trim());
    }
  });

  // Keyboard navigation
  searchInput.addEventListener("keydown", (e: KeyboardEvent) => {
    const count = getOptionCount();

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        if (resultsContainer!.hidden) return;
        setActiveOption(activeIndex < count - 1 ? activeIndex + 1 : 0);
        break;
      case "ArrowUp":
        e.preventDefault();
        if (resultsContainer!.hidden) return;
        setActiveOption(activeIndex > 0 ? activeIndex - 1 : count - 1);
        break;
      case "Enter":
        e.preventDefault();
        if (activeIndex >= 0) {
          const options = resultsContainer!.querySelectorAll('[role="option"]');
          const selected = options[activeIndex] as HTMLAnchorElement | undefined;
          if (selected?.href) {
            window.location.href = selected.href;
          }
        }
        break;
      case "Escape":
        hideResults();
        searchInput.blur();
        break;
    }
  });

  // Click outside to close
  document.addEventListener("click", (e: MouseEvent) => {
    if (
      searchContainer &&
      !searchContainer.contains(e.target as Node)
    ) {
      hideResults();
    }
  });

  // Global Cmd+K / Ctrl+K shortcut
  document.addEventListener("keydown", (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "k") {
      e.preventDefault();
      // If mobile overlay exists, open it. Otherwise focus desktop input.
      if (window.innerWidth <= 768 && mobileToggle) {
        openMobileOverlay();
      } else {
        searchInput.focus();
        searchInput.select();
      }
    }
  });

  // --- Mobile overlay ---
  let overlayEl: HTMLElement | null = null;
  let overlayEscapeHandler: ((e: KeyboardEvent) => void) | null = null;
  let overlayScrollY = 0;

  function openMobileOverlay(): void {
    if (overlayEl) return;

    overlayEl = document.createElement("div");
    overlayEl.className = "search-overlay";
    overlayEl.innerHTML = `
      <div class="search-overlay-header">
        <input
          type="search"
          class="search-input"
          placeholder="${escapeHtml(strings.placeholder)}"
          role="combobox"
          aria-expanded="false"
          aria-autocomplete="list"
          aria-haspopup="listbox"
          aria-controls="search-overlay-results"
          aria-label="${escapeHtml(strings.ariaLabel)}"
          autocomplete="off"
          autocorrect="off"
          autocapitalize="none"
          spellcheck="false"
        />
        <button class="search-overlay-close" type="button" aria-label="${escapeHtml(strings.close)}">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
            <line x1="4" y1="4" x2="16" y2="16"></line>
            <line x1="16" y1="4" x2="4" y2="16"></line>
          </svg>
        </button>
      </div>
      <div id="search-overlay-results" class="search-overlay-results" role="listbox" aria-label="${escapeHtml(strings.ariaLabel)}"></div>
      <span class="search-sr-status" aria-live="polite"></span>
    `;

    document.body.appendChild(overlayEl);
    // Lock body scroll. On iOS Safari, `overflow: hidden` alone does not stop
    // touch scroll on the page behind the overlay; pinning the body via
    // `position: fixed` and restoring scroll on close is the reliable approach.
    overlayScrollY = window.scrollY;
    document.body.style.position = "fixed";
    document.body.style.top = `-${overlayScrollY}px`;
    document.body.style.left = "0";
    document.body.style.right = "0";
    document.body.style.width = "100%";

    const overlayInput = overlayEl.querySelector(
      ".search-input"
    ) as HTMLInputElement;
    const overlayResults = overlayEl.querySelector(
      ".search-overlay-results"
    ) as HTMLElement;
    const overlayStatus = overlayEl.querySelector(
      ".search-sr-status"
    ) as HTMLElement;
    const closeBtn = overlayEl.querySelector(
      ".search-overlay-close"
    ) as HTMLButtonElement;

    let overlayActiveIndex = -1;
    let overlayDebounce: ReturnType<typeof setTimeout> | null = null;
    let overlayQuery = "";

    function overlaySetActive(index: number): void {
      const options = overlayResults.querySelectorAll('[role="option"]');
      options.forEach((opt) => opt.setAttribute("aria-selected", "false"));
      overlayActiveIndex = index;
      if (index >= 0 && index < options.length) {
        const opt = options[index];
        opt.setAttribute("aria-selected", "true");
        overlayInput.setAttribute("aria-activedescendant", opt.id);
        opt.scrollIntoView({ block: "nearest" });
      } else {
        overlayInput.removeAttribute("aria-activedescendant");
      }
    }

    async function overlaySearch(query: string): Promise<void> {
      overlayQuery = query;
      if (query.length < MIN_QUERY_LENGTH) {
        if (query.length > 0) {
          overlayInput.setAttribute("aria-expanded", "true");
          renderMinChars(overlayResults, strings);
        } else {
          overlayInput.setAttribute("aria-expanded", "false");
          overlayResults.innerHTML = "";
        }
        if (overlayStatus) overlayStatus.textContent = "";
        return;
      }

      const q = query.length > 100 ? query.slice(0, 100) : query;

      try {
        const ms = await ensureIndex(strings.locale);
        if (overlayQuery !== query) return;
        const results = ms.search(q) as Array<
          MiniSearch.SearchResult & SearchDocument
        >;

        if (results.length === 0) {
          overlayInput.setAttribute("aria-expanded", "true");
          renderNoResults(overlayResults, q, strings);
          if (overlayStatus) overlayStatus.textContent = strings.noResultsStatus;
          return;
        }

        const groups = groupResults(results, q, labels);
        overlayInput.setAttribute("aria-expanded", "true");
        renderResults(overlayResults, groups, q, strings.locale, "overlay");
        overlayActiveIndex = -1;

        const totalShown = groups.reduce((sum, g) => sum + g.items.length, 0);
        if (overlayStatus) {
          overlayStatus.textContent = formatCount(strings.resultsStatus, totalShown);
        }
      } catch (err) {
        console.error("Search failed:", err);
        overlayResults.innerHTML = "";
        overlayInput.setAttribute("aria-expanded", "false");
      }
    }

    overlayInput.addEventListener("input", () => {
      if (overlayDebounce) clearTimeout(overlayDebounce);
      overlayDebounce = setTimeout(() => {
        overlaySearch(overlayInput.value.trim());
      }, DEBOUNCE_MS);
    });

    overlayInput.addEventListener("keydown", (e: KeyboardEvent) => {
      const count = overlayResults.querySelectorAll('[role="option"]').length;
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          overlaySetActive(
            overlayActiveIndex < count - 1 ? overlayActiveIndex + 1 : 0
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          overlaySetActive(
            overlayActiveIndex > 0 ? overlayActiveIndex - 1 : count - 1
          );
          break;
        case "Enter":
          e.preventDefault();
          if (overlayActiveIndex >= 0) {
            const options = overlayResults.querySelectorAll('[role="option"]');
            const selected = options[overlayActiveIndex] as
              | HTMLAnchorElement
              | undefined;
            if (selected?.href) {
              window.location.href = selected.href;
            }
          }
          break;
        case "Escape":
          closeMobileOverlay();
          break;
      }
    });

    closeBtn.addEventListener("click", closeMobileOverlay);

    // Document-level Escape handler (removes itself on close). This catches the
    // key even when focus has not yet landed on the overlay input.
    overlayEscapeHandler = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeMobileOverlay();
    };
    document.addEventListener("keydown", overlayEscapeHandler);

    // Focus the input after a tick (to ensure overlay is rendered)
    requestAnimationFrame(() => {
      overlayInput.focus();
    });
  }

  function closeMobileOverlay(): void {
    if (!overlayEl) return;
    overlayEl.remove();
    overlayEl = null;
    document.body.style.position = "";
    document.body.style.top = "";
    document.body.style.left = "";
    document.body.style.right = "";
    document.body.style.width = "";
    window.scrollTo(0, overlayScrollY);
    if (overlayEscapeHandler) {
      document.removeEventListener("keydown", overlayEscapeHandler);
      overlayEscapeHandler = null;
    }
  }

  if (mobileToggle) {
    mobileToggle.addEventListener("click", openMobileOverlay);
  }
}

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initSearch);
} else {
  initSearch();
}
