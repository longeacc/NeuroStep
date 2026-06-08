"use client";

import { useState } from "react";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, FileDown, Check, Copy } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  usePrescription,
  validatePrescription,
  openPrescriptionPdf,
} from "@/lib/prescriptions";
import { PRIORITE_LABELS } from "@/lib/types";

export default function PrescriptionDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const prescId = Number(params.id);
  const queryClient = useQueryClient();
  const { data: presc, isLoading } = usePrescription(prescId);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  if (isLoading) return <p className="text-muted-foreground">Chargement…</p>;
  if (!presc) return <p className="text-destructive">Prescription introuvable.</p>;

  const shareUrl = presc.share_token
    ? `${window.location.origin}/p/${presc.share_token}`
    : null;

  async function validate() {
    setBusy(true);
    try {
      await validatePrescription(prescId);
      await queryClient.invalidateQueries({ queryKey: ["prescriptions", prescId] });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <Link href="/prescriptions" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Mes prescriptions
      </Link>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Prescription #{presc.id}</h1>
          <p className="text-sm text-muted-foreground">
            Patient #{presc.patient_id} · {new Date(presc.created_at).toLocaleDateString("fr-FR")}
          </p>
        </div>
        <Badge variant={presc.status === "validated" ? "success" : "secondary"}>
          {presc.status === "validated" ? "Validée" : "Brouillon"}
        </Badge>
      </div>

      {presc.notes && (
        <Card>
          <CardContent className="p-4 text-sm">
            <b>Notes :</b> {presc.notes}
          </CardContent>
        </Card>
      )}

      <div className="grid gap-3">
        {presc.items.map((item) => (
          <Card key={item.id}>
            <CardContent className="space-y-1 p-4">
              <div className="flex items-center justify-between">
                <span className="font-semibold">{item.application.nom}</span>
                <Badge variant="outline">Priorité {PRIORITE_LABELS[item.priorite]}</Badge>
              </div>
              {item.consignes && (
                <p className="text-sm"><b>Consignes :</b> {item.consignes}</p>
              )}
              {item.feedback_patient && (
                <p className="text-sm text-emerald-700">
                  <b>Retour patient :</b> {item.feedback_patient}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        {presc.status === "draft" ? (
          <Button onClick={validate} disabled={busy}>
            <Check className="h-4 w-4" /> Valider la prescription
          </Button>
        ) : (
          <>
            <Button onClick={() => openPrescriptionPdf(presc.id)}>
              <FileDown className="h-4 w-4" /> Télécharger le PDF
            </Button>
            {shareUrl && (
              <Button
                variant="outline"
                onClick={() => {
                  navigator.clipboard.writeText(shareUrl);
                  setCopied(true);
                }}
              >
                <Copy className="h-4 w-4" /> {copied ? "Lien copié !" : "Copier le lien patient"}
              </Button>
            )}
          </>
        )}
      </div>
    </div>
  );
}
