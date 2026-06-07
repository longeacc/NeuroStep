import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Navbar } from "@/components/navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "NeuroStep — Catalogue d'outils numériques",
  description:
    "Catalogue d'outils numériques pour cérébrolésés / tumeur, à destination des ergothérapeutes.",
  manifest: "/manifest.webmanifest",
};

export const viewport: Viewport = {
  themeColor: "#1f8fc0",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <Providers>
          <Navbar />
          <main className="container py-8">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
