const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function businessGet(path) {
  const res = await fetch(`${API_BASE}/api/business${path}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function businessPost(path, body = {}) {
  const res = await fetch(`${API_BASE}/api/business${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
