// Accès données catalogue + hooks TanStack Query.

import { useQuery } from "@tanstack/react-query";
import { api, qs } from "@/lib/api";
import type { Application, Trouble, Theme, CatalogueFilters } from "@/lib/types";

export function getApplications(filters: CatalogueFilters) {
  return api.request<Application[]>(
    `/applications${qs({ q: filters.q, os: filters.os, trouble: filters.trouble })}`
  );
}

export function getTroubles() {
  return api.request<Trouble[]>("/applications/_meta/troubles");
}

export function getThemes() {
  return api.request<Theme[]>("/applications/_meta/themes");
}

export function useApplications(filters: CatalogueFilters) {
  return useQuery({
    queryKey: ["applications", filters],
    queryFn: () => getApplications(filters),
  });
}

export function useTroubles() {
  return useQuery({ queryKey: ["troubles"], queryFn: getTroubles });
}
