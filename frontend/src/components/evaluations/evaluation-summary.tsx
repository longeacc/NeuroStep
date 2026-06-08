"use client";

import { useEvaluationSummary } from "@/lib/evaluations";
import { AXIS_LABELS, EVAL_AXES } from "@/lib/types";

export function EvaluationSummary({ appId }: { appId: number }) {
  const { data } = useEvaluationSummary(appId);
  if (!data || data.nombre === 0) {
    return <p className="text-sm text-muted-foreground">Aucune évaluation pour le moment.</p>;
  }

  return (
    <div className="space-y-2">
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-primary">
          {data.moyenne_globale?.toFixed(1) ?? "—"}
        </span>
        <span className="text-sm text-muted-foreground">
          / 5 · {data.nombre} évaluation{data.nombre > 1 ? "s" : ""}
        </span>
      </div>
      <div className="grid gap-1.5 sm:grid-cols-2">
        {EVAL_AXES.map((axe) => {
          const v = data.moyennes_par_axe[axe];
          return (
            <div key={axe} className="flex items-center gap-2 text-sm">
              <span className="w-36 text-muted-foreground">{AXIS_LABELS[axe]}</span>
              <div className="h-2 flex-1 overflow-hidden rounded bg-secondary">
                <div
                  className="h-full bg-primary"
                  style={{ width: `${((v ?? 0) / 5) * 100}%` }}
                />
              </div>
              <span className="w-8 text-right tabular-nums">{v?.toFixed(1) ?? "—"}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
