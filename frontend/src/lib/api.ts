// Client API minimal vers le backend FastAPI.
// Le token d'accès JWT (court) est lu depuis le store Zustand (mémoire).
// Le refresh token vit dans un cookie httpOnly géré par le backend.

import { useAuthStore } from "@/stores/auth";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
  }
}

interface RequestOptions extends RequestInit {
  auth?: boolean;
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { auth, headers, ...rest } = opts;
  const h = new Headers(headers);
  if (!h.has("Content-Type") && rest.body) h.set("Content-Type", "application/json");
  if (auth) {
    const token = useAuthStore.getState().accessToken;
    if (token) h.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: h,
    credentials: "include", // permet l'envoi/réception du cookie refresh
  });

  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = (data && (data.detail as string)) || res.statusText;
    throw new ApiError(res.status, detail);
  }
  return data as T;
}

// Construit une query string en ignorant les valeurs vides.
export function qs(params: Record<string, string | undefined>): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v) sp.set(k, v);
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

export const api = { request };
