const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const getToken = () => localStorage.getItem("token");
export const setToken = (t) => localStorage.setItem("token", t);
export const clearToken = () => localStorage.removeItem("token");

const FIELD_LABELS = { name: "Name", email: "Email", password: "Password" };

function formatDetail(detail) {
  if (!Array.isArray(detail)) return typeof detail === "string" ? detail : null;

  return detail
    .map((d) => {
      const field = d.loc?.[d.loc.length - 1];
      const label = FIELD_LABELS[field] ?? field;

      let text = d.msg;
      if (d.type === "string_too_short") text = `must be at least ${d.ctx?.min_length} characters`;
      if (d.type === "string_too_long") text = `must be at most ${d.ctx?.max_length} characters`;

      return label ? `${label} ${text}` : text;
    })
    .join(". ");
}

export async function request(path, { method = "GET", body, form } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let payload;
  if (form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    payload = new URLSearchParams(form);
  } else if (body) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(`${BASE}${path}`, { method, headers, body: payload });
  } catch {
    const err = new Error("Server is unreachable");
    err.status = 0;
    throw err;
  }

  if (res.status === 401 && token && !path.startsWith("/auth/")) {
    clearToken();
    window.location.href = "/register?mode=login";
  }

  const data = res.status === 204 ? null : await res.json().catch(() => null);

  if (!res.ok) {
    const err = new Error(formatDetail(data?.detail) ?? "Request failed");
    err.status = res.status;
    throw err;
  }
  return data;
}