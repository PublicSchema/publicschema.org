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

// Shared index promise: ensures only one fetch + build happens
let indexPromise: Promise<MiniSearch<SearchDocument>> | null = null;

function ensureIndex(): Promise<MiniSearch<SearchDocument>> {
  if (indexPromise) return indexPromise;
  indexPromise = fetch("/search-index.json")
    .then((res) => {
      if (!res.ok) throw new Error(`Search index fetch failed: ${res.status}`);
      return res.json();
    })
    .then((docs: SearchDocument[]) => {
      const ms = new MiniSearch<SearchDocument>({
        fields: ["title", "body", "keywords"],
        storeFields: ["type", "title", "body", "path", "meta", "keywords"],
        searchOptions: {
          boost: { title: 3, body: 1, keywords: 0.5 },
          prefix: true,
          fuzzy: 0.2,
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

const TYPE_LABELS: Record<string, string> = {
  concept: "Concepts",
  property: "Properties",
  vocabulary: "Vocabularies",
  doc: "Docs",
};

const DEBOUNCE_MS = 120;
const MIN_QUERY_LENGTH = 2;
const MAX_RESULTS = 8;
const MAX_PER_GROUP = 3;

// Highlight matched substring in a title
function highlightMatch(title: string, query: string): string {
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`(${escaped})`, "gi");
  return escapeHtml(title).replace(regex, "<mark>$1</mark>");
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

// Find which vocabulary value label matched the query
function findMatchedValue(keywords: string, query: string): string | null {
  if (!keywords) return null;
  const q = query.toLowerCase();
  const labels = keywords.split(/\s+/);
  // Try multi-word match first (e.g., "Never Married")
  const fullKeywords = keywords.split(/\s{2,}|\t/);
  for (const label of fullKeywords) {
    if (label.toLowerCase().includes(q)) return label.trim();
  }
  for (const label of labels) {
    if (label.toLowerCase().includes(q)) return label;
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
  query: string
): GroupedResults[] {
  const groups: Record<string, GroupedResults> = {};

  // First pass: collect up to MAX_PER_GROUP per type (ensures type diversity)
  for (const result of results) {
    const type = result.type;
    if (!groups[type]) {
      groups[type] = {
        type,
        label: TYPE_LABELS[type] || type,
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
  idPrefix: string = "desktop"
): void {
  let optionIndex = 0;
  let html = "";

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
      html += `<a class="search-result" href="${escapeHtml(result.path)}" role="option" id="search-opt-${idPrefix}-${optionIndex}" aria-selected="false">
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

function renderNoResults(container: HTMLElement, query: string): void {
  container.innerHTML = `<div class="search-no-results">
    No results for "${escapeHtml(truncate(query, 60))}"
    <div style="margin-top: var(--space-sm)">
      Browse: <a href="/concepts/">Concepts</a> &middot; <a href="/properties/">Properties</a> &middot; <a href="/vocab/">Vocabularies</a>
    </div>
  </div>`;
}

function renderMinChars(container: HTMLElement): void {
  container.innerHTML = `<div class="search-min-chars">Type at least 2 characters to search</div>`;
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

  if (!searchInput || !resultsContainer) return;

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
        renderMinChars(resultsContainer!);
      } else {
        hideResults();
      }
      if (srStatus) srStatus.textContent = "";
      return;
    }

    // Truncate very long queries
    const q = query.length > 100 ? query.slice(0, 100) : query;

    try {
      const ms = await ensureIndex();
      // Check that query hasn't changed during async wait
      if (currentQuery !== query) return;
      const results = ms.search(q) as Array<
        MiniSearch.SearchResult & SearchDocument
      >;

      if (results.length === 0) {
        showResults();
        renderNoResults(resultsContainer!, q);
        if (srStatus) srStatus.textContent = "No results found";
        return;
      }

      const groups = groupResults(results, q);
      showResults();
      renderResults(resultsContainer!, groups, q);
      activeIndex = -1;

      const totalShown = groups.reduce((sum, g) => sum + g.items.length, 0);
      if (srStatus) {
        srStatus.textContent = `${totalShown} result${totalShown === 1 ? "" : "s"} found`;
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
    ensureIndex();
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

  function openMobileOverlay(): void {
    if (overlayEl) return;

    overlayEl = document.createElement("div");
    overlayEl.className = "search-overlay";
    overlayEl.innerHTML = `
      <div class="search-overlay-header">
        <input
          type="search"
          class="search-input"
          placeholder="Search concepts, properties..."
          role="combobox"
          aria-expanded="false"
          aria-autocomplete="list"
          aria-haspopup="listbox"
          aria-controls="search-overlay-results"
          aria-label="Search PublicSchema"
          autocomplete="off"
        />
        <button class="search-overlay-close" type="button" aria-label="Close search">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
            <line x1="4" y1="4" x2="16" y2="16"></line>
            <line x1="16" y1="4" x2="4" y2="16"></line>
          </svg>
        </button>
      </div>
      <div id="search-overlay-results" class="search-overlay-results" role="listbox" aria-label="Search results"></div>
      <span class="search-sr-status" aria-live="polite"></span>
    `;

    document.body.appendChild(overlayEl);
    document.body.style.overflow = "hidden";

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
          renderMinChars(overlayResults);
        } else {
          overlayInput.setAttribute("aria-expanded", "false");
          overlayResults.innerHTML = "";
        }
        if (overlayStatus) overlayStatus.textContent = "";
        return;
      }

      const q = query.length > 100 ? query.slice(0, 100) : query;

      try {
        const ms = await ensureIndex();
        if (overlayQuery !== query) return;
        const results = ms.search(q) as Array<
          MiniSearch.SearchResult & SearchDocument
        >;

        if (results.length === 0) {
          overlayInput.setAttribute("aria-expanded", "true");
          renderNoResults(overlayResults, q);
          if (overlayStatus) overlayStatus.textContent = "No results found";
          return;
        }

        const groups = groupResults(results, q);
        overlayInput.setAttribute("aria-expanded", "true");
        renderResults(overlayResults, groups, q, "overlay");
        overlayActiveIndex = -1;

        const totalShown = groups.reduce((sum, g) => sum + g.items.length, 0);
        if (overlayStatus) {
          overlayStatus.textContent = `${totalShown} result${totalShown === 1 ? "" : "s"} found`;
        }
      } catch {
        // Silently fail; user can still browse
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

    // Focus the input after a tick (to ensure overlay is rendered)
    requestAnimationFrame(() => {
      overlayInput.focus();
    });
  }

  function closeMobileOverlay(): void {
    if (!overlayEl) return;
    overlayEl.remove();
    overlayEl = null;
    document.body.style.overflow = "";
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
