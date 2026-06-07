// State des filtres du catalogue (Zustand).

import { create } from "zustand";
import type { CatalogueFilters } from "@/lib/types";

interface FilterState extends CatalogueFilters {
  setFilter: (patch: Partial<CatalogueFilters>) => void;
  reset: () => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  q: "",
  os: "",
  trouble: "",
  setFilter: (patch) => set(patch),
  reset: () => set({ q: "", os: "", trouble: "" }),
}));
