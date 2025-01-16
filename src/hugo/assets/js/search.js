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
    { name: 'categories', weight:2 },
    { name: 'content', weight: 1 }
  ]
};

let fuse;

document.addEventListener('DOMContentLoaded', () => {
  initializeSearch();
});

function fetchData() {
  return fetch(new URL('index.json', window.location.href).href)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    });
}

function initializeSearch() {
  const searchInput = document.getElementById('searchInput');
  const searchCategory = document.getElementById('searchCategory');
  const searchButton = document.getElementById('searchButton');

  searchInput.addEventListener('input', search);
  searchCategory.addEventListener('change', search);
  searchButton.addEventListener('click', search);

  fetchData()
    .then(data => {
      fuse = new Fuse(data, fuseOptions);
      displayResults(fuse._docs);
    })
    .catch(error => console.error("Error loading JSON:", error));
}

function search() {
  const searchQuery = document.getElementById('searchInput').value.trim();
  const selectedCategory = document.getElementById('searchCategory').value;

  let results = searchQuery ? fuse.search(searchQuery).map(result => result.item) : fuse._docs;

  if (selectedCategory) {
    results = filterByCategory(results, selectedCategory);
  }

  displayResults(results);
}

function filterByCategory(results, category) {
  return results.filter(item => item.categories && item.categories.includes(category));
}

function displayResults(results) {
  const resultsContainer = document.getElementById('searchResults');
  resultsContainer.innerHTML = results.length ? '' : '<p>No results found.</p>';

  results.forEach(item => {
    resultsContainer.innerHTML += atob(item.card);
  });
}
