/*
SPDX-FileCopyrightText: 2024 CERN (home.cern)

SPDX-License-Identifier: BSD-3-Clause
*/

import Fuse from "https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.mjs";

document.addEventListener("DOMContentLoaded", async () => {
  const url = new URL(window.location);
  const config = await SearchConfig.fromUrl(new URL("index.json", url.href));
  const fuse = new Fuse(config.index, {
    useExtendedSearch: true,
    ignoreLocation: true,
    threshold: 0,
    keys: config.keys
  });
  const results = new SearchResults(
    document.getElementById("search-results"), config.view
  );
  const input = new SearchInput(
    document.getElementById("search-input"), url.searchParams.get("q")
  );
  const suggestions = new SearchSuggestions(
    document.getElementById("search-suggestions")
  );
  const pagination = new SearchPagination(
    document.getElementById("search-pagination"), results
  );
  const button = new SearchButton(document.getElementById("search-button"));
  const filters = new SearchFilters(
    document.getElementById("search-filters"), config.filter
  );
  const search = new Search(
    fuse, input, suggestions, pagination, button, filters, results
  );
  search.search();
  search.show(parseInt(url.searchParams.get("p"), 10) || 1);
});

class Search {
  constructor(
    fuse, input, suggestions, pagination, button, filters, results
  ) {
    this.fuse = fuse;
    this.input = input;
    this.suggestions = suggestions;
    this.pagination = pagination;
    this.button = button;
    this.filters = filters;
    this.results = results;

    this.handleInputKeydown = this.handleInputKeydown.bind(this);
    this.input.element.addEventListener("keydown", this.handleInputKeydown);

    this.handleButtonClick = this.handleButtonClick.bind(this);
    this.button.element.addEventListener("click", this.handleButtonClick);
  }

  search() {
    let results;
    if (this.input.value) {
      results = this.fuse.search(this.input.value).map(({ item }) => item);
    } else {
      results = this.fuse._docs;
    }
    this.results.results = [...results].sort((a, b) => {
      return (b.weight || 0) - (a.weight || 0);
    });
  }

  show(page = 1) {
    this.pagination.show(Math.ceil(this.results.results.length / 9), page);
  }

  handleInputKeydown(event) {
    if (event.key === "Enter") {
      this.search();
      this.show();
    }
  }

  handleButtonClick() {
    this.search();
    this.show();
  }
}

class SearchConfig {
  constructor(keys, filter, view, index) {
    this.keys = keys;
    this.filter = filter;
    this.view = view;
    this.index = index;
  }

  static async fromUrl(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.status}`);
    }
    const data = await response.json();
    return this.fromDict(data);
  }

  static fromDict(data) {
    return new SearchConfig(
      data['keys'], data['filter'], data['view'], data['index']
    );
  }
}

class SearchInput {
  constructor(element, value) {
    this.element = element;
    this.value = value;

    this.handleKeydown = this.handleKeydown.bind(this);
    this.element.addEventListener("keydown", this.handleKeydown);
  }

  get value() {
    return this.element.value.trim();
  }

  set value(value) {
    this.element.value = value;
  }

  set param(value) {
    const url = new URL(window.location);
    if (this.value) {
      url.searchParams.set("q", value);
    } else {
      url.searchParams.delete("q");
    }
    window.history.pushState({}, "", url);
  }

  handleKeydown(event) {
    if (event.key === "Enter") {
      this.param = this.value;
    }
  }
}

class SearchSuggestions {
  constructor(element) {
    this.element = element;
  }
}

class SearchPagination {
  constructor(element, results) {
    this.element = element;
    this.results = results;
    this.handleButtonClick = this.handleButtonClick.bind(this);
  }

  set param(value) {
    const page = parseInt(value, 10);
    const url = new URL(window.location);

    url.searchParams.set("p", page);
    window.history.pushState({}, "", url);
  }

  button(value, text, active) {
    const li = document.createElement("li");
    li.classList.add("page-item");
    if (active) {
      li.classList.add("active");
    }
    const button = document.createElement("button");
    button.classList.add("page-link");
    button.value = value;
    button.innerText = text;
    button.addEventListener("click", this.handleButtonClick);
    li.appendChild(button);
    return li;
  }

  show(total, page) {
    this.param = page;
    const ul = document.createElement("ul");
    ul.classList.add("pagination");
    if (page > 1) {
      ul.appendChild(this.button(1, "««", false));
      ul.appendChild(this.button(page - 1, "«", false));
    }
    const startPage = Math.max(1, Math.min(page - 2, total - 4));
    const endPage = Math.min(total, Math.max(page + 2, 5));
    for (let i = startPage; i <= endPage; i++) {
      ul.appendChild(this.button(i, i, i === page));
    }
    if (page < total) {
      ul.appendChild(this.button(page + 1, "»", false));
      ul.appendChild(this.button(total, "»»", false));
    }
    this.element.replaceChildren(ul);
    this.results.show((page - 1) * 9, page * 9);
  }

  handleButtonClick(event) {
    this.show(
      Math.ceil(this.results.results.length / 9),
      parseInt(event.currentTarget.value, 10)
    );
  }
}

class SearchButton {
  constructor(element) {
    this.element = element;
  }
}

class SearchFilters {
  constructor(element, filter) {
    this.element = element;
    this.filter = filter;
  }

  show(activeFilters, inactiveFilters) {
    searchFilterMenuElement.innerHTML = "";

    if (activeFilters.length) {
      this.element.classList.add("show");
    }

    activeFilters.map(item => {
      const activeFilter = new SearchFilter(item);
      const button = Object.assign(document.createElement("button"), {
        type: "button",
        className: "search-filter-button",
        value: item,
        innerHTML: `<i class="fas fa-times mr-1"></i>${item}`
      });
      button.dataset.state = "active";
      button.addEventListener("click", handleFilterButton);
      searchFilterMenuElement.appendChild(button);
    });

    inactiveFilters = Object.values(
      inactiveFilters.reduce((acc, filter) => {
        acc[filter] = acc[filter] || { filter, count: 0 };
        acc[filter].count++;
        return acc;
      }, {})
    ).sort((a, b) => b.count - a.count);

    inactiveFilters.forEach(item => {
      const button = Object.assign(document.createElement("button"), {
        type: "button",
        className: "search-filter-button",
        value: item.filter,
        innerHTML: `${item.filter}
          <span class="badge badge-filter ml-1">${item.count}</span>`
      });
      button.addEventListener("click", handleFilterButton);
      searchFilterMenuElement.appendChild(button);
    });
  }

}

class SearchFilter {
  constructor(filter, count) {
    this.filter = filter;
    this.count = count;
  }

  get activeView() {
    const i = document.createElement("i");
    i.classList.add("fas", "fa-times", "mr-1");
    const button = document.createElement("button");
    button.type = "button";
    button.classList.add("search-filter-button", "active");
    button.value = this.filter;
    button.replaceChildren(i, document.createTextNode(this.filter));
    return button;
  }

  get inactiveView() {
    const span = document.createElement("span");
    span.classList.add("badge", "badge-filter", "ml-1");
    span.innerText = this.count;
    const button = document.createElement("button");
    button.type = "button"
    button.classList.add("search-filter-button");
    button.value = this.filter;
    button.replaceChildren(document.createTextNode(this.filter), span);
    return button;
  }
}

class SearchResults {
  constructor(element, view) {
    this.element = element;
    this.view = view;
    this.results = [];
  }

  get results() {
    return this._results;
  }

  set results(results) {
    if (results.length) {
      this._results = results.map(item => new SearchResult(
        item.image,
        item.project,
        item.title,
        item.date,
        item.text,
        item.url
      ));
    } else {
      this._results = [];
    }
  }

  show(start, end) {
    const results = this.results.slice(start, end);
    if (results.length) {
      let cards;
      if (this.view === "grid") {
        this.element.classList.add("row");
        cards = results.map(result => result.gridView);
      } else if (this.view === "list") {
        this.element.classList.remove("row");
        cards = results.map(result => result.listView);
      }
      this.element.replaceChildren(...cards);
    } else {
      this.element.classList.remove("row");
      const text = document.createElement("p");
      text.innerText = "No results found.";
      this.element.replaceChildren(text);
    }
  }
}

class SearchResult {
  constructor(image, project, title, date, text, url) {
    this.image = image;
    this.project = project;
    this.title = title;
    this.date = date;
    this.text = text;
    this.url = url;
  }

  get gridView() {
    const frame = document.createElement("div")
    frame.classList.add(
      "mb-3", "position-relative", "embed-responsive", "embed-responsive-4by3"
    );
    if (this.image) {
      const img = document.createElement("img");
      img.classList.add(
        "mh-100", "mw-100", "position-absolute", "grid-card-image"
      );
      img.src = this.image;
      frame.appendChild(img);
    } else {
      const svg = document.createElementNS(
        "http://www.w3.org/2000/svg", "svg"
      );
      svg.setAttribute("width", "400");
      svg.setAttribute("height", "300");
      svg.classList.add(
        "mh-100", "mw-100", "position-absolute", "grid-card-image"
      );
      const circle = document.createElementNS(
        "http://www.w3.org/2000/svg", "circle"
      );
      circle.setAttribute("cx", "50%");
      circle.setAttribute("cy", "50%");
      circle.setAttribute("r", "100");
      circle.setAttribute(
        "fill",
        `hsl(${this.title.split("").reduce(
          (acc, char) => acc + char.charCodeAt(0), 0
        ) % 360}, 50%, 30%)`
      );
      svg.appendChild(circle);
      const text = document.createElementNS(
        "http://www.w3.org/2000/svg", "text"
      );
      text.setAttribute("x", "50%");
      text.setAttribute("y", "50%");
      text.setAttribute("dy", "0.35em");
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("fill", "white");
      text.setAttribute("font-size", "100");
      text.setAttribute("font-family", "Arial, sans-serif");
      text.appendChild(document.createTextNode(this.title[0].toUpperCase()));
      svg.appendChild(text);
      frame.appendChild(svg);
    }
    const body = document.createElement("div");
    body.classList.add("card-body", "d-flex", "flex-column");
    body.appendChild(frame);
    const link = document.createElement("a");
    link.href = this.url;
    link.classList.add("stretched-link", "post-title");
    link.innerText = this.title;
    const title = document.createElement("h3");
    title.appendChild(link);
    body.appendChild(title);
    const summary = document.createElement("p");
    summary.classList.add("card-text");
    summary.innerText = this.text;
    body.appendChild(summary);
    const card = document.createElement("div");
    card.classList.add(
      "card", "interactive-card", "shadow-lg", "border-0", "h-100"
    );
    card.appendChild(body);
    const element = document.createElement("div");
    element.classList.add("col-lg-4", "col-sm-6", "mb-5");
    element.appendChild(card);
    return element;
  }

  get listView() {
    const body = document.createElement("div");
    body.classList.add("card-body");
    if (this.project) {
      const project = document.createElement("h6");
      const icon = document.createElement("i");
      icon.classList.add("fas", "fa-rss");
      project.appendChild(icon);
      const text = document.createElement("small");
      text.classList.add("ml-1");
      text.innerText = this.project;
      project.appendChild(text);
      body.appendChild(project);
    }
    const title = document.createElement("h3");
    const link = document.createElement("a");
    link.href = this.url;
    link.classList.add("stretched-link", "post-title");
    link.innerText = this.title;
    title.appendChild(link);
    body.appendChild(title);
    if (this.date) {
      const date = document.createElement("div");
      date.classList.add("mb-2");
      const time = document.createElement("time");
      time.innerText = this.date;
      date.appendChild(time);
      body.appendChild(date);
    }
    const text = document.createElement("p");
    text.classList.add("card-text");
    text.innerText = this.text;
    body.appendChild(text);
    const element = document.createElement("div");
    element.classList.add(
      "card", "interactive-card", "border-0", "shadow-lg", "mb-4"
    );
    if (this.image) {
      const img = document.createElement("img")
      img.classList.add("m-3", "w-100", "mh-100", "rounded");
      img.src = this.image;
      const frame = document.createElement("div");
      frame.classList.add("col-md-3");
      frame.appendChild(img);
      const row = document.createElement("div");
      row.classList.add("row");
      row.appendChild(frame);
      const column = document.createElement("div");
      column.classList.add("col-md-9", "p-0", "position-static");
      column.appendChild(body);
      row.appendChild(column);
      element.appendChild(row);
    } else {
      element.appendChild(body);
    }
    return element;
  }
}
