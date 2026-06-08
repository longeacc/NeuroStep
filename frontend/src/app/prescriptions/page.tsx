"use client";

import Link from "next/link";
import { Plus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useMyPrescriptions } from "@/lib/prescriptions";
import { useAuthStore } from "@/stores/auth";

export default function PrescriptionsPage() {
  const user = useAuthStore((s) => s.user);
  const { data, isLoading } = useMyPrescriptions(!!user && user.role === "ergo");

  if (!user || user.role !== "ergo") {
    return (
      <p className="text-muted-foreground">
        Réservé aux ergothérapeutes. <Link href="/login" className="text-primary underline">Connexion</Link>
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Mes prescriptions</h1>
        <Button asChild>
          <Link href="/prescriptions/new">
            <Plus className="h-4 w-4" /> Nouvelle prescription
          </Link>
        </Button>
      </div>

      {isLoading && <p className="text-muted-foreground">Chargement…</p>}
      {data && data.length === 0 && (
        <p className="text-muted-foreground">Aucune prescription pour le moment.</p>
      )}

      <div className="grid gap-3">
        {data?.map((p) => (
          <Link key={p.id} href={`/prescriptions/${p.id}`}>
            <Card className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-center justify-between p-4">
                <div>
                  <div className="font-semibold">Prescription #{p.id}</div>
                  <div className="text-sm text-muted-foreground">
                    Patient #{p.patient_id} · {p.items.length} outil(s) ·{" "}
                    {new Date(p.created_at).toLocaleDateString("fr-FR")}
                  </div>
                </div>
                <Badge variant={p.status === "validated" ? "success" : "secondary"}>
                  {p.status === "validated" ? "Validée" : "Brouillon"}
                </Badge>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
