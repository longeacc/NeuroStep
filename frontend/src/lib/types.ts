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

// --- Relations thérapeutiques ---
export interface Relation {
  id: number;
  ergo_id: number;
  patient_id: number;
  active: boolean;
  created_at: string;
}

// --- Évaluations multi-axes (spec 5.5) ---
export const EVAL_AXES = [
  "pertinence_clinique",
  "utilisabilite",
  "efficacite",
  "accessibilite",
  "integration",
] as const;
export type EvalAxis = (typeof EVAL_AXES)[number];

export const AXIS_LABELS: Record<EvalAxis, string> = {
  pertinence_clinique: "Pertinence clinique",
  utilisabilite: "Utilisabilité",
  efficacite: "Efficacité",
  accessibilite: "Accessibilité",
  integration: "Intégration",
};

export interface EvaluationInput {
  application_id: number;
  pertinence_clinique: number;
  utilisabilite: number;
  efficacite: number;
  accessibilite: number;
  integration: number;
  avantages?: string;
  limites?: string;
  contexte_utilisation?: string;
  profil_patient?: string;
}

export interface Evaluation extends EvaluationInput {
  id: number;
  user_id: number;
  moyenne: number;
  created_at: string;
  auteur_rpps_verifie: boolean;
}

export interface EvaluationSummary {
  application_id: number;
  nombre: number;
  moyenne_globale: number | null;
  moyennes_par_axe: Partial<Record<EvalAxis, number>>;
}

// --- Prescriptions (spec 5.4) ---
export interface PrescriptionItemInput {
  application_id: number;
  consignes?: string;
  priorite: number; // 1 haute … 3 basse
}

export interface PrescriptionItem {
  id: number;
  application_id: number;
  consignes: string | null;
  priorite: number;
  feedback_patient: string | null;
  application: Application;
}

export interface Prescription {
  id: number;
  ergo_id: number;
  patient_id: number;
  status: "draft" | "validated";
  notes: string | null;
  share_token: string | null;
  created_at: string;
  validated_at: string | null;
  items: PrescriptionItem[];
}

export const PRIORITE_LABELS: Record<number, string> = {
  1: "Haute",
  2: "Moyenne",
  3: "Basse",
};
