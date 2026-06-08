"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useApplication } from "@/lib/queries";
import { EvaluationSummary } from "@/components/evaluations/evaluation-summary";
import { EvaluationList } from "@/components/evaluations/evaluation-list";
import { EvaluationForm } from "@/components/evaluations/evaluation-form";

export default function ApplicationDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const appId = Number(params.id);
  const { data: app, isLoading } = useApplication(appId);

  if (isLoading) return <p className="text-muted-foreground">Chargement…</p>;
  if (!app) return <p className="text-destructive">Outil introuvable.</p>;

  return (
    <div className="space-y-6">
      <Link href="/" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Retour au catalogue
      </Link>

      <div>
        <h1 className="text-3xl font-bold tracking-tight">{app.nom}</h1>
        <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <span>{app.plateformes.join(" · ") || "—"}</span>
          <span>•</span>
          <span>{app.gratuit ? "Gratuit" : "Payant"}</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {app.troubles.map((t) => (
          <Badge key={t.id} title={t.fonction?.nom ?? undefined}>
            {t.name}
          </Badge>
        ))}
      </div>

      {app.description && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Fiche</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-line text-sm">{app.description}</p>
          </CardContent>
        </Card>
      )}

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Évaluations professionnelles</h2>
        <EvaluationSummary appId={appId} />
        <EvaluationList appId={appId} />
      </section>

      <EvaluationForm appId={appId} />
    </div>
  );
}
