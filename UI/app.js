// --- Service URLs ---
const AUTH_URL = "http://localhost:8001";
const ARTWORK_URL = "http://localhost:8002";
const ORDERS_URL = "http://localhost:8003";

// --- Token helpers ---
const tokenKey = "authToken";

function saveToken(token) {
  if (token) localStorage.setItem(tokenKey, token);
  else localStorage.removeItem(tokenKey);

  document.getElementById("token_status").innerText =
    token ? "✅ Authenticated" : "❌ Not authenticated";
}

function getToken() {
  return localStorage.getItem(tokenKey);
}

function authHeaders() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}`, "Content-Type": "application/json" } : {};
}

// --- Auth ---
async function register() {
  const u = document.getElementById("reg_user").value.trim();
  const p = document.getElementById("reg_pass").value.trim();
  const r = document.getElementById("reg_role").value;

  const res = await fetch(`${AUTH_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: u, password: p, role: r }),
  });

  const msg = await res.text();
  alert(res.ok ? "✅ Registered successfully!" : `⚠️ Failed: ${msg}`);
}

async function login() {
  const u = document.getElementById("login_user").value.trim();
  const p = document.getElementById("login_pass").value.trim();

  const form = new URLSearchParams();
  form.append("username", u);
  form.append("password", p);

  const res = await fetch(`${AUTH_URL}/auth/token`, {
    method: "POST",
    body: form,
  });

  const data = await res.json();
  if (res.ok && data.access_token) {
    saveToken(data.access_token);
    alert("✅ Logged in successfully");
    await refreshUser();
  } else {
    alert("⚠️ Login failed: " + JSON.stringify(data));
  }
}

async function logout() {
  saveToken(null);
  document.getElementById("artistSection").style.display = "none";
  document.getElementById("purchaseSection").style.display = "none";
  document.getElementById("ordersSection").style.display = "none";
  document.getElementById("logoutBtn").style.display = "none";
  document.getElementById("authSection").style.display = "block";
  listArtworks();
}

// --- User info ---
async function refreshUser() {
  const t = getToken();
  if (!t) return;

  try {
    const res = await fetch(`${AUTH_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${t}` },
    });
    if (!res.ok) throw new Error("Token invalid/expired");

    const user = await res.json();

    // Toggle UI by role
    document.getElementById("authSection").style.display = "none";
    document.getElementById("logoutBtn").style.display = "inline-block";
    document.getElementById("ordersSection").style.display = "block";

    if (user.role === "artist") {
      document.getElementById("artistSection").style.display = "block";
      document.getElementById("purchaseSection").style.display = "none";
    } else if (user.role === "user") {
      document.getElementById("purchaseSection").style.display = "block";
      document.getElementById("artistSection").style.display = "none";
    } else {
      document.getElementById("artistSection").style.display = "none";
      document.getElementById("purchaseSection").style.display = "none";
    }
  } catch (err) {
    console.warn("User check failed:", err);
    saveToken(null);
  }
}

// --- Artwork ---
async function createArtwork() {
  const title = document.getElementById("art_title").value.trim();
  const desc = document.getElementById("art_desc").value.trim();
  const price = parseFloat(document.getElementById("art_price").value || 0);

  const res = await fetch(`${ARTWORK_URL}/artworks`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ title, description: desc, price }),
  });

  const j = await res.json();
  if (res.ok) {
    alert(`🎉 Artwork created: ${j.title}`);
    listArtworks();
  } else {
    alert("⚠️ Failed: " + JSON.stringify(j));
  }
}

async function listArtworks() {
  const res = await fetch(`${ARTWORK_URL}/artworks`);
  const arr = await res.json();
  const el = document.getElementById("art_list");
  el.innerHTML = "";

  arr.forEach((a) => {
    const card = document.createElement("div");
    card.className = "art-card";
    card.innerHTML = `
      <h3>${a.title}</h3>
      <p>${a.description || "No description"}</p>
      <p><b>Owner:</b> ${a.owner}</p>
      <p><b>Price:</b> $${a.price}</p>
      <span class="status ${a.is_sold ? "sold" : "available"}">
        ${a.is_sold ? "❌ Sold" : "✅ Available"}
      </span>
      ${
        !a.is_sold && getToken()
          ? `<button onclick="buyArtwork(${a.id})">Buy</button>`
          : ""
      }
    `;
    el.appendChild(card);
  });
}

// --- Purchase ---
async function buyArtwork(artId) {
  const res = await fetch(`${ORDERS_URL}/orders`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ art_id: artId }),
  });

  const j = await res.json();
  if (res.ok) {
    alert(`🛒 Order created! ID: ${j.id}`);
    listArtworks();
    listOrders();
  } else {
    alert("⚠️ Failed: " + JSON.stringify(j));
  }
}

async function purchase() {
  const artId = parseInt(document.getElementById("buy_art_id").value);
  await buyArtwork(artId);
}

// --- Orders ---
async function listOrders() {
  const res = await fetch(`${ORDERS_URL}/orders`, {
    headers: authHeaders(),
  });

  const arr = await res.json();
  const el = document.getElementById("ordersList");
  el.innerHTML = "";

  if (!res.ok) {
    el.innerHTML = `<p>⚠️ Failed to fetch orders: ${JSON.stringify(arr)}</p>`;
    return;
  }

  if (arr.length === 0) {
    el.innerHTML = "<p>No orders found.</p>";
    return;
  }

  arr.forEach((o) => {
    const div = document.createElement("div");
    div.className = "art-card";
    div.innerHTML = `
      <p><b>Order ID:</b> ${o.id}</p>
      <p><b>Artwork ID:</b> ${o.art_id}</p>
      <p><b>Buyer:</b> ${o.buyer}</p>
      <p><b>Status:</b> ${o.status}</p>
    `;
    el.appendChild(div);
  });
}

// --- Init ---
document.getElementById("token_status").innerText = getToken()
  ? "✅ Authenticated"
  : "❌ Not authenticated";

(async () => {
  await refreshUser();
  listArtworks();
  if (getToken()) listOrders();
})();
