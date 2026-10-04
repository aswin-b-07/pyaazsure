/* ==========================================================================
   PYAAZSURE - Shared JavaScript Utilities
   ========================================================================== */

const API_BASE = ""; // Relative path to API

/**
 * Universal API fetch helper
 */
async function apiFetch(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server returned HTTP ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`[API Error] ${endpoint}:`, err);
    throw err;
  }
}

/**
 * Renders status badge HTML string
 */
function renderStatusBadge(statusStr) {
  if (statusStr === "AI Assessment Complete") {
    return `<span class="badge badge-complete">✓ AI Complete</span>`;
  } else if (statusStr === "Needs Human Review" || statusStr.includes("Needs Human")) {
    return `<span class="badge badge-review">⚠️ Needs Review</span>`;
  } else if (statusStr === "Images Uploaded") {
    return `<span class="badge badge-registered" style="background:#e1bee7; color:#4a148c;">📷 Images Added</span>`;
  } else {
    return `<span class="badge badge-registered">📝 Registered</span>`;
  }
}

/**
 * Toast / Alert Notification
 */
function showNotification(message, type = "info") {
  const existing = document.getElementById("toast-notification");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.id = "toast-notification";
  toast.style.position = "fixed";
  toast.style.bottom = "20px";
  toast.style.right = "20px";
  toast.style.padding = "12px 20px";
  toast.style.borderRadius = "8px";
  toast.style.color = "#ffffff";
  toast.style.fontWeight = "600";
  toast.style.fontSize = "0.9rem";
  toast.style.zIndex = "9999";
  toast.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
  toast.style.transition = "all 0.3s ease";

  if (type === "success") {
    toast.style.background = "#15803d";
  } else if (type === "error") {
    toast.style.background = "#b91c1c";
  } else {
    toast.style.background = "#7b1fa2";
  }

  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Highlight current navbar link
document.addEventListener("DOMContentLoaded", () => {
  const currentPath = window.location.pathname;
  const links = document.querySelectorAll(".nav-links a");
  links.forEach(link => {
    const href = link.getAttribute("href");
    if (currentPath.endsWith(href) || (currentPath === "/" && href === "index.html")) {
      link.classList.add("active");
    }
  });
});
