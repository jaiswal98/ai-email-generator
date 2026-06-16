const state = {
  token: localStorage.getItem("token"),
  user: JSON.parse(localStorage.getItem("user") || "null"),
  latestEmail: null,
};

const $ = (id) => document.getElementById(id);

function showToast(message) {
  const toast = $("toast");
  toast.textContent = message;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

function setLoading(button, isLoading, text = "Loading...") {
  if (!button) return;
  if (isLoading) {
    button.dataset.originalText = button.textContent;
    button.textContent = text;
    button.disabled = true;
  } else {
    button.textContent = button.dataset.originalText || button.textContent;
    button.disabled = false;
  }
}

async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(path, { ...options, headers });

  if (response.status === 204) return null;

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong");
  }
  return data;
}

function updateUI() {
  const loggedIn = Boolean(state.token && state.user);
  $("authSection").classList.toggle("hidden", loggedIn);
  $("generatorSection").classList.toggle("hidden", !loggedIn);
  $("historySection").classList.toggle("hidden", !loggedIn);
  $("logoutBtn").classList.toggle("hidden", !loggedIn);
  $("authStatus").textContent = loggedIn ? `Logged in as ${state.user.name}` : "Not logged in";

  if (loggedIn) loadHistory();
}

function saveSession(data) {
  state.token = data.access_token;
  state.user = data.user;
  localStorage.setItem("token", state.token);
  localStorage.setItem("user", JSON.stringify(state.user));
  updateUI();
}

$("registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.target.querySelector("button");
  setLoading(button, true, "Creating...");
  try {
    const data = await api("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({
        name: $("regName").value,
        email: $("regEmail").value,
        password: $("regPassword").value,
      }),
    });
    saveSession(data);
    showToast("Account created successfully");
  } catch (error) {
    showToast(error.message);
  } finally {
    setLoading(button, false);
  }
});

$("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.target.querySelector("button");
  setLoading(button, true, "Logging in...");
  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: $("loginEmail").value,
        password: $("loginPassword").value,
      }),
    });
    saveSession(data);
    showToast("Logged in successfully");
  } catch (error) {
    showToast(error.message);
  } finally {
    setLoading(button, false);
  }
});

$("logoutBtn").addEventListener("click", () => {
  state.token = null;
  state.user = null;
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  updateUI();
  showToast("Logged out");
});

$("emailForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = $("generateBtn");
  setLoading(button, true, "Generating...");

  try {
    const data = await api("/api/emails/generate", {
      method: "POST",
      body: JSON.stringify({
        purpose: $("purpose").value,
        recipient_type: $("recipientType").value,
        tone: $("tone").value,
        key_points: $("keyPoints").value,
        language: $("language").value,
        length: $("length").value,
        include_subject: true,
        include_call_to_action: true,
      }),
    });

    state.latestEmail = data;
    $("score").textContent = `${data.score}/100`;
    $("subject").textContent = data.subject;
    $("body").textContent = data.body;
    $("cta").textContent = data.call_to_action || "";
    $("tips").innerHTML = (data.improvement_tips || [])
      .map((tip) => `<li>${escapeHtml(tip)}</li>`)
      .join("");
    showToast("Email generated and saved");
    loadHistory();
  } catch (error) {
    showToast(error.message);
  } finally {
    setLoading(button, false);
  }
});

$("copyBtn").addEventListener("click", async () => {
  if (!state.latestEmail) {
    showToast("Generate an email first");
    return;
  }
  const text = `Subject: ${state.latestEmail.subject}\n\n${state.latestEmail.body}`;
  await navigator.clipboard.writeText(text);
  showToast("Copied to clipboard");
});

$("refreshHistoryBtn").addEventListener("click", loadHistory);

async function loadHistory() {
  if (!state.token) return;
  try {
    const items = await api("/api/emails/history");
    const list = $("historyList");
    if (!items.length) {
      list.innerHTML = "<p>No emails generated yet.</p>";
      return;
    }

    list.innerHTML = items
      .map(
        (item) => `
        <article class="history-item">
          <div class="card-head">
            <h3>${escapeHtml(item.subject)}</h3>
            <button class="ghost" onclick="deleteEmail(${item.id})">Delete</button>
          </div>
          <p class="history-meta">${escapeHtml(item.tone)} · ${escapeHtml(item.recipient_type)} · Score ${item.score}/100 · ${new Date(item.created_at).toLocaleString()}</p>
          <p>${escapeHtml(item.body.slice(0, 240))}${item.body.length > 240 ? "..." : ""}</p>
        </article>`
      )
      .join("");
  } catch (error) {
    showToast(error.message);
  }
}

async function deleteEmail(id) {
  try {
    await api(`/api/emails/${id}`, { method: "DELETE" });
    showToast("Email deleted");
    loadHistory();
  } catch (error) {
    showToast(error.message);
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

updateUI();
