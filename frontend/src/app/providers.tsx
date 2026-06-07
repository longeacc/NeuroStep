"use client";

import { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { refresh } from "@/lib/auth";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 60_000, refetchOnWindowFocus: false, retry: 1 },
        },
      })
  );

  // Tente de restaurer la session via le cookie refresh httpOnly au démarrage.
  useEffect(() => {
    void refresh();
  }, []);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
