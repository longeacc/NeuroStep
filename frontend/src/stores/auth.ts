// State d'authentification (Zustand). Le token d'accès reste en mémoire
// (pas de persistance localStorage — réduit la surface XSS) ; il est
// régénéré via le cookie refresh httpOnly au rechargement.

import { create } from "zustand";
import type { User } from "@/lib/types";

interface AuthState {
  accessToken: string | null;
  user: User | null;
  setAuth: (token: string, user: User | null) => void;
  setUser: (user: User | null) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setAuth: (accessToken, user) => set({ accessToken, user }),
  setUser: (user) => set({ user }),
  clear: () => set({ accessToken: null, user: null }),
}));
