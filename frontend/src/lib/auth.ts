// Fonctions d'authentification : login (OAuth2 password), refresh, logout, profil.

import { api, API_BASE } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type { User } from "@/lib/types";

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function login(email: string, password: string): Promise<User> {
  // OAuth2PasswordRequestForm attend du form-urlencoded.
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
    credentials: "include",
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error((data && data.detail) || "Échec de connexion");

  const { access_token } = data as TokenResponse;
  useAuthStore.getState().setAuth(access_token, null);
  const user = await me();
  useAuthStore.getState().setUser(user);
  return user;
}

export async function me(): Promise<User> {
  return api.request<User>("/users/me", { auth: true });
}

// Tente de restaurer une session via le cookie refresh (au démarrage).
export async function refresh(): Promise<boolean> {
  try {
    const data = await api.request<TokenResponse>("/auth/refresh", { method: "POST" });
    useAuthStore.getState().setAuth(data.access_token, null);
    useAuthStore.getState().setUser(await me());
    return true;
  } catch {
    return false;
  }
}

export async function logout(): Promise<void> {
  try {
    await api.request<void>("/auth/logout", { method: "POST" });
  } finally {
    useAuthStore.getState().clear();
  }
}
