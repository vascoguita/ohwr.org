/*
SPDX-FileCopyrightText: 2024 CERN (home.cern)

SPDX-License-Identifier: BSD-3-Clause
*/

import Fuse from "https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.mjs";


document.addEventListener("DOMContentLoaded", () => {
  const data = SearchIndex.fromUrl(new URL("index.json", window.location.href)).data;
  const fuse = new Fuse(data, {
    useExtendedSearch: true,
    ignoreLocation: true,
    threshold: 0,
    keys: JSON.parse(document.getElementById("search-script").dataset.keys),
  });
  const search = Search(fuse,
    new SearchInput(document.getElementById("search-input")),
    new SearchSuggestions(document.getElementById('search-suggestions')),
    new SearchPagination(document.getElementById("search-pagination")),
    new SearchButton(document.getElementById("search-button")),
    new SearchFilters(document.getElementById("search-filters")),
    new SearchResults(document.getElementById("search-results")),
    new SearchScript(document.getElementById("search-script"))
  );
});

class Search {
  constructor(
    fuse, input, suggestions, pagination, button, filters, results,
  ) {
    this.fuse = fuse;
    this.input = input;
    this.suggestions = suggestions;
    this.pagination = pagination;
    this.button = button;
    this.filters = filters;
    this.results = results;
    this.search();
  }

  search() {
    let results;
    if (this.input.value) {
      results = this.fuse.search(this.input.value).map(({ item }) => item);
    } else {
      results = fuse._docs;
    }
  }
}

class SearchIndex {
  constructor(data) {
    this.data = data;
  }

  static async fromUrl(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.status}`);
    }
    const data = await response.json();
    return new SearchIndex(data);
  }
}

class SearchInput {
  constructor(element) {
    this.element = element;
    this.value = this.param;
  }

  get value() {
    return this.element.value;
  }

  set value(value) {
    this.element.value = value;
  }

  get param() {
    const url = new URL(window.location);
    return url.searchParams.get("q");
  }
}

class SearchSuggestions {
  constructor(element) {
    this.element = element;
  }
}

class SearchPagination {
  constructor(element) {
    this.element = element;
  }
}

class SearchButton {
  constructor(element) {
    this.element = element;
  }
}

class SearchFilters {
  constructor(element) {
    this.element = element;
  }
}

class SearchResults {
  constructor(element) {
    this.element = element;
  }
}

class SearchScript {
  constructor(element) {
    this.element = element;
  }
}
