const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const getToken = () => localStorage.getItem("token");
export const setToken = (t) => localStorage.setItem("token", t);
export const clearToken = () => localStorage.removeItem("token");

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
    const detail = Array.isArray(data?.detail)
      ? data.detail.map((d) => d.msg).join(". ")
      : data?.detail;
    const err = new Error(typeof detail === "string" ? detail : "Request failed");
    err.status = res.status;
    throw err;
  }
  return data;
}