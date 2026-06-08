"use client";

import { BadgeCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useEvaluations } from "@/lib/evaluations";
import { AXIS_LABELS, EVAL_AXES } from "@/lib/types";

export function EvaluationList({ appId }: { appId: number }) {
  const { data: evals } = useEvaluations(appId);
  if (!evals || evals.length === 0) return null;

  return (
    <div className="space-y-3">
      {evals.map((ev) => (
        <Card key={ev.id}>
          <CardContent className="space-y-2 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-semibold">Moyenne {ev.moyenne.toFixed(1)} / 5</span>
                {ev.auteur_rpps_verifie && (
                  <Badge variant="success" className="gap-1">
                    <BadgeCheck className="h-3.5 w-3.5" /> RPPS vérifié
                  </Badge>
                )}
              </div>
              <span className="text-xs text-muted-foreground">
                {new Date(ev.created_at).toLocaleDateString("fr-FR")}
              </span>
            </div>

            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
              {EVAL_AXES.map((axe) => (
                <span key={axe}>
                  {AXIS_LABELS[axe]} : <b>{ev[axe]}</b>
                </span>
              ))}
            </div>

            {ev.avantages && <p className="text-sm"><b>Avantages :</b> {ev.avantages}</p>}
            {ev.limites && <p className="text-sm"><b>Limites :</b> {ev.limites}</p>}
            {ev.contexte_utilisation && (
              <p className="text-sm"><b>Contexte :</b> {ev.contexte_utilisation}</p>
            )}
            {ev.profil_patient && (
              <p className="text-sm"><b>Profil patient :</b> {ev.profil_patient}</p>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
