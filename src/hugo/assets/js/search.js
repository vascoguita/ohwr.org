/*
SPDX-FileCopyrightText: 2024 CERN (home.cern)

SPDX-License-Identifier: BSD-3-Clause
*/

import Fuse from "https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.mjs";

const searchScriptElement = document.getElementById("search-script");
const searchInputElement = document.getElementById("search-input");
const searchButtonElement = document.getElementById("search-button");
const searchSuggestionsElement = document.getElementById('search-suggestions');
const searchFilterMenuElement = document.getElementById("search-filter-menu");
const searchResultsElement = document.getElementById("search-results");

let fuse;
let filterFuse;
let results;
let suggestions;
let selectedSuggestionIndex = -1;
const perPage = 9;
let paginator;

document.addEventListener("DOMContentLoaded", initializeSearch);

async function initializeSearch() {
  const url = new URL("index.json", window.location.href);
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch data: ${response.status}`);
  }

  const data = await response.json();

  fuse = new Fuse(data, {
    useExtendedSearch: true,
    ignoreLocation: true,
    threshold: 0,
    keys: JSON.parse(searchScriptElement.dataset.keys),
  });

  const filterData = [...new Set(data.flatMap(item =>
    item[searchScriptElement.dataset.filter] || []
  ))];

  filterFuse = new Fuse(filterData, {minMatchCharLength: 2});

  searchInputElement.addEventListener("input", handleSearchInput);
  searchInputElement.addEventListener("keydown", handleSearchKeydown);
  searchButtonElement.addEventListener("click", handleSearchButton);
  paginator = new Paginator(document.getElementById("search-pagination"));
  performSearch();
}

function performSearch() {
  const url = new URL(window.location);
  const query = url.searchParams.get("q");
  const filters = url.searchParams.getAll("f");
  const page = parseInt(url.searchParams.get("p"), 10) || 1;

  displaySearchInput(query);

  hideSuggestions();

  results = query ? fuse.search(query).map(({ item }) => item) : fuse._docs;

  if (filters.length) {
    results = results.filter(result =>
      result[searchScriptElement.dataset.filter] &&
      filters.every(filter =>
        result[searchScriptElement.dataset.filter].includes(filter)
      )
    );
  }

  results = [...results].sort((a, b) => b.weight - a.weight);

  paginator.show(Math.ceil(results.length / perPage), page);

  displaySearchFilters(
    filters,
    results.flatMap(result =>
      result[searchScriptElement.dataset.filter] || []
    ).filter(filter => !filters.includes(filter))
  );
}

function displaySearchInput(query) {
  searchInputElement.value = query;
}

function displaySearchResults(startIndex, endIndex) {
  const paginatedResults = results.slice(startIndex, endIndex);

  searchResultsElement.innerHTML = paginatedResults.length ? "" : "<p>No results found.</p>";

  if (searchScriptElement.dataset.view === "grid") {
    searchResultsElement.classList.add("row");
  }
  paginatedResults.forEach(item => {
    const card = Card.create(
      searchScriptElement.dataset.view,
      item.image,
      item.project,
      item.title,
      item.date,
      item.text,
      item.url
    );
    searchResultsElement.appendChild(card.element);
  });
}

function displaySearchFilters(activeFilters, inactiveFilters) {
  searchFilterMenuElement.innerHTML = "";

  if (activeFilters.length) {
    searchFilterMenuElement.classList.add("show");
  }

  activeFilters.forEach(item => {
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

function handleSearchInput(event) {
  const url = new URL(window.location);
  const filters = url.searchParams.getAll("f");
  const inputValue = event.target.value.trim();
  suggestions = inputValue ? filterFuse.search(inputValue).map(({ item }) => item) : [];
  suggestions = suggestions.filter(filter => !filters.includes(filter)).slice(0, 8);
  displaySuggestions(suggestions);
}

function handleSearchKeydown(event) {
  const inputValue = event.target.value.trim();
  if (event.key === "Enter") {
    if (selectedSuggestionIndex >= 0) {
      updateFilter(suggestions[selectedSuggestionIndex]);
    } else {
      updateQuery(inputValue);
    }
  } else if (event.key === "ArrowDown") {
    selectedSuggestionIndex = (selectedSuggestionIndex + 1) % suggestions.length;
    highlightSuggestion(selectedSuggestionIndex);
  } else if (event.key === "ArrowUp") {
    selectedSuggestionIndex = (selectedSuggestionIndex - 1 + suggestions.length) % suggestions.length;
    highlightSuggestion(selectedSuggestionIndex);
  }
}

function handleSearchButton() {
  updateQuery(searchInputElement.value.trim());
}

function updateQuery(query) {
  const url = new URL(window.location);

  if (query) {
    url.searchParams.set("q", query);
  } else {
    url.searchParams.delete("q");
  }
  url.searchParams.delete("p");
  window.history.pushState({}, "", url);
  performSearch();
}

function displaySuggestions(suggestions) {
  selectedSuggestionIndex = -1;
  searchSuggestionsElement.querySelectorAll(".search-suggestion-item").forEach(item => item.remove());
  suggestions.forEach(suggestion => {
    const button = document.createElement("button");
    button.className = "search-suggestion-item text-muted pl-3 row w-100 m-0";
    button.innerText = suggestion;
    button.value = suggestion;
    button.addEventListener("click", handleSuggestionButton);
    searchSuggestionsElement.appendChild(button);
  });
  if (suggestions.length) {
    searchSuggestionsElement.style.display = "block";
  } else {
    searchSuggestionsElement.style.display = "none";
  }
}

function updateFilter(filter) {
  const url = new URL(window.location);

  url.searchParams.append("f", filter);
  url.searchParams.delete("q");
  url.searchParams.delete("p");
  window.history.pushState({}, "", url);
  performSearch();
}

function handleFilterButton(event) {
  const filter = event.currentTarget.value;
  const url = new URL(window.location);

  if (event.currentTarget.dataset.state === "active") {
    url.searchParams.delete("f", filter);
  } else {
    url.searchParams.append("f", filter);
  }
  url.searchParams.delete("p");
  window.history.pushState({}, "", url);
  performSearch();
}

function handleSuggestionButton(event) {
  updateFilter(event.currentTarget.value);
}

function hideSuggestions() {
  searchSuggestionsElement.style.display = "none";
}

function highlightSuggestion(index) {
  const suggestionButtons = searchSuggestionsElement.querySelectorAll(".search-suggestion-item");
  suggestionButtons.forEach((button, i) => {
    if (i === index) {
      button.dataset.state = "active";
    } else {
      button.dataset.state = "";
    }
  });
}

class Card {
  constructor(image, project, title, date, text, url) {
    this.image = image;
    this.project = project;
    this.title = title;
    this.date = date;
    this.text = text;
    this.url = url;
  }

  static create(type, image, project, title, date, text, url) {
    switch (type) {
      case "grid":
        return new GridCard(image, project, title, date, text, url);
      case "list":
        return new ListCard(image, project, title, date, text, url);
      default:
        throw new Error(`Invalid card type: ${type}`);
    }
  }
}

class GridCard extends Card {
  get element () {
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
}

class ListCard extends Card {
  get element() {
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

class Paginator {
  constructor(element) {
    this.element = element;
    this.handle = this.handle.bind(this);
  }

  button(value, text, active) {
    const li = document.createElement("li");
    li.className = `page-item${active ? " active" : ""}`;
    const button = document.createElement("button");
    button.classList.add("page-link");
    button.value = value;
    button.innerText = text;
    button.addEventListener("click", this.handle);
    li.appendChild(button);
    return li;
  }

  show(total, page) {
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
    displaySearchResults((page - 1) * perPage, (page - 1) * perPage + perPage);
  }

  handle(event) {
    const page = parseInt(event.currentTarget.value, 10);
    const url = new URL(window.location);

    url.searchParams.set("p", page);
    window.history.pushState({}, "", url);
    this.show(Math.ceil(results.length / perPage), page);
  }
}
