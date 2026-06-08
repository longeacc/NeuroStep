import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Evaluation, EvaluationInput, EvaluationSummary } from "@/lib/types";

export function createEvaluation(input: EvaluationInput) {
  return api.request<Evaluation>("/evaluations", {
    method: "POST",
    auth: true,
    body: JSON.stringify(input),
  });
}

export function getEvaluations(appId: number) {
  return api.request<Evaluation[]>(`/evaluations/application/${appId}`);
}

export function getEvaluationSummary(appId: number) {
  return api.request<EvaluationSummary>(`/evaluations/application/${appId}/summary`);
}

export function useEvaluations(appId: number) {
  return useQuery({
    queryKey: ["evaluations", appId],
    queryFn: () => getEvaluations(appId),
  });
}

export function useEvaluationSummary(appId: number) {
  return useQuery({
    queryKey: ["evaluations", appId, "summary"],
    queryFn: () => getEvaluationSummary(appId),
  });
}
