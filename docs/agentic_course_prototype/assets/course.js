const progressBar = document.querySelector("[data-progress]");

function updateProgress() {
  if (!progressBar) return;
  const doc = document.documentElement;
  const max = doc.scrollHeight - doc.clientHeight;
  const pct = max <= 0 ? 0 : (doc.scrollTop / max) * 100;
  progressBar.style.width = `${Math.min(100, Math.max(0, pct))}%`;
}

window.addEventListener("scroll", updateProgress, { passive: true });
window.addEventListener("resize", updateProgress);
updateProgress();

document.querySelectorAll("[data-check]").forEach((box) => {
  const key = `jobagent-course:${location.pathname}:${box.getAttribute("data-check")}`;
  box.checked = localStorage.getItem(key) === "1";
  box.addEventListener("change", () => {
    localStorage.setItem(key, box.checked ? "1" : "0");
  });
});
