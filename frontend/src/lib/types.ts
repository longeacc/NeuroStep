// Types miroir des schémas Pydantic du backend (app/schemas).

export type Role = "admin" | "ergo" | "patient";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  role: Role;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface SousFonction {
  id: number;
  nom: string;
}

export interface FonctionCognitive {
  id: number;
  nom: string;
  is_motrice: boolean;
  sous_fonctions: SousFonction[];
}

export interface Trouble {
  id: number;
  name: string;
  fonction: FonctionCognitive | null;
  sous_fonctions: SousFonction[];
  retentissements: { id: number; libelle: string }[];
}

export interface Theme {
  id: number;
  name: string;
}

export interface Application {
  id: number;
  nom: string;
  description: string | null;
  objectif_ther: string | null;
  image: string | null;
  url_store: string | null;
  gratuit: boolean;
  enrichi: boolean;
  plateformes: string[];
  troubles: Trouble[];
  themes: Theme[];
}

export interface CatalogueFilters {
  q?: string;
  os?: string;
  trouble?: string;
}
