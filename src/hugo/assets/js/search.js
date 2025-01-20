
/*
SPDX-FileCopyrightText: 2024 CERN (home.cern)

SPDX-License-Identifier: BSD-3-Clause
*/

const fuseOptions = {
	keys: [
        'title',
		'categories',
		'content',
        'url',
	]
};

let fuse

fetch("index.json")
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    fuse = new Fuse(data, fuseOptions);
    console.log("Loaded:", data);
  })
  .catch(error => console.error("Error loading JSON:", error));

const searchInput = document.getElementById('searchInput');
const searchCategory = document.getElementById('searchCategory');
const searchButton = document.getElementById('searchButton');

searchInput.addEventListener('input', performSearch);
searchCategory.addEventListener('change', performSearch);
searchButton.addEventListener('click', performSearch);

function performSearch() {
  const searchQuery = searchInput.value.trim();
  const selectedCategory = searchCategory.value;

  let results = fuse.search(searchQuery);

  console.log("Match projects:", results);
}