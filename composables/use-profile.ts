export type UserProfile = {
  analysis?: {
    niveau_global?: string;
    points_forts?: string[];
    points_ameliorer?: string[];
    style_apprentissage?: string;
  };
  recommendations?: string[];
  next_steps?: string[];
  suggested_courses?: Array<{
    title: string;
    description: string;
    difficulty: string;
    duration: string;
  }>;
  statistics?: {
    score: string;
    score_percentage: number;
    completed_at: string;
  };
};

export function useProfile() {
  const profile = useState<UserProfile | null>("user_profile", () => null);
  const profileLoading = useState<boolean>("profile_loading", () => false);
  const profileError = useState<string | null>("profile_error", () => null);

  // Récupérer le profil depuis le backend
  const fetchProfile = async () => {
    try {
      profileLoading.value = true;
      profileError.value = null;

      const accessToken = useCookie("access_token").value;

      const data = await $fetch<UserProfile>(
        "http://127.0.0.1:8000/api/profile/v1/me",
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        },
      );

      profile.value = data;
      return data;
    }
    catch (e: any) {
      console.error("Erreur fetchProfile:", e);
      profileError.value = e.message || "Erreur lors de la récupération du profil";
      return null;
    }
    finally {
      profileLoading.value = false;
    }
  };

  // Récupérer les recommandations de l'IA
  const fetchRecommendations = async () => {
    try {
      const accessToken = useCookie("access_token").value;

      const data = await $fetch<{ recommendations: string[]; next_steps: string[] }>(
        "http://127.0.0.1:8000/api/profile/v1/recommendations",
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        },
      );

      if (profile.value) {
        profile.value.recommendations = data.recommendations;
        profile.value.next_steps = data.next_steps;
      }

      return data;
    }
    catch (e: any) {
      console.error("Erreur fetchRecommendations:", e);
      return null;
    }
  };

  // Réinitialiser le profil
  const resetProfile = () => {
    profile.value = null;
    profileLoading.value = false;
    profileError.value = null;
  };

  return {
    profile,
    profileLoading,
    profileError,
    fetchProfile,
    fetchRecommendations,
    resetProfile,
  };
}
