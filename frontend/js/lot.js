/* ==========================================================================
   PYAAZSURE - Lot Registration JavaScript
   ========================================================================== */

document.addEventListener("DOMContentLoaded", async () => {
  // Set default date to today YYYY-MM-DD
  const dateInput = document.getElementById("date");
  if (dateInput) {
    const today = new Date().toISOString().split("T")[0];
    dateInput.value = today;
  }

  // Pre-fetch lot count to display expected Lot ID
  try {
    const lots = await apiFetch("/api/lots");
    const nextNum = (lots.length || 0) + 1;
    const formattedNum = String(nextNum).padStart(5, '0');
    const previewEl = document.getElementById("preview-lot-id");
    if (previewEl) {
      previewEl.textContent = `ONN-2026-${formattedNum}`;
    }
  } catch (err) {
    console.error("Error fetching preview lot count:", err);
  }

  // Form submission handler
  const form = document.getElementById("register-lot-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      
      const submitBtn = document.getElementById("btn-submit");
      submitBtn.disabled = true;
      submitBtn.textContent = "Registering Lot...";

      const centre_name = document.getElementById("centre_name").value.trim();
      const date = document.getElementById("date").value;
      const sample_size_expected = parseInt(document.getElementById("sample_size_expected").value, 10);

      try {
        const result = await apiFetch("/api/lots", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            centre_name: centre_name,
            date: date,
            sample_size_expected: sample_size_expected
          })
        });

        showNotification(`Lot ${result.lot_id} registered successfully!`, "success");

        // Redirect to Image Upload & Assessment page for this lot
        setTimeout(() => {
          window.location.href = `upload.html?lot_id=${result.lot_id}`;
        }, 800);

      } catch (err) {
        showNotification(`Failed to register lot: ${err.message}`, "error");
        submitBtn.disabled = false;
        submitBtn.textContent = "Create Lot & Upload Images →";
      }
    });
  }
});
