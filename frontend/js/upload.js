/* ==========================================================================
   PYAAZSURE - Image Upload & AI Assessment Script
   ========================================================================== */

let selectedLotId = "";

document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const paramLotId = urlParams.get("lot_id");

  const lotSelect = document.getElementById("lot-select");

  // Load available lots into select dropdown
  try {
    const lots = await apiFetch("/api/lots");
    lotSelect.innerHTML = `<option value="">-- Select a Lot --</option>` + lots.map(lot => `
      <option value="${lot.lot_id}" ${paramLotId === lot.lot_id ? 'selected' : ''}>
        ${lot.lot_id} - ${lot.centre_name} (${lot.date})
      </option>
    `).join("");

    if (paramLotId) {
      lotSelect.value = paramLotId;
      loadLotDetails(paramLotId);
    }
  } catch (err) {
    showNotification("Failed to load lots: " + err.message, "error");
  }

  lotSelect.addEventListener("change", (e) => {
    const val = e.target.value;
    if (val) {
      loadLotDetails(val);
    } else {
      resetLotDetails();
    }
  });

  // Dropzone drag & drop handlers
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");

  if (dropzone && fileInput) {
    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("active");
    });

    dropzone.addEventListener("dragleave", () => {
      dropzone.classList.remove("active");
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("active");
      if (e.dataTransfer.files.length > 0) {
        handleFileUpload(e.dataTransfer.files);
      }
    });

    fileInput.addEventListener("change", () => {
      if (fileInput.files.length > 0) {
        handleFileUpload(fileInput.files);
      }
    });
  }

  // AI Execution Button Listener
  const btnRunAi = document.getElementById("btn-run-ai");
  if (btnRunAi) {
    btnRunAi.addEventListener("click", async () => {
      if (!selectedLotId) {
        showNotification("Please select a lot first.", "error");
        return;
      }

      btnRunAi.disabled = true;
      btnRunAi.innerHTML = `⏳ Running Mock AI Inference & Grading Engine...`;

      try {
        const report = await apiFetch(`/api/lots/${selectedLotId}/analyze`, {
          method: "POST"
        });

        showNotification("AI Assessment Complete! Generating report...", "success");

        setTimeout(() => {
          window.location.href = `report.html?lot_id=${selectedLotId}`;
        }, 1000);

      } catch (err) {
        showNotification("Analysis failed: " + err.message, "error");
        btnRunAi.disabled = false;
        btnRunAi.innerHTML = `⚡ Run Mock AI & Generate Report`;
      }
    });
  }
});

async function loadLotDetails(lotId) {
  selectedLotId = lotId;
  const metaBox = document.getElementById("lot-metadata-box");
  const btnRunAi = document.getElementById("btn-run-ai");

  try {
    const lot = await apiFetch(`/api/lots/${lotId}`);
    document.getElementById("meta-centre").textContent = lot.centre_name;
    document.getElementById("meta-date").textContent = lot.date;
    document.getElementById("meta-target").textContent = lot.sample_size_expected;
    document.getElementById("meta-status").innerHTML = renderStatusBadge(lot.status);
    metaBox.style.display = "block";

    // Load existing uploaded images
    loadLotImages(lotId);

  } catch (err) {
    showNotification("Error loading lot metadata: " + err.message, "error");
  }
}

function resetLotDetails() {
  selectedLotId = "";
  document.getElementById("lot-metadata-box").style.display = "none";
  document.getElementById("image-preview-grid").innerHTML = "";
  document.getElementById("img-count-badge").textContent = "0";
  document.getElementById("btn-run-ai").disabled = true;
}

async function loadLotImages(lotId) {
  const grid = document.getElementById("image-preview-grid");
  const badge = document.getElementById("img-count-badge");
  const statusMsg = document.getElementById("img-status-msg");
  const btnRunAi = document.getElementById("btn-run-ai");

  try {
    const images = await apiFetch(`/api/lots/${lotId}/images`);
    badge.textContent = images.length;

    if (images.length === 0) {
      grid.innerHTML = "";
      statusMsg.textContent = "No images uploaded for this lot yet.";
      btnRunAi.disabled = true;
      return;
    }

    statusMsg.textContent = `${images.length} image(s) ready for AI analysis.`;
    btnRunAi.disabled = false;

    grid.innerHTML = images.map((img, idx) => `
      <div class="image-card">
        <img src="${img.file_path}" alt="Sample ${idx+1}" onerror="this.src='https://via.placeholder.com/150/7b1fa2/ffffff?text=Onion+Sample'">
        <div class="image-card-body">
          <div style="font-weight:600; font-size:0.75rem;">Sample #${idx+1}</div>
          <div style="color:var(--text-muted); font-size:0.7rem;">${img.predicted_class || 'Pending'}</div>
        </div>
      </div>
    `).join("");

  } catch (err) {
    console.error("Error loading images:", err);
  }
}

async function handleFileUpload(files) {
  if (!selectedLotId) {
    showNotification("Please select a target lot before uploading images.", "error");
    return;
  }

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  showNotification(`Uploading ${files.length} image(s)...`, "info");

  try {
    await fetch(`/api/lots/${selectedLotId}/images`, {
      method: "POST",
      body: formData
    });

    showNotification("Images uploaded successfully!", "success");
    loadLotImages(selectedLotId);

  } catch (err) {
    showNotification("Upload failed: " + err.message, "error");
  }
}

async function generateBatch(count) {
  if (!selectedLotId) {
    showNotification("Please select a target lot before generating sample batch.", "error");
    return;
  }

  showNotification(`Generating batch of ${count} synthetic sample onion images...`, "info");

  try {
    await apiFetch(`/api/lots/${selectedLotId}/generate-sample-images?count=${count}`, {
      method: "POST"
    });

    showNotification(`Generated ${count} sample images successfully!`, "success");
    loadLotImages(selectedLotId);

  } catch (err) {
    showNotification("Failed to generate sample batch: " + err.message, "error");
  }
}
