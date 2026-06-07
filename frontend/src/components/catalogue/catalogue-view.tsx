"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ApplicationCard } from "./application-card";
import { useApplications, useTroubles } from "@/lib/queries";
import { useFilterStore } from "@/stores/filters";

const OS_OPTIONS = ["iOS", "Android", "Web", "Windows"];
const ALL = "__all__";

export function CatalogueView() {
  const { q, os, trouble, setFilter } = useFilterStore();
  const [searchInput, setSearchInput] = useState(q ?? "");

  const { data: apps, isLoading, isError } = useApplications({ q, os, trouble });
  const { data: troubles } = useTroubles();

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-muted-foreground">Cérébrolésés / Tumeur</p>
        <h1 className="text-3xl font-bold tracking-tight">Catalogue numérique</h1>
      </div>

      <form
        className="grid gap-3 sm:grid-cols-3"
        onSubmit={(e) => {
          e.preventDefault();
          setFilter({ q: searchInput });
        }}
      >
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Rechercher (nom ou description)…"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
        </div>

        <Select
          value={os || ALL}
          onValueChange={(v) => setFilter({ os: v === ALL ? "" : v })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Support (OS)" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>Tous les supports</SelectItem>
            {OS_OPTIONS.map((o) => (
              <SelectItem key={o} value={o}>
                {o}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={trouble || ALL}
          onValueChange={(v) => setFilter({ trouble: v === ALL ? "" : v })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Pathologie (trouble)" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>Tous les troubles</SelectItem>
            {troubles?.map((t) => (
              <SelectItem key={t.id} value={t.name}>
                {t.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </form>

      {isLoading && <p className="text-muted-foreground">Chargement…</p>}
      {isError && (
        <p className="text-destructive">
          Impossible de joindre l&apos;API. Vérifiez que le backend tourne.
        </p>
      )}
      {apps && apps.length === 0 && (
        <p className="text-muted-foreground">Aucun outil trouvé pour ces critères.</p>
      )}

      <div className="grid gap-4">
        {apps?.map((app) => (
          <ApplicationCard key={app.id} app={app} />
        ))}
      </div>
    </div>
  );
}
