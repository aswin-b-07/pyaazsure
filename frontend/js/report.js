/* ==========================================================================
   PYAAZSURE - Digital Quality Report JavaScript
   ========================================================================== */

let gradeChartInstance = null;
let defectChartInstance = null;

document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const lotId = urlParams.get("lot_id");

  const selectCard = document.getElementById("select-report-card");
  const reportSelect = document.getElementById("report-lot-select");
  const btnLoadReport = document.getElementById("btn-load-report");

  if (lotId) {
    loadReport(lotId);
  } else {
    // If no lot_id in URL, display lot selector dropdown
    selectCard.style.display = "block";
    try {
      const reports = await apiFetch("/api/reports");
      if (reports.length > 0) {
        reportSelect.innerHTML = `<option value="">-- Choose Assessed Lot --</option>` + reports.map(r => `
          <option value="${r.lot_id}">${r.lot_id} - ${r.centre_name || 'Mandi'} (Grade A: ${r.grade_a_pct}%)</option>
        `).join("");
        
        // Auto-load first report if available
        loadReport(reports[0].lot_id);
      } else {
        reportSelect.innerHTML = `<option value="">No assessed reports found</option>`;
      }
    } catch (err) {
      console.error("Error loading reports list:", err);
    }
  }

  if (btnLoadReport) {
    btnLoadReport.addEventListener("click", () => {
      const selected = reportSelect.value;
      if (selected) {
        window.location.href = `report.html?lot_id=${selected}`;
      }
    });
  }
});

async function loadReport(lotId) {
  const container = document.getElementById("report-container");

  try {
    const report = await apiFetch(`/api/lots/${lotId}/report`);
    
    // Header & Meta
    document.getElementById("rep-lot-id").textContent = report.lot_id;
    document.getElementById("rep-centre-name").textContent = report.centre_name || "N/A";
    document.getElementById("rep-date").textContent = report.date || "N/A";
    document.getElementById("rep-status-badge").innerHTML = renderStatusBadge(report.status);

    // Key Stats
    document.getElementById("rep-grade-a").textContent = `${report.grade_a_pct}%`;
    document.getElementById("rep-urs").textContent = `${report.urs_pct}%`;
    document.getElementById("rep-defective").textContent = `${report.defective_pct}%`;
    document.getElementById("rep-avg-conf").textContent = `${report.avg_confidence}%`;

    // Explanation
    document.getElementById("rep-explanation").textContent = report.explanation;

    // Counts & Breakdown Table
    const bd = report.defect_breakdown || {};
    const total = report.total_analyzed || 1;

    document.getElementById("count-healthy").textContent = bd.healthy;
    document.getElementById("pct-healthy").textContent = `${((bd.healthy / total) * 100).toFixed(1)}%`;

    document.getElementById("count-undersized").textContent = bd.undersized;
    document.getElementById("pct-undersized").textContent = `${((bd.undersized / total) * 100).toFixed(1)}%`;

    document.getElementById("count-damaged").textContent = bd.damaged;
    document.getElementById("pct-damaged").textContent = `${((bd.damaged / total) * 100).toFixed(1)}%`;

    document.getElementById("count-rotten").textContent = bd.rotten;
    document.getElementById("pct-rotten").textContent = `${((bd.rotten / total) * 100).toFixed(1)}%`;

    document.getElementById("count-sprouted").textContent = bd.sprouted;
    document.getElementById("pct-sprouted").textContent = `${((bd.sprouted / total) * 100).toFixed(1)}%`;

    document.getElementById("count-total").textContent = total;

    // Render Charts
    renderCharts(report);

    // Load Image Gallery
    loadGalleryImages(lotId);

    container.style.display = "block";

  } catch (err) {
    showNotification("Failed to load report: " + err.message, "error");
  }
}

function renderCharts(report) {
  if (typeof Chart === "undefined") return;

  // Grade Distribution Donut Chart
  const ctxGrade = document.getElementById("gradeChart").getContext("2d");
  if (gradeChartInstance) gradeChartInstance.destroy();

  gradeChartInstance = new Chart(ctxGrade, {
    type: "doughnut",
    data: {
      labels: ["Grade A (Healthy)", "URS (Undersized)", "Defective"],
      datasets: [{
        data: [report.grade_a_pct, report.urs_pct, report.defective_pct],
        backgroundColor: ["#16a34a", "#0284c7", "#dc2626"],
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" }
      }
    }
  });

  // Defect Classification Bar Chart
  const bd = report.defect_breakdown || {};
  const ctxDefect = document.getElementById("defectChart").getContext("2d");
  if (defectChartInstance) defectChartInstance.destroy();

  defectChartInstance = new Chart(ctxDefect, {
    type: "bar",
    data: {
      labels: ["Healthy", "Undersized", "Damaged", "Rotten", "Sprouted"],
      datasets: [{
        label: "Sample Count",
        data: [bd.healthy, bd.undersized, bd.damaged, bd.rotten, bd.sprouted],
        backgroundColor: ["#16a34a", "#0284c7", "#ea580c", "#dc2626", "#854d0e"],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

async function loadGalleryImages(lotId) {
  const grid = document.getElementById("report-images-grid");
  try {
    const images = await apiFetch(`/api/lots/${lotId}/images`);
    if (images.length === 0) {
      grid.innerHTML = `<div style="color:var(--text-muted);">No images found.</div>`;
      return;
    }

    grid.innerHTML = images.map(img => {
      let badgeClass = "badge-complete";
      if (img.predicted_class !== "Healthy") {
        badgeClass = img.predicted_class === "Undersized" ? "badge-registered" : "badge-review";
      }

      return `
        <div class="image-card">
          <img src="${img.file_path}" alt="${img.predicted_class}" onerror="this.src='https://via.placeholder.com/150/7b1fa2/ffffff?text=Onion+Sample'">
          <div class="image-card-body">
            <div style="font-weight:700; font-size:0.8rem; margin-bottom:0.2rem;">
              ${img.predicted_class || 'Pending'}
            </div>
            <div style="font-size:0.75rem; color:var(--text-muted);">
              Conf: ${img.confidence ? img.confidence + '%' : 'N/A'}
            </div>
          </div>
        </div>
      `;
    }).join("");

  } catch (err) {
    console.error("Error loading report images gallery:", err);
  }
}
