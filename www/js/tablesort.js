'use strict'
document.addEventListener('DOMContentLoaded', function() {

const table = document.querySelector('table.sortable');
const headers = table.querySelectorAll('th');
const rows = Array.from(document.querySelectorAll('tr'));

let currSortCol = null;
let order = 1; // 1=asc, -1=desc

for(let i = 0; i < headers.length; i++) {
  const isNum = headers[i].classList.contains('numeric');
  headers[i].onclick = function() { sortCol(i + 1, isNum); };
}

function sortCol(col, isNum) {
  // Track indexes to make the sort stable and allow sorting on multiple rows
  for(let i = 0; i < rows.length; i++) {
    rows[i].lastIndex = i;
  }

  order = ((col == currSortCol) ? -order : order);

  rows.sort(function(rowA, rowB) {
    // Keep the header row first
    if (rowA.lastIndex == 0) {
      return -1;
    } else if (rowB.lastIndex == 0) {
      return 1;
    }

    const q = 'td:nth-of-type(' + col + ')';
    let a = rowA.querySelector(q).innerText.toUpperCase();
    let b = rowB.querySelector(q).innerText.toUpperCase();

    if (isNum) {
      a = parseFloat(a);
      b = parseFloat(b);
    }

    // Order such that empty strings always come last
    if (a === b) {
      return rowA.lastIndex - rowB.lastIndex;
    } else if (!a) {
      return 1;
    } else if (!b) {
      return -1;
    } else {
      return ((a < b) ? -1 : 1) * order;
    }
  });

  while (table.lastChild) {
    table.lastChild.remove();
  }

  for (let i = 0; i < rows.length; i++) {
    table.appendChild(rows[i]);
  }

  currSortCol = col;
}

});
