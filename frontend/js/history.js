/* ==========================================================================
   PYAAZSURE - Lot History & Archive Script
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  loadLotHistory();

  const searchInput = document.getElementById("search-input");
  const filterStatus = document.getElementById("filter-status");

  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        loadLotHistory();
      }, 300);
    });
  }

  if (filterStatus) {
    filterStatus.addEventListener("change", () => {
      loadLotHistory();
    });
  }
});

async function loadLotHistory() {
  const tbody = document.getElementById("history-tbody");
  const searchVal = document.getElementById("search-input") ? document.getElementById("search-input").value.trim() : "";
  const statusVal = document.getElementById("filter-status") ? document.getElementById("filter-status").value : "";

  try {
    // Fetch lots and reports
    let queryParams = [];
    if (searchVal) queryParams.push(`search=${encodeURIComponent(searchVal)}`);
    if (statusVal) queryParams.push(`status_filter=${encodeURIComponent(statusVal)}`);
    
    const queryString = queryParams.length > 0 ? `?${queryParams.join("&")}` : "";
    const lots = await apiFetch(`/api/lots${queryString}`);
    const reports = await apiFetch(`/api/reports`);

    // Map reports by lot_id for fast lookup
    const reportMap = {};
    reports.forEach(r => {
      reportMap[r.lot_id] = r;
    });

    if (lots.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="9" style="text-align:center; padding:2.5rem; color:var(--text-muted);">
            No lots found matching your filter criteria.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = lots.map(lot => {
      const rep = reportMap[lot.lot_id];
      const isAssessed = lot.status.includes("Complete") || lot.status.includes("Review");

      const gradeA = rep ? `${rep.grade_a_pct}%` : "N/A";
      const urs = rep ? `${rep.urs_pct}%` : "N/A";
      const defective = rep ? `${rep.defective_pct}%` : "N/A";
      const avgConf = rep ? `${rep.avg_confidence}%` : "N/A";

      return `
        <tr>
          <td><strong style="color:var(--primary);">${lot.lot_id}</strong></td>
          <td>${lot.centre_name}</td>
          <td>${lot.date}</td>
          <td><span style="color:#15803d; font-weight:700;">${gradeA}</span></td>
          <td><span style="color:#0369a1; font-weight:600;">${urs}</span></td>
          <td><span style="color:#b91c1c; font-weight:600;">${defective}</span></td>
          <td><strong>${avgConf}</strong></td>
          <td>${renderStatusBadge(lot.status)}</td>
          <td>
            <a href="${isAssessed ? 'report.html?lot_id=' + lot.lot_id : 'upload.html?lot_id=' + lot.lot_id}" class="btn btn-sm ${isAssessed ? 'btn-primary' : 'btn-secondary'}">
              ${isAssessed ? 'View Report' : 'Assess Lot'}
            </a>
          </td>
        </tr>
      `;
    }).join("");

  } catch (err) {
    showNotification("Failed to load lot history: " + err.message, "error");
  }
}
