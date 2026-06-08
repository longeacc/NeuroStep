"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useApplications } from "@/lib/queries";
import { useMyRelations } from "@/lib/relations";
import { createPrescription } from "@/lib/prescriptions";
import { useAuthStore } from "@/stores/auth";
import { PRIORITE_LABELS } from "@/lib/types";

interface Selection {
  consignes: string;
  priorite: number;
}

export default function NewPrescriptionPage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const isErgo = !!user && user.role === "ergo";

  const { data: relations } = useMyRelations(isErgo);
  const { data: apps } = useApplications({});
  const [patientId, setPatientId] = useState<string>("");
  const [notes, setNotes] = useState("");
  const [selected, setSelected] = useState<Record<number, Selection>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isErgo) {
    return <p className="text-muted-foreground">Réservé aux ergothérapeutes.</p>;
  }

  const activePatients = (relations ?? []).filter((r) => r.active);

  function toggle(appId: number) {
    setSelected((s) => {
      const next = { ...s };
      if (next[appId]) delete next[appId];
      else next[appId] = { consignes: "", priorite: 2 };
      return next;
    });
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const items = Object.entries(selected).map(([appId, sel]) => ({
      application_id: Number(appId),
      consignes: sel.consignes || undefined,
      priorite: sel.priorite,
    }));
    if (!patientId) return setError("Sélectionnez un patient.");
    if (items.length === 0) return setError("Sélectionnez au moins un outil.");

    setLoading(true);
    try {
      const presc = await createPrescription({
        patient_id: Number(patientId),
        notes: notes || undefined,
        items,
      });
      router.push(`/prescriptions/${presc.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="space-y-6" onSubmit={submit}>
      <h1 className="text-3xl font-bold tracking-tight">Nouvelle prescription</h1>

      <div className="space-y-2">
        <Label>Patient</Label>
        <Select value={patientId} onValueChange={setPatientId}>
          <SelectTrigger className="max-w-sm">
            <SelectValue placeholder="Sélectionner un patient" />
          </SelectTrigger>
          <SelectContent>
            {activePatients.map((r) => (
              <SelectItem key={r.patient_id} value={String(r.patient_id)}>
                Patient #{r.patient_id}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {activePatients.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Aucun patient lié. Créez d&apos;abord une relation thérapeutique.
          </p>
        )}
      </div>

      <div className="space-y-2">
        <Label>Notes générales (optionnel)</Label>
        <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} />
      </div>

      <div className="space-y-2">
        <Label>Outils ({Object.keys(selected).length} sélectionné(s))</Label>
        <div className="grid gap-2">
          {apps?.map((app) => {
            const sel = selected[app.id];
            return (
              <Card key={app.id}>
                <CardContent className="space-y-3 p-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={!!sel}
                      onChange={() => toggle(app.id)}
                      className="h-4 w-4"
                    />
                    <span className="font-medium">{app.nom}</span>
                  </label>

                  {sel && (
                    <div className="grid gap-2 pl-6 sm:grid-cols-[1fr_160px]">
                      <Input
                        placeholder="Consignes personnalisées…"
                        value={sel.consignes}
                        onChange={(e) =>
                          setSelected((s) => ({
                            ...s,
                            [app.id]: { ...sel, consignes: e.target.value },
                          }))
                        }
                      />
                      <Select
                        value={String(sel.priorite)}
                        onValueChange={(v) =>
                          setSelected((s) => ({
                            ...s,
                            [app.id]: { ...sel, priorite: Number(v) },
                          }))
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {[1, 2, 3].map((p) => (
                            <SelectItem key={p} value={String(p)}>
                              Priorité {PRIORITE_LABELS[p]}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}
      <Button type="submit" disabled={loading}>
        {loading ? "Création…" : "Créer la prescription"}
      </Button>
    </form>
  );
}
