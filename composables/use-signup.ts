export type SignupBaseData = {
  nom: string;
  prenom: string;
  username: string;
  email: string;
  motDePasseHash: string;
};

export type EtudiantSpecificData = {
  niveau_technique: number;
  competences: string[];
  objectifs_apprentissage: string | null;
  motivation: string | null;
  niveau_energie: number;
};

export type ProfesseurSpecificData = {
  niveau_experience: number;
  specialites: string[];
  motivation_principale: string | null;
  niveau_technologique: number;
};

export type EtudiantSignupData = SignupBaseData & EtudiantSpecificData & {
  status: "Etudiant";
};

export type ProfesseurSignupData = SignupBaseData & ProfesseurSpecificData & {
  status: "Professeur";
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

  const signupEtudiant = async (etudiantData: EtudiantSpecificData) => {
    if (!baseData.value) {
      throw new Error("Données de base manquantes");
    }

    const fullData: EtudiantSignupData = {
      ...baseData.value,
      ...etudiantData,
      status: "Etudiant",
      objectifs_apprentissage: etudiantData.objectifs_apprentissage || null,
      motivation: etudiantData.motivation || null,
    };

    const { data, error } = await useFetch<SignupResponse>("http://127.0.0.1:8000/api/auth/v1/signup", {
      method: "POST",
      body: fullData,
    });

    if (error.value) {
      console.error("Erreur backend:", error.value);

      // Extraire le message d'erreur depuis différents formats possibles
      let errorMessage = "Erreur lors de l'inscription";

      if (error.value.data) {
        if (typeof error.value.data === "string") {
          errorMessage = error.value.data;
        }
        else if (error.value.data.message) {
          errorMessage = error.value.data.message;
        }
        else if (error.value.data.detail) {
          errorMessage = error.value.data.detail;
        }
      }
      else if (error.value.message) {
        errorMessage = error.value.message;
      }

      const err = new Error(errorMessage);
      (err as any).statusCode = error.value.statusCode;
      throw err;
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
      status: "Professeur",
      niveau_experience: mapExperienceToNumber(professeurData.niveau_experience),
      specialites: professeurData.specialites,
      motivation_principale: professeurData.motivation_principale || null,
      niveau_technologique: professeurData.niveau_technologique,
    };

    const { data, error } = await useFetch<SignupResponse>("http://127.0.0.1:8000/api/auth/v1/signup", {
      method: "POST",
      body: fullData,
    });

    if (error.value) {
      console.error("Erreur backend:", error.value);

      // Extraire le message d'erreur depuis différents formats possibles
      let errorMessage = "Erreur lors de l'inscription";

      if (error.value.data) {
        if (typeof error.value.data === "string") {
          errorMessage = error.value.data;
        }
        else if (error.value.data.message) {
          errorMessage = error.value.data.message;
        }
        else if (error.value.data.detail) {
          errorMessage = error.value.data.detail;
        }
      }
      else if (error.value.message) {
        errorMessage = error.value.message;
      }

      const err = new Error(errorMessage);
      (err as any).statusCode = error.value.statusCode;
      throw err;
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
