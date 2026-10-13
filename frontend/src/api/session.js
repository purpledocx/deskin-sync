import { getToken } from "./client";

// JWT payload: { sub: email, user_id, role, exp }
// redirect to login if the Local Storage token is manually corrupted
export function getUser() {
  const token = getToken();
  if (!token) return null;
  try {
    const b64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const p = JSON.parse(atob(b64));
    if (p.exp * 1000 < Date.now()) return null;
    return { id: p.user_id, email: p.sub, role: p.role };
  } catch {
    return null;
  }
}

export const canViewAll = (user) =>
  user?.role === "Teacher" || user?.role === "Admin";