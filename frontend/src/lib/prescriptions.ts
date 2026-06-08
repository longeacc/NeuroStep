import { useQuery } from "@tanstack/react-query";
import { api, API_BASE } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type { Prescription, PrescriptionItemInput } from "@/lib/types";

interface CreatePrescriptionInput {
  patient_id: number;
  notes?: string;
  items: PrescriptionItemInput[];
}

export function createPrescription(input: CreatePrescriptionInput) {
  return api.request<Prescription>("/prescriptions", {
    method: "POST",
    auth: true,
    body: JSON.stringify(input),
  });
}

export function getMyPrescriptions() {
  return api.request<Prescription[]>("/prescriptions", { auth: true });
}

export function getPrescription(id: number) {
  return api.request<Prescription>(`/prescriptions/${id}`, { auth: true });
}

export function validatePrescription(id: number) {
  return api.request<Prescription>(`/prescriptions/${id}/validate`, {
    method: "POST",
    auth: true,
  });
}

// Accès patient via lien sécurisé (sans authentification).
export function getSharedPrescription(token: string) {
  return api.request<Prescription>(`/prescriptions/shared/${token}`);
}

export function submitFeedback(token: string, itemId: number, feedback: string) {
  return api.request<{ status: string }>(
    `/prescriptions/shared/${token}/items/${itemId}/feedback`,
    { method: "POST", body: JSON.stringify({ feedback }) }
  );
}

// Le PDF nécessite l'en-tête d'auth : on récupère un blob puis on l'ouvre.
export async function openPrescriptionPdf(id: number) {
  const token = useAuthStore.getState().accessToken;
  const res = await fetch(`${API_BASE}/prescriptions/${id}/pdf`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: "include",
  });
  if (!res.ok) throw new Error("Impossible de générer le PDF");
  const blob = await res.blob();
  window.open(URL.createObjectURL(blob), "_blank");
}

export function useMyPrescriptions(enabled = true) {
  return useQuery({
    queryKey: ["prescriptions"],
    queryFn: getMyPrescriptions,
    enabled,
  });
}

export function usePrescription(id: number, enabled = true) {
  return useQuery({
    queryKey: ["prescriptions", id],
    queryFn: () => getPrescription(id),
    enabled,
  });
}
