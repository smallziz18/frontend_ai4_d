import { useApi } from "~/composables/use-api";

export type ProfileAnalysis = {
  niveau_global?: string;
  points_forts?: string[];
  points_ameliorer?: string[];
  style_apprentissage?: string;
  [key: string]: any;
};

export type Profile = {
  analysis?: ProfileAnalysis;
  recommendations?: string[];
  next_steps?: string[];
  [key: string]: any;
};

export type ProfileTaskStatus = {
  task_id: string;
  status: string;
  result?: Profile;
  error?: string;
};

export function useProfile() {
  const api = useApi();
  const profile = useState<Profile | null>("user_profile", () => null);
  const profileLoading = useState<boolean>("profile_loading", () => false);
  const profileTaskId = useState<string | null>("profile_task_id", () => null);

  // Récupérer le profil depuis le backend
  const fetchProfile = async () => {
    try {
      profileLoading.value = true;
      const data = await api.profile.getMyProfile();

      if (data) {
        profile.value = data as Profile;
      }

      return data;
    }
    catch (e: any) {
      console.error("Erreur fetchProfile:", e);
      return null;
    }
    finally {
      profileLoading.value = false;
    }
  };

  // Récupérer les recommandations
  const fetchRecommendations = async () => {
    try {
      const data = await api.profile.getRecommendations();

      if (data && profile.value) {
        profile.value.recommendations = (data as any).recommendations;
        profile.value.next_steps = (data as any).next_steps;
      }

      return data;
    }
    catch (e: any) {
      console.error("Erreur fetchRecommendations:", e);
      return null;
    }
  };

  // Analyser le questionnaire et générer le profil
  const analyzeQuiz = async (quizResult: any) => {
    try {
      profileLoading.value = true;
      const data = await api.questionnaire.analyzeQuiz(quizResult);

      if (data?.task_id) {
        profileTaskId.value = data.task_id;
        return data.task_id;
      }

      throw new Error("Aucun task_id reçu");
    }
    catch (e: any) {
      console.error("Erreur analyzeQuiz:", e);
      throw e;
    }
    finally {
      profileLoading.value = false;
    }
  };

  // Vérifier le statut de l'analyse du profil
  const checkProfileStatus = async (taskId: string): Promise<ProfileTaskStatus | null> => {
    try {
      const data = await api.questionnaire.getAnalysisResult(taskId);
      return data as ProfileTaskStatus;
    }
    catch (e: any) {
      console.error("Erreur checkProfileStatus:", e);
      return null;
    }
  };

  // Cache pour hasProfile avec timestamp
  const hasProfileCache = useState<{ value: boolean; timestamp: number } | null>("has_profile_cache_with_time", () => null);
  const CACHE_DURATION = 30000; // 30 secondes

  // Vérifier si l'utilisateur a un profil
  const hasProfile = async (): Promise<boolean> => {
    try {
      // Vérifier le cache
      const now = Date.now();
      if (hasProfileCache.value && (now - hasProfileCache.value.timestamp) < CACHE_DURATION) {
        console.warn("hasProfile: Utilisation du cache");
        return hasProfileCache.value.value;
      }

      // Appel API
      const data = await api.profile.hasProfile();
      // ✅ Si le profil existe, c'est suffisant
      // Le flag questionnaire_completed est informatif mais pas bloquant
      const result = data.has_profile;

      // Mettre à jour le cache
      hasProfileCache.value = { value: result, timestamp: now };

      return result;
    }
    catch (e: any) {
      console.error("Erreur hasProfile:", e);
      return false;
    }
  };

  // Invalider le cache hasProfile
  const invalidateHasProfileCache = () => {
    hasProfileCache.value = null;
  };

  // Réinitialiser le profil
  const resetProfile = () => {
    profile.value = null;
    profileLoading.value = false;
    profileTaskId.value = null;
  };

  return {
    profile,
    profileLoading,
    profileTaskId,
    fetchProfile,
    fetchRecommendations,
    analyzeQuiz,
    checkProfileStatus,
    hasProfile,
    invalidateHasProfileCache,
    resetProfile,
  };
}
