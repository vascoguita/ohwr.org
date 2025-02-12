/*
SPDX-FileCopyrightText: 2024 CERN (home.cern)

SPDX-License-Identifier: BSD-3-Clause
*/

import Fuse from 'https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.mjs';

const fuseOptions = {
  useExtendedSearch: true,
  ignoreLocation: true,
  threshold: 0,
  keys: [
    { name: 'title', weight: 3 },
    { name: 'tags', weight:2 },
    { name: 'content', weight: 1 }
  ]
};

let fuse;

initializeSearch();

function initializeSearch() {
  const searchInput = document.getElementById('searchInput');
  const searchButton = document.getElementById('searchButton');
  const availableTags = document.getElementById('availableTags');

  searchInput.addEventListener('keypress', searchEventListener);
  searchButton.addEventListener('click', searchEventListener);
  availableTags.addEventListener('click', tagsEventListener);

  fetchData()
    .then(data => {
      fuse = new Fuse(data, fuseOptions);
      search();
    })
    .catch(error => console.error("Error loading JSON:", error));
}

async function fetchData() {
  const response = await fetch(new URL('index.json', window.location.href).href);

  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  return await response.json();
}

function search() {
  const url = new URL(window.location);
  const query = url.searchParams.get('q');
  const selectedTags = url.searchParams.getAll('t');

  let results = fuse._docs;

  if (query) {
    results = fuse.search(query).map(result => result.item);
  }

  let filteredResults = results;

  if (selectedTags.length) {
    filteredResults = results.filter(result => result.tags && result.tags.every(tag => selectedTags.includes(tag))); 
  }

  let sortedResults = [...filteredResults].sort((a, b) => b.weight - a.weight);

  let availableTags = sortedResults.flatMap(result => result.tags || []).filter(tag => !selectedTags.includes(tag));

  console.log(availableTags.reduce((acc, tag) => {
    acc[tag] = (acc[tag] || 0) + 1;
    return acc;
  }, {}));

  displaySearchInput(query);
  displaySelectedTags(selectedTags);
  displayAvailableTags(availableTags);
  displayResults(sortedResults);
}

function displaySearchInput(query) {
  document.getElementById('searchInput').value = query;
}

function displaySelectedTags(tags) {
  const selectedTags = document.getElementById('selectedTags');

  selectedTags.innerHTML = '';
  tags.forEach(item => {
    selectedTags.innerHTML +=
      `<button type="button" class="selected-tag-button" value="${item}">
        ${item}
      </button>`
  });
}

function displayAvailableTags(tags) {
  const availableTags = document.getElementById('availableTags');
  const tagCounts = Object.values(
    tags.reduce((acc, tag) => {
      acc[tag] = acc[tag] || { tag, count: 0 };
      acc[tag].count++;
      return acc;
    }, {})).sort((a, b) => b.count - a.count);

  availableTags.innerHTML = '';

  tagCounts.forEach(item => {
    availableTags.innerHTML +=
      `<button type="button" class="available-tag-button" value="${item.tag}">
        ${item.tag} <span class="badge badge-primary">${item.count}</span>
      </button>`
  });
}

function displayResults(results) {
  const searchResults = document.getElementById('searchResults');

  searchResults.innerHTML = results.length ? '' : '<p>No results found.</p>';

  results.forEach(item => {
    searchResults.innerHTML += atob(item.card);
  });
}

function tagsEventListener(event) {
    const tag = event.target.getAttribute('value');
    const url = new URL(window.location);
  
    url.searchParams.append('t', tag)
    window.history.pushState({}, '', url);
    search();
}

function searchEventListener(event) {
  if (event.type === 'keypress' && event.key !== "Enter") return;

  const searchQuery = document.getElementById('searchInput').value.trim();
  const url = new URL(window.location);

  if (searchQuery) {
    url.searchParams.set('q', searchQuery);
  } else {
    url.searchParams.delete('q');
  }
  window.history.pushState({}, '', url);
  search();
}
