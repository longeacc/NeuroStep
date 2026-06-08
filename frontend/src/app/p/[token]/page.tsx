"use client";

import { useEffect, useState } from "react";
import { Atkinson_Hyperlegible } from "next/font/google";
import {
  AppWindow,
  ChevronLeft,
  ChevronRight,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";
import { SpeakButton, speak } from "@/components/patient/speak-button";
import { getSharedPrescription, submitFeedback } from "@/lib/prescriptions";
import type { Prescription } from "@/lib/types";

// Typographie conçue pour la basse vision (spec 5.7).
const atkinson = Atkinson_Hyperlegible({ subsets: ["latin"], weight: ["400", "700"] });

export default function SharedPrescriptionPage({
  params,
}: {
  params: { token: string };
}) {
  const { token } = params;
  const [presc, setPresc] = useState<Prescription | null>(null);
  const [error, setError] = useState(false);
  const [index, setIndex] = useState(0);
  const [sent, setSent] = useState<Record<number, boolean>>({});

  useEffect(() => {
    getSharedPrescription(token).then(setPresc).catch(() => setError(true));
  }, [token]);

  if (error)
    return (
      <p className={`${atkinson.className} text-2xl`}>
        Ce lien n’est plus valide. Demandez-en un nouveau à votre thérapeute.
      </p>
    );
  if (!presc) return <p className={`${atkinson.className} text-2xl`}>Chargement…</p>;

  const item = presc.items[index];
  const total = presc.items.length;

  async function sendFeedback(positif: boolean) {
    const message = positif ? "Cet outil m’aide." : "Cet outil est difficile pour moi.";
    await submitFeedback(token, item.id, message);
    setSent((s) => ({ ...s, [item.id]: true }));
    speak("Merci pour votre retour.");
  }

  // Palette réduite à 3 couleurs : fond ardoise clair, texte ardoise foncé, accent ciel.
  return (
    <div className={`${atkinson.className} mx-auto max-w-xl space-y-8 text-slate-800`}>
      <header className="text-center">
        <p className="text-lg text-slate-500">
          Outil {index + 1} sur {total}
        </p>
        <h1 className="mt-1 text-3xl font-bold">Mes outils</h1>
      </header>

      <section className="space-y-6 rounded-3xl border-4 border-sky-700 bg-white p-8 text-center">
        <AppWindow className="mx-auto h-20 w-20 text-sky-700" aria-hidden />
        <h2 className="text-3xl font-bold">{item.application.nom}</h2>

        {item.consignes && (
          <p className="rounded-2xl bg-sky-50 p-4 text-2xl leading-relaxed">
            {item.consignes}
          </p>
        )}

        {/* Action 1 : écouter (synthèse vocale) */}
        <SpeakButton
          text={`${item.application.nom}. ${item.consignes ?? ""}`}
          label="Écouter"
        />

        {/* Feedback en un seul geste (pas de saisie clavier). */}
        {sent[item.id] ? (
          <p className="text-2xl font-bold text-sky-700">Merci pour votre retour !</p>
        ) : (
          <div className="flex justify-center gap-4">
            <button
              type="button"
              onClick={() => sendFeedback(true)}
              className="inline-flex items-center gap-2 rounded-2xl bg-sky-700 px-6 py-4 text-xl font-bold text-white"
            >
              <ThumbsUp className="h-6 w-6" aria-hidden /> Ça m’aide
            </button>
            <button
              type="button"
              onClick={() => sendFeedback(false)}
              className="inline-flex items-center gap-2 rounded-2xl border-4 border-sky-700 px-6 py-4 text-xl font-bold text-sky-700"
            >
              <ThumbsDown className="h-6 w-6" aria-hidden /> Difficile
            </button>
          </div>
        )}
      </section>

      {/* Navigation : au plus 2 boutons (précédent / suivant). */}
      <nav className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setIndex((i) => Math.max(0, i - 1))}
          disabled={index === 0}
          className="inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-xl font-bold text-sky-700 disabled:invisible"
        >
          <ChevronLeft className="h-7 w-7" aria-hidden /> Précédent
        </button>
        <button
          type="button"
          onClick={() => setIndex((i) => Math.min(total - 1, i + 1))}
          disabled={index === total - 1}
          className="inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-xl font-bold text-sky-700 disabled:invisible"
        >
          Suivant <ChevronRight className="h-7 w-7" aria-hidden />
        </button>
      </nav>
    </div>
  );
}
