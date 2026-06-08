"use client";

import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { createEvaluation } from "@/lib/evaluations";
import { useAuthStore } from "@/stores/auth";
import { AXIS_LABELS, EVAL_AXES, type EvalAxis } from "@/lib/types";

const NOTES = [1, 2, 3, 4, 5];

export function EvaluationForm({ appId }: { appId: number }) {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const [axes, setAxes] = useState<Record<EvalAxis, number>>({
    pertinence_clinique: 4,
    utilisabilite: 4,
    efficacite: 4,
    accessibilite: 4,
    integration: 4,
  });
  const [texts, setTexts] = useState({
    avantages: "",
    limites: "",
    contexte_utilisation: "",
    profil_patient: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);

  // Seul un ergothérapeute connecté peut évaluer.
  if (!user || user.role !== "ergo") {
    return (
      <p className="text-sm text-muted-foreground">
        Connectez-vous en tant qu&apos;ergothérapeute pour évaluer cet outil.
      </p>
    );
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await createEvaluation({ application_id: appId, ...axes, ...texts });
      await queryClient.invalidateQueries({ queryKey: ["evaluations", appId] });
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur");
    } finally {
      setLoading(false);
    }
  }

  if (done) return <p className="text-sm text-emerald-600">Évaluation enregistrée. Merci !</p>;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Évaluer cet outil</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={submit}>
          <div className="grid gap-3 sm:grid-cols-2">
            {EVAL_AXES.map((axe) => (
              <div key={axe} className="space-y-1">
                <Label>{AXIS_LABELS[axe]}</Label>
                <div className="flex gap-1">
                  {NOTES.map((n) => (
                    <button
                      key={n}
                      type="button"
                      onClick={() => setAxes((a) => ({ ...a, [axe]: n }))}
                      className={`h-8 w-8 rounded border text-sm ${
                        axes[axe] >= n
                          ? "border-primary bg-primary text-primary-foreground"
                          : "border-input"
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {(["avantages", "limites", "contexte_utilisation", "profil_patient"] as const).map(
            (field) => (
              <div key={field} className="space-y-1">
                <Label className="capitalize">{field.replace(/_/g, " ")}</Label>
                <Textarea
                  value={texts[field]}
                  onChange={(e) => setTexts((t) => ({ ...t, [field]: e.target.value }))}
                  rows={2}
                />
              </div>
            )
          )}

          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button type="submit" disabled={loading}>
            {loading ? "Envoi…" : "Publier l'évaluation"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
