'use strict'
document.addEventListener('DOMContentLoaded', function() {

const table = document.querySelector('table.sortable');

if (!table) {
  return;
}

const headers = table.querySelectorAll('th');
const rows = Array.from(document.querySelectorAll('tr'));

const descArrow = '<span class="sort-arrow">&darr;</span>';
const ascArrow = '<span class="sort-arrow">&uarr;</span>';

let currSortCol = null;
let order = -1; // 1=asc, -1=desc

for (let i = 0; i < headers.length; i++) {
  const isNum = headers[i].classList.contains('numeric');
  headers[i].onclick = function() { sortCol(i, isNum); };

  if (i == 0) {
    headers[0].onclick()
  }
}

function getValue(row, col, isNum) {
  const el = row.querySelector('td:nth-of-type(' + (col + 1) + ')');
  let val = el.getAttribute('data-sort-val');

  val = (val ? val : el.innerText);
  val = val.toUpperCase()

  return (isNum ? parseFloat(val) : val);
}

function sortCol(col, isNum) {
  // Track indexes to make the sort stable and allow sorting on multiple rows
  for (let i = 0; i < rows.length; i++) {
    rows[i].lastIndex = i;
  }

  order = ((col == currSortCol) ? -order : -1);

  if (currSortCol != null) {
    const arr = headers[currSortCol].querySelector('.sort-arrow');
    headers[currSortCol].removeChild(arr);
  }

  headers[col].innerHTML += (order < 0 ? descArrow : ascArrow);

  rows.sort(function(rowA, rowB) {
    // Keep the header row first
    if (rowA.lastIndex == 0) {
      return -1;
    } else if (rowB.lastIndex == 0) {
      return 1;
    }

    const a = getValue(rowA, col, isNum);
    const b = getValue(rowB, col, isNum);

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
