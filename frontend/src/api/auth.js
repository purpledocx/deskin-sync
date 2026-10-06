import { request, setToken, clearToken } from "./client";

export const register = ({ name, email, password }) =>
  request("/auth/register", { method: "POST", body: { name, email, password } });

// OAuth2 password flow: email --> username, form != JSON
export async function login(email, password) {
  const data = await request("/auth/login", {
    method: "POST",
    form: { username: email, password },
  });
  setToken(data.access_token);
}

export const logout = () => clearToken();