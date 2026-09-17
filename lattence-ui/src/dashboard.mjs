import { visualGrammar } from "./grammar.mjs";
import {
  filterRows,
  moveSelection,
  rowsForSection,
  sortRows,
  visibleRows,
} from "./dashboard-model.mjs";

const elements = {
  navigation: document.querySelector("#navigation"),
  filter: document.querySelector("#filter"),
  header: document.querySelector("#table-header"),
  body: document.querySelector("#table-body"),
  viewport: document.querySelector(".table-viewport"),
  detail: document.querySelector("#detail-content"),
  save: document.querySelector("#save-view"),
  copy: document.querySelector("#copy-json"),
  export: document.querySelector("#export-json"),
};

const state = {
  presentation: { graph: { nodes: [] }, findings: [], cross_layer_chains: [] },
  section: visualGrammar.navigation[0],
  query: "",
  sortField: "id",
  direction: "ascending",
  selected: 0,
};

function currentRows() {
  return sortRows(
    filterRows(rowsForSection(state.presentation, state.section), state.query),
    state.sortField,
    state.direction,
  );
}

function rowColumns(row) {
  return [row.type ?? row.severity ?? "CHAIN", row.id ?? row.name, row.status ?? "PASS"];
}

function renderNavigation() {
  elements.navigation.replaceChildren(
    ...visualGrammar.navigation.map((label) => {
      const button = document.createElement("button");
      button.className = "nav-item";
      button.textContent = label;
      button.setAttribute("aria-current", label === state.section ? "page" : "false");
      button.addEventListener("click", () => {
        state.section = label;
        state.selected = 0;
        render();
      });
      return button;
    }),
  );
}

function renderHeader() {
  const fields = ["type", "id", "status"];
  elements.header.replaceChildren(
    ...fields.map((field) => {
      const cell = document.createElement("th");
      const button = document.createElement("button");
      button.textContent = field.toUpperCase();
      button.addEventListener("click", () => {
        state.direction =
          state.sortField === field && state.direction === "ascending"
            ? "descending"
            : "ascending";
        state.sortField = field;
        render();
      });
      cell.append(button);
      return cell;
    }),
  );
}

function renderRows() {
  const rows = currentRows();
  const visible = visibleRows(
    rows,
    elements.viewport.scrollTop,
    elements.viewport.clientHeight || 640,
  );
  elements.body.replaceChildren(
    ...visible.rows.map((row, offset) => {
      const index = visible.start + offset;
      const tableRow = document.createElement("tr");
      tableRow.tabIndex = index === state.selected ? 0 : -1;
      tableRow.setAttribute("aria-selected", String(index === state.selected));
      for (const value of rowColumns(row)) {
        const cell = document.createElement("td");
        cell.textContent = String(value ?? "");
        tableRow.append(cell);
      }
      tableRow.addEventListener("click", () => {
        state.selected = index;
        renderRows();
      });
      return tableRow;
    }),
  );
  elements.detail.textContent = rows[state.selected]
    ? JSON.stringify(rows[state.selected], null, 2)
    : "No data. Run lattence scan .";
}

function render() {
  renderNavigation();
  renderHeader();
  renderRows();
}

elements.filter.addEventListener("input", (event) => {
  state.query = event.target.value;
  state.selected = 0;
  renderRows();
});
elements.viewport.addEventListener("scroll", renderRows);
document.addEventListener("keydown", (event) => {
  const movement = event.key === "ArrowDown" ? 1 : event.key === "ArrowUp" ? -1 : 0;
  if (!movement) return;
  event.preventDefault();
  state.selected = moveSelection(state.selected, movement, currentRows().length);
  renderRows();
});
elements.save.addEventListener("click", () => {
  localStorage.setItem("lattence.saved-view", JSON.stringify({ ...state }));
});
elements.copy.addEventListener("click", () => {
  navigator.clipboard.writeText(elements.detail.textContent);
});
elements.export.addEventListener("click", () => {
  const blob = new Blob([JSON.stringify(state.presentation, null, 2)], {
    type: "application/json",
  });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "lattence-presentation.json";
  link.click();
  URL.revokeObjectURL(link.href);
});

fetch("./presentation.json")
  .then((response) => (response.ok ? response.json() : Promise.reject(response)))
  .then((presentation) => {
    state.presentation = presentation;
    render();
  })
  .catch(render);
