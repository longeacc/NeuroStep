import Image from "next/image";
import Link from "next/link";
import { ExternalLink } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Application } from "@/lib/types";

export function ApplicationCard({ app }: { app: Application }) {
  return (
    <Card className="overflow-hidden transition-shadow hover:shadow-md">
      <CardContent className="flex gap-4 p-5">
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-2">
            <Link
              href={`/applications/${app.id}`}
              className="truncate text-lg font-semibold hover:text-primary hover:underline"
            >
              {app.nom}
            </Link>
            {app.enrichi && <Badge variant="success">Enrichi</Badge>}
          </div>

          <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>{app.plateformes.join(" · ") || "—"}</span>
            <span>•</span>
            <span>{app.gratuit ? "Gratuit" : "Payant"}</span>
          </div>

          {app.description && (
            <p className="mb-3 line-clamp-3 whitespace-pre-line text-sm text-foreground/80">
              {app.description}
            </p>
          )}

          <div className="flex flex-wrap gap-1.5">
            {app.troubles.map((t) => (
              <Badge key={t.id} variant="default" title={t.fonction?.nom ?? undefined}>
                {t.name}
              </Badge>
            ))}
          </div>

          {app.url_store && (
            <a
              href={app.url_store}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 inline-flex items-center gap-1 text-sm text-primary hover:underline"
            >
              Voir l&apos;outil <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>

        {app.image && (
          <div className="relative hidden h-28 w-44 flex-shrink-0 overflow-hidden rounded-md border sm:block">
            <Image
              src={app.image}
              alt={app.nom}
              fill
              sizes="176px"
              className="object-cover"
              unoptimized
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
