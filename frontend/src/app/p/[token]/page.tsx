"use client";

import { useEffect, useState } from "react";
import { Brain } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { getSharedPrescription, submitFeedback } from "@/lib/prescriptions";
import { PRIORITE_LABELS, type Prescription } from "@/lib/types";

export default function SharedPrescriptionPage({
  params,
}: {
  params: { token: string };
}) {
  const { token } = params;
  const [presc, setPresc] = useState<Prescription | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    getSharedPrescription(token).then(setPresc).catch(() => setError(true));
  }, [token]);

  if (error) return <p className="text-destructive">Lien invalide ou expiré.</p>;
  if (!presc) return <p className="text-muted-foreground">Chargement…</p>;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-2">
        <Brain className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold">Vos outils recommandés</h1>
      </div>
      <p className="text-sm text-muted-foreground">
        Prescription du {new Date(presc.created_at).toLocaleDateString("fr-FR")}.
      </p>

      <div className="space-y-4">
        {presc.items.map((item) => (
          <SharedItem
            key={item.id}
            token={token}
            itemId={item.id}
            nom={item.application.nom}
            description={item.application.description}
            consignes={item.consignes}
            priorite={item.priorite}
            initialFeedback={item.feedback_patient}
          />
        ))}
      </div>
    </div>
  );
}

function SharedItem({
  token,
  itemId,
  nom,
  description,
  consignes,
  priorite,
  initialFeedback,
}: {
  token: string;
  itemId: number;
  nom: string;
  description: string | null;
  consignes: string | null;
  priorite: number;
  initialFeedback: string | null;
}) {
  const [feedback, setFeedback] = useState(initialFeedback ?? "");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  async function send() {
    if (!feedback.trim()) return;
    setBusy(true);
    try {
      await submitFeedback(token, itemId, feedback);
      setSaved(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card>
      <CardContent className="space-y-2 p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">{nom}</h2>
          <Badge variant="outline">Priorité {PRIORITE_LABELS[priorite]}</Badge>
        </div>
        {consignes && (
          <p className="rounded bg-secondary p-2 text-sm">
            <b>Consignes :</b> {consignes}
          </p>
        )}
        {description && (
          <p className="whitespace-pre-line text-sm text-muted-foreground">{description}</p>
        )}

        <div className="space-y-2 pt-2">
          <Textarea
            placeholder="Votre retour d'usage…"
            value={feedback}
            onChange={(e) => {
              setFeedback(e.target.value);
              setSaved(false);
            }}
            rows={2}
          />
          <Button size="sm" onClick={send} disabled={busy}>
            {saved ? "Merci !" : "Envoyer mon retour"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
