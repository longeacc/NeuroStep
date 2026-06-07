"use client";

import Link from "next/link";
import { Brain, LogIn, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth";
import { logout } from "@/lib/auth";

export function Navbar() {
  const user = useAuthStore((s) => s.user);

  return (
    <header className="border-b bg-background">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Brain className="h-6 w-6 text-primary" />
          <span>
            Neuro<span className="text-primary">Step</span>
          </span>
        </Link>

        <nav className="flex items-center gap-3">
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
            Catalogue
          </Link>
          {user ? (
            <>
              <span className="text-sm text-muted-foreground">{user.email}</span>
              <Button variant="outline" size="sm" onClick={() => logout()}>
                <LogOut className="h-4 w-4" /> Déconnexion
              </Button>
            </>
          ) : (
            <Button asChild variant="outline" size="sm">
              <Link href="/login">
                <LogIn className="h-4 w-4" /> Connexion
              </Link>
            </Button>
          )}
        </nav>
      </div>
    </header>
  );
}
