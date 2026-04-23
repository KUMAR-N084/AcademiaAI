const $ = sel => document.querySelector(sel);
let currentMode = "explain";
let lastQuestion = "";
let lastAnswer = "";
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || "";

async function apiFetch(url, options = {}) {
  const headers = new Headers(options.headers || {});
  const method = (options.method || "GET").toUpperCase();

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }
  if (!["GET", "HEAD", "OPTIONS"].includes(method) && csrfToken) {
    headers.set("X-CSRFToken", csrfToken);
  }

  const response = await fetch(url, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (response.status === 401) {
    const message = typeof payload === "object" && payload.error
      ? payload.error
      : "Your session has expired. Please log in again.";
    alert(message);
    window.location.href = "/login";
    throw new Error(message);
  }

  if (!response.ok) {
    const message = typeof payload === "object" && payload.error
      ? payload.error
      : "Request failed.";
    throw new Error(message);
  }

  return payload;
}

async function apiFetchBlob(url, options = {}) {
  const headers = new Headers(options.headers || {});
  const method = (options.method || "GET").toUpperCase();

  if (!["GET", "HEAD", "OPTIONS"].includes(method) && csrfToken) {
    headers.set("X-CSRFToken", csrfToken);
  }

  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    let message = "Your session has expired. Please log in again.";
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const payload = await response.json();
      message = payload.error || message;
    }
    alert(message);
    window.location.href = "/login";
    throw new Error(message);
  }

  if (!response.ok) {
    let message = "Request failed.";
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const payload = await response.json();
      message = payload.error || message;
    }
    throw new Error(message);
  }

  return response.blob();
}

// THEME
const theme = localStorage.getItem("theme") || "light";
document.documentElement.setAttribute("data-theme", theme);
$("#themeToggle").textContent = theme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode";

$("#themeToggle").addEventListener("click", () => {
  const cur = document.documentElement.getAttribute("data-theme");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
  $("#themeToggle").textContent = next === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode";
});

// MODE
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentMode = btn.dataset.mode;
  });
});

function showLoader(show) { $("#loader").classList.toggle("hidden", !show); }
function hideAll() { ["#answer","#flashcards","#vizSection","#videoSection"].forEach(s => $(s).classList.add("hidden")); }

// ASK
$("#askBtn").addEventListener("click", async () => {
  const q = $("#question").value.trim();
  if (!q) return alert("Please type a question.");
  hideAll(); showLoader(true);
  try {
    const data = await apiFetch("/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, mode: currentMode })
    });
    showLoader(false);

    lastQuestion = q;
    lastAnswer = data.answer;
    $("#pdfBtn").disabled = false;

    if (currentMode === "flashcards") renderFlashcards(data.answer);
    else {
      $("#answer").innerHTML = marked.parse(data.answer);
      $("#answer").classList.remove("hidden");
    }
  } catch (e) { showLoader(false); alert(e.message); }
});

function renderFlashcards(raw) {
  try {
    const clean = raw.replace(/```json|```/g, "").trim();
    const cards = JSON.parse(clean);
    const c = $("#flashcards"); c.innerHTML = "";
    cards.forEach(card => {
      const div = document.createElement("div");
      div.className = "card";
      div.innerHTML = `<div class="card-inner">
        <div class="card-front">${card.q}</div>
        <div class="card-back">${card.a}</div></div>`;
      div.addEventListener("click", () => div.classList.toggle("flipped"));
      c.appendChild(div);
    });
    c.classList.remove("hidden");
  } catch {
    $("#answer").textContent = raw;
    $("#answer").classList.remove("hidden");
  }
}

// VISUALIZE
$("#visualBtn").addEventListener("click", async () => {
  const q = $("#question").value.trim();
  if (!q) return alert("Enter a topic.");
  hideAll(); showLoader(true);
  try {
    const data = await apiFetch("/visualize", {
      method:"POST", headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ topic: q })
    });
    showLoader(false);

    const nodes = data.graph.nodes.map(n => ({
      id: n.id, label: n.label, shape: "box",
      color: { background:"#eef2ff", border:"#4f46e5" },
      font: { color:"#1f2937" }
    }));
    const edges = data.graph.edges.map(e => ({
      from: e.from, to: e.to, label: e.label || "",
      arrows:"to", color:{ color:"#9ca3af" }, font:{ size:10 }
    }));
    new vis.Network($("#network"),
      { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) },
      { physics:{ stabilization:true } }
    );
    $("#chartImg").src = "data:image/png;base64," + data.chart;
    $("#vizSection").classList.remove("hidden");
  } catch(e) { showLoader(false); alert(e.message); }
});

// VIDEO
$("#videoBtn").addEventListener("click", async () => {
  const q = $("#question").value.trim();
  if (!q) return alert("Enter a topic.");
  hideAll(); showLoader(true);
  try {
    const data = await apiFetch("/video", {
      method:"POST", headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ topic: q })
    });
    showLoader(false);
    $("#videoFrame").src = data.embed;
    $("#videoSection").classList.remove("hidden");
  } catch(e) { showLoader(false); alert(e.message); }
});

// PDF EXPORT
$("#pdfBtn").addEventListener("click", async () => {
  if (!lastAnswer) return;
  try {
    const blob = await apiFetchBlob("/export/pdf", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: lastQuestion, answer: lastAnswer })
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "academic_answer.pdf"; a.click();
    URL.revokeObjectURL(url);
  } catch(e) { alert(e.message); }
});

// HISTORY
$("#historyBtn").addEventListener("click", async () => {
  $("#historyDrawer").classList.remove("hidden");
  const data = await apiFetch("/history");
  const list = $("#historyList"); list.innerHTML = "";
  if (!data.history.length) { list.innerHTML = "<p class='muted small'>No history yet.</p>"; return; }
  data.history.forEach(h => {
    const div = document.createElement("div");
    div.className = "hist-item";
    div.innerHTML = `
      <span class="del" data-id="${h._id}">✖</span>
      <div class="q">${h.question.substring(0, 80)}${h.question.length > 80 ? "..." : ""}</div>
      <div class="meta">${h.mode} · ${new Date(h.created_at).toLocaleString()}</div>`;
    div.addEventListener("click", (e) => {
      if (e.target.classList.contains("del")) return;
      $("#question").value = h.question;
      lastQuestion = h.question; lastAnswer = h.answer;
      $("#pdfBtn").disabled = false;
      hideAll();
      $("#answer").innerHTML = marked.parse(h.answer);
      $("#answer").classList.remove("hidden");
      $("#historyDrawer").classList.add("hidden");
    });
    list.appendChild(div);
  });
  // delete handlers
  list.querySelectorAll(".del").forEach(x => {
    x.addEventListener("click", async (e) => {
      e.stopPropagation();
      const id = x.dataset.id;
      try {
        await apiFetch(`/history/${id}`, { method: "DELETE" });
        x.parentElement.remove();
        if (!list.children.length) {
          list.innerHTML = "<p class='muted small'>No history yet.</p>";
        }
      } catch (error) {
        alert(error.message);
      }
    });
  });
});

$("#closeDrawer").addEventListener("click", () => {
  $("#historyDrawer").classList.add("hidden");
});
