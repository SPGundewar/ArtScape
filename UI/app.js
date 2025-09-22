const AUTH = "http://localhost:8001";
const ART = "http://localhost:8002";
const ORD = "http://localhost:8003";

function _saveToken(t){
  localStorage.setItem("token", t);
  document.getElementById("token_status").innerText = t ? "Authenticated" : "Not authenticated";
}

function _getToken(){
  return localStorage.getItem("token");
}

async function register(){
  const u = document.getElementById("reg_user").value;
  const p = document.getElementById("reg_pass").value;
  const r = document.getElementById("reg_role").value;
  const res = await fetch(`${AUTH}/auth/register`, {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ username:u, password:p, role:r })
  });
  alert(await res.text());
}

async function login(){
  const u = document.getElementById("login_user").value;
  const p = document.getElementById("login_pass").value;
  const form = new URLSearchParams();
  form.append("username", u);
  form.append("password", p);
  const res = await fetch(`${AUTH}/auth/token`, {
    method:"POST",
    body: form
  });
  const j = await res.json();
  if(j.access_token){
    _saveToken(j.access_token);
    alert("Logged in");
  } else {
    alert(JSON.stringify(j));
  }
}

async function createArtwork(){
  const t = _getToken();
  if(!t){ alert("login first"); return; }
  const title = document.getElementById("art_title").value;
  const desc = document.getElementById("art_desc").value;
  const price = parseFloat(document.getElementById("art_price").value || 0);
  const res = await fetch(`${ART}/artworks`, {
    method:"POST",
    headers: {"Content-Type":"application/json", "Authorization": "Bearer " + t},
    body: JSON.stringify({title, description:desc, price})
  });
  const j = await res.json();
  if(res.ok) {
    alert("Created: " + j.title);
    listArtworks();
  } else {
    alert(JSON.stringify(j));
  }
}

async function listArtworks(){
  const res = await fetch(`${ART}/artworks`);
  const arr = await res.json();
  const el = document.getElementById("art_list");
  el.innerHTML = "";
  arr.forEach(a=>{
    const node = document.createElement("div");
    node.className = "art";
    node.innerHTML = `<b>${a.id} - ${a.title}</b> (owner: ${a.owner}) — $${a.price} — sold: ${a.is_sold}<br>${a.description || ""}`;
    el.appendChild(node);
  });
}

async function purchase(){
  const t = _getToken();
  if(!t){ alert("login first"); return; }
  const art_id = parseInt(document.getElementById("buy_art_id").value);
  const res = await fetch(`${ORD}/orders`, {
    method:"POST",
    headers: {"Content-Type":"application/json", "Authorization": "Bearer " + t},
    body: JSON.stringify({ art_id })
  });
  const j = await res.json();
  if(res.ok) {
    alert("Order created id: " + j.id);
    listArtworks();
  } else {
    alert(JSON.stringify(j));
  }
}

document.getElementById("token_status").innerText = _getToken() ? "Authenticated" : "Not authenticated";
