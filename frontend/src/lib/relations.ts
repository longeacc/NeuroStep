import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Relation } from "@/lib/types";

export function getMyRelations() {
  return api.request<Relation[]>("/relations", { auth: true });
}

export function useMyRelations(enabled = true) {
  return useQuery({ queryKey: ["relations"], queryFn: getMyRelations, enabled });
}
