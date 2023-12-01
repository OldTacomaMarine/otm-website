'use strict'
document.addEventListener('DOMContentLoaded', function() {

const ASCENDING = 1;
const DESCENDING = -ASCENDING;
const INITIAL_SORT_COL = 'Bore';
const DEFAULT_NUM_SORT_DIR = DESCENDING;
const DEFAULT_SORT_DIR = ASCENDING;
const DESC_ARROW = '<span class="sort-arrow">&darr;</span>';
const ASC_ARROW = '<span class="sort-arrow">&uarr;</span>';

const tables = document.querySelectorAll('table.sortable');

for (let i = 0; i < tables.length; i++) {
  initTable(tables[i]);
}


function initTable(table) {
  table.currSortCol = null;
  table.order = null;

  const headers = table.querySelectorAll('th');

  // Add an onclick handler to each table header
  for (let i = 0; i < headers.length; i++) {
    const isNum = headers[i].classList.contains('numeric');
    headers[i].onclick = function() { sortCol(table,i, isNum); };

    // Sort the initially sorted column
    if (headers[i].textContent === INITIAL_SORT_COL) {
      sortCol(table, i, isNum);
    }
  }
}	

function getValue(row, col, isNum) {
  const el = row.querySelector('td:nth-of-type(' + (col + 1) + ')');
  let val = el.getAttribute('data-sort-val');

  val = (val ? val : el.innerText);
  val = val.toUpperCase()

  return (isNum ? parseFloat(val) : val);
}

function sortCol(table, col, isNum) {
  const headers = table.querySelectorAll('th');
  const rows = Array.from(table.querySelectorAll('tr'));

  // Track indexes to make the sort stable and allow sorting on multiple rows
  for (let i = 0; i < rows.length; i++) {
    rows[i].lastIndex = i;
  }

  // If this column is not the previously sorted column, set the sort
  // direction to be the default according to its data type.
  if (col != table.currSortCol) {
    table.order = (isNum ? DEFAULT_NUM_SORT_DIR : DEFAULT_SORT_DIR);
  } else {
    // This column was already sorted, sort in reverse
    table.order = -table.order;
  }

  // Remove the sort arrow from the old sorted column (if any).
  // If this column was the old one, we still do this to change arrow direction.
  if (table.currSortCol != null) {
    const arr = headers[table.currSortCol].querySelector('.sort-arrow');
    headers[table.currSortCol].removeChild(arr);
  }

  // Add the sort direction arrow to this column
  headers[col].innerHTML += (table.order == DESCENDING ? DESC_ARROW : ASC_ARROW);

  rows.sort(function(rowA, rowB) {
    // Keep the header row first
    if (rowA.lastIndex == 0) {
      return -1;
    } else if (rowB.lastIndex == 0) {
      return 1;
    }

    const a = getValue(rowA, col, isNum);
    const b = getValue(rowB, col, isNum);

    // Order such that empty strings always come last regardless of sort direction
    if (a === b) {
      return rowA.lastIndex - rowB.lastIndex;
    } else if (!a) {
      return 1;
    } else if (!b) {
      return -1;
    } else {
      return ((a < b) ? -1 : 1) * table.order;
    }
  });

  while (table.lastChild) {
    table.lastChild.remove();
  }

  for (let i = 0; i < rows.length; i++) {
    table.appendChild(rows[i]);
  }

  table.currSortCol = col;
}

});
