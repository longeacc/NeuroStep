"use client";

import { Volume2 } from "lucide-react";

// Synthèse vocale intégrée (Web Speech API) — spec 5.7.
export function speak(text: string) {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "fr-FR";
  u.rate = 0.95;
  window.speechSynthesis.speak(u);
}

export function SpeakButton({ text, label = "Écouter" }: { text: string; label?: string }) {
  return (
    <button
      type="button"
      onClick={() => speak(text)}
      aria-label={`Lire à voix haute : ${label}`}
      className="inline-flex items-center gap-3 rounded-2xl bg-sky-700 px-6 py-4 text-xl font-bold text-white shadow-md transition-transform hover:scale-[1.02] focus-visible:outline focus-visible:outline-4 focus-visible:outline-sky-900"
    >
      <Volume2 className="h-7 w-7" aria-hidden />
      {label}
    </button>
  );
}
