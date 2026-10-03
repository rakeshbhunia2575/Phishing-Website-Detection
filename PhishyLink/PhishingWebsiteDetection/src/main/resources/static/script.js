// Same-origin by default (files served from Spring Boot's static folder).
// If you open index.html from elsewhere, use "http://localhost:8080/api/predict" and enable CORS in Spring.
const API_URL = "/api/predict";

const $ = (id) => document.getElementById(id);
const form = $("form"), input = $("url"), btn = $("go"), errorBox = $("error");

async function api(options) {
  const res = await fetch(API_URL, options);
  if (!res.ok) {
    let text = "";
    try { text = (await res.text()).trim(); } catch (_) {}
    const plain = text && !text.startsWith("{") && !text.startsWith("<") && text.length < 200;
    throw new Error(plain ? text : "Something went wrong on the server (" + res.status + ").");
  }
  return res.json();
}

const isBad = (label) => /phish/i.test(label || "");

function clean(value) {
  if (Array.isArray(value)) value = value.join(" ");
  return typeof value === "string" && value.trim() ? value.trim() : "";
}

function messageColor(msg) {
  const m = (msg || "").toLowerCase();
  if (m.includes("good to go")) return "green";
  if (m.includes("could be malicious")) return "orange";
  return "red";
}

function showError(text) {
  errorBox.textContent = text;
  errorBox.hidden = !text;
}

function showResult(d) {
  $("label").textContent = d.label || "Unknown";
  $("verdict").className = "verdict " + (isBad(d.label) ? "bad" : "good");
  $("r-url").textContent = d.url || "";

  const reason = clean(d.reason ?? d.reasons), notes = clean(d.notes);
  $("r-reason").textContent = reason;
  $("reason-row").hidden = !reason;
  $("r-notes").textContent = notes;
  $("notes-row").hidden = !notes;

  const msg = $("message");
  msg.textContent = d.message || "";
  msg.className = "message " + messageColor(d.message);
  msg.hidden = !d.message;

  const box = $("result");
  box.hidden = false;
  box.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function renderHistory(items) {
  $("hist-count").textContent = Array.isArray(items) ? items.length : 0;
  const list = $("history");
  list.replaceChildren();
  if (!Array.isArray(items) || !items.length) {
    const p = document.createElement("p");
    p.className = "empty";
    p.textContent = "No links checked yet. Paste one above to get started.";
    list.append(p);
    return;
  }
  for (const it of items) {
    const row = document.createElement("div");
    row.className = "row";
    row.title = it.url || "";

    const u = document.createElement("span");
    u.className = "h-url";
    u.textContent = it.url || "";

    const chip = document.createElement("span");
    chip.className = "chip " + (isBad(it.label) ? "bad" : "good");
    chip.textContent = it.label || "Unknown";

    const c = document.createElement("span");
    c.className = "h-conf";
    const n = Number(it.confidence);
    c.textContent = isNaN(n) ? "" : (n <= 1 ? n * 100 : n).toFixed(1) + "%";

    row.append(u, chip, c);
    row.addEventListener("click", () => { input.value = it.url || ""; input.focus(); });
    list.append(row);
  }
}

async function loadHistory() {
  try { renderHistory(await api()); }
  catch (e) { renderHistory([]); }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = input.value.trim();
  if (!url) { showError("Enter a link to check."); input.focus(); return; }

  showError("");
  btn.disabled = true;
  btn.classList.add("busy");
  btn.textContent = "Checking";
  try {
    const data = await api({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urlReq: url })
    });
    showResult(data);
    loadHistory();
  } catch (err) {
    showError(err.message || "Could not reach the PhishyLink server. Check that it is running.");
  } finally {
    btn.disabled = false;
    btn.classList.remove("busy");
    btn.textContent = "Check link";
  }
});

loadHistory();

// History dropdown
const toggle = $("hist-toggle"), panel = $("hist-panel");
toggle.addEventListener("click", () => {
  const open = toggle.getAttribute("aria-expanded") === "true";
  toggle.setAttribute("aria-expanded", String(!open));
  panel.hidden = open;
});

$("year").textContent = new Date().getFullYear();
