// Logs JS errors, resource load errors (like <img src=...> 404), and promise rejections

// JS runtime errors
window.addEventListener("error", (e) => {
  // Resource load errors (IMG, LINK, SCRIPT) arrive with e.target set
  if (e.target && (e.target.tagName === "IMG" || e.target.tagName === "LINK" || e.target.tagName === "SCRIPT")) {
    const el = e.target;
    const kind = el.tagName.toLowerCase();
    const src = el.src || el.href;
    console.error(`[ASSET-LOAD-ERROR] <${kind}> failed to load:`, src);
  } else {
    console.error("[JS-ERROR]", e.error || e.message, e);
  }
}, true);

// Unhandled promise rejections
window.addEventListener("unhandledrejection", (e) => {
  console.error("[UNHANDLED-REJECTION]", e.reason);
});
