export type SignupBaseData = {
  nom: string;
  prenom: string;
  username: string;
  email: string;
  motDePasseHash: string;
};

export type EtudiantSignupData = SignupBaseData & {
  status: "StatutUtilisateur.ETUDIANT";
  niveau_technique: number;
  competences: string[];
  objectifs_apprentissage: string | null;
  motivation: string | null;
  niveau_energie: number;
};

export type ProfesseurSignupData = SignupBaseData & {
  status: "StatutUtilisateur.PROFESSEUR";
  niveau_experience: number;
  specialites: string[];
  motivation_principale: string | null;
  niveau_technologique: number;
};

type SignupResponse = {
  message: string;
  new_user: {
    id: string;
    username: string;
    email: string;
  };
};

// Fonction pour mapper le niveau d'expérience vers un nombre
function mapExperienceToNumber(experience: string): number {
  const mapping: Record<string, number> = {
    Débutant: 2,
    Intermédiaire: 5,
    Avancé: 10,
    Expert: 15,
  };
  return mapping[experience] || 2;
}

export function useSignup() {
  const baseData = useState<SignupBaseData | null>("signupBaseData", () => null);

  const setBaseData = (data: SignupBaseData) => {
    baseData.value = data;
  };

  const signupEtudiant = async (etudiantData: Omit<EtudiantSignupData, keyof SignupBaseData>) => {
    if (!baseData.value) {
      throw new Error("Données de base manquantes");
    }

    const fullData: EtudiantSignupData = {
      ...baseData.value,
      ...etudiantData,
      status: "StatutUtilisateur.ETUDIANT",
      objectifs_apprentissage: etudiantData.objectifs_apprentissage || null,
      motivation: etudiantData.motivation || null,
    };

    console.log("Données envoyées au backend:", fullData);

    const { data, error } = await useFetch<SignupResponse>("http://127.0.0.1:8000/api/auth/v1/signup", {
      method: "POST",
      body: fullData,
    });

    if (error.value) {
      console.error("Erreur backend:", error.value);
      const errorMessage = error.value.data?.detail || "Erreur lors de l'inscription";
      throw new Error(errorMessage);
    }

    // Nettoyer les données temporaires après inscription réussie
    baseData.value = null;

    return data.value;
  };

  const signupProfesseur = async (professeurData: {
    niveau_experience: string;
    specialites: string[];
    motivation_principale: string;
    niveau_technologique: number;
  }) => {
    if (!baseData.value) {
      throw new Error("Données de base manquantes");
    }

    // Convertir le niveau d'expérience en nombre
    const fullData: ProfesseurSignupData = {
      ...baseData.value,
      status: "StatutUtilisateur.PROFESSEUR",
      niveau_experience: mapExperienceToNumber(professeurData.niveau_experience),
      specialites: professeurData.specialites,
      motivation_principale: professeurData.motivation_principale || null,
      niveau_technologique: professeurData.niveau_technologique,
    };

    console.log("Données envoyées au backend:", fullData);

    const { data, error } = await useFetch<SignupResponse>("http://127.0.0.1:8000/api/auth/v1/signup", {
      method: "POST",
      body: fullData,
    });

    if (error.value) {
      console.error("Erreur backend:", error.value);
      const errorMessage = error.value.data?.detail || "Erreur lors de l'inscription";
      throw new Error(errorMessage);
    }

    // Nettoyer les données temporaires après inscription réussie
    baseData.value = null;

    return data.value;
  };

  return {
    baseData: readonly(baseData),
    setBaseData,
    signupEtudiant,
    signupProfesseur,
  };
}
