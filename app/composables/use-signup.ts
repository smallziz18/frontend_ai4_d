import { useApi } from "~/composables/use-api";

export type SignupBaseData = {
  nom: string;
  prenom: string;
  username: string;
  email: string;
  motDePasseHash: string;
  status: "Etudiant" | "Professeur";
};

export type EtudiantPreferencesData = {
  niveau_technique: number;
  competences: string[];
  objectifs_apprentissage: string | null;
  motivation: string | null;
  niveau_energie: number;
};

export type ProfesseurPreferencesData = {
  niveau_experience: string;
  specialites: string[];
  motivation_principale: string | null;
  niveau_technologique: number;
};

export type EtudiantSignupData = SignupBaseData & {
  status: "Etudiant";
};

export type ProfesseurSignupData = SignupBaseData & {
  status: "Professeur";
};

export function useSignup() {
  const api = useApi();
  const baseData = useState<SignupBaseData | null>("signupBaseData", () => null);
  // Stocker les préférences pour les utiliser après le questionnaire
  const etudiantPreferences = useState<EtudiantPreferencesData | null>("etudiantPreferences", () => null);
  const professeurPreferences = useState<ProfesseurPreferencesData | null>("professeurPreferences", () => null);

  const setBaseData = (data: Omit<SignupBaseData, "status">, status: "Etudiant" | "Professeur") => {
    baseData.value = { ...data, status };
  };

  const signupEtudiant = async (preferences: EtudiantPreferencesData) => {
    if (!baseData.value) {
      throw new Error("Données de base manquantes");
    }

    // Stocker les préférences pour les utiliser après le questionnaire
    etudiantPreferences.value = preferences;

    // N'envoyer que les données de base au backend (sans créer de profil)
    const signupData: EtudiantSignupData = {
      nom: baseData.value.nom,
      prenom: baseData.value.prenom,
      username: baseData.value.username,
      email: baseData.value.email,
      motDePasseHash: baseData.value.motDePasseHash,
      status: "Etudiant",
    };

    console.warn("Données envoyées au backend (sans profil):", signupData);

    try {
      const data = await api.auth.signup(signupData);

      // NE PAS nettoyer les données temporaires - on en aura besoin pour le questionnaire
      // baseData.value = null;

      return data;
    }
    catch (error: any) {
      console.error("Erreur backend:", error);
      const errorMessage = error.data?.detail || error.message || "Erreur lors de l'inscription";
      throw new Error(errorMessage);
    }
  };

  const signupProfesseur = async (preferences: ProfesseurPreferencesData) => {
    if (!baseData.value) {
      throw new Error("Données de base manquantes");
    }

    // Stocker les préférences pour les utiliser après le questionnaire
    professeurPreferences.value = preferences;

    // N'envoyer que les données de base au backend (sans créer de profil)
    const signupData: ProfesseurSignupData = {
      nom: baseData.value.nom,
      prenom: baseData.value.prenom,
      username: baseData.value.username,
      email: baseData.value.email,
      motDePasseHash: baseData.value.motDePasseHash,
      status: "Professeur",
    };

    console.warn("Données envoyées au backend (sans profil):", signupData);

    try {
      const data = await api.auth.signup(signupData);

      // NE PAS nettoyer les données temporaires - on en aura besoin pour le questionnaire
      // baseData.value = null;

      return data;
    }
    catch (error: any) {
      console.error("Erreur backend:", error);
      const errorMessage = error.data?.detail || error.message || "Erreur lors de l'inscription";
      throw new Error(errorMessage);
    }
  };

  const clearSignupData = () => {
    baseData.value = null;
    etudiantPreferences.value = null;
    professeurPreferences.value = null;
  };

  return {
    baseData: readonly(baseData),
    etudiantPreferences: readonly(etudiantPreferences),
    professeurPreferences: readonly(professeurPreferences),
    setBaseData,
    signupEtudiant,
    signupProfesseur,
    clearSignupData,
  };
}
