/**
 * Composable pour gérer les cours et la roadmap d'apprentissage
 */

type _Course = {
  id: string;
  title: string;
  description: string;
  level: string;
  duration: string;
  modules: number;
  enrolled: boolean;
  progress: number;
  image: string;
  color: string;
  tags: string[];
  created_at?: string;
  updated_at?: string;
};

type RoadmapGenerateRequest = {
  duration_weeks: number;
  force_regenerate?: boolean;
};

type ProgressUpdateRequest = {
  module_id: string;
  lesson_id?: string;
  time_spent_minutes?: number;
};

type LessonCompleteRequest = {
  lesson_id: string;
  time_spent_minutes: number;
};

type ModuleCompleteRequest = {
  module_id: string;
  evaluation_score: number;
};

type NoteRequest = {
  module_id: string;
  content: string;
};

type ProjectRequest = {
  module_id: string;
  title: string;
  description: string;
  github_url?: string;
  demo_url?: string;
};

export function useCourses() {
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Helper pour les appels API
  async function apiFetch(endpoint: string, options: any = {}) {
    const accessToken = useCookie("access_token").value;
    const baseURL = "http://127.0.0.1:8000";

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`;
    }

    return await $fetch(`${baseURL}${endpoint}`, {
      ...options,
      headers,
    });
  }

  // ==================== ROADMAP ====================

  /**
   * Générer une roadmap personnalisée
   */
  async function generateRoadmap(request: RoadmapGenerateRequest) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/profile/v1/roadmap/generate", {
        method: "POST",
        body: JSON.stringify(request),
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la génération de la roadmap";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Récupérer la roadmap active de l'utilisateur
   */
  async function getActiveRoadmap() {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/profile/v1/roadmap/my-active", {
        method: "GET",
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la récupération de la roadmap";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Récupérer la progression détaillée d'un cours
   */
  async function getCourseProgression(courseId: string) {
    isLoading.value = true;
    error.value = null;

    try {
      // Essayer d'abord la route roadmap
      let data;
      try {
        data = await apiFetch(`/api/profile/v1/roadmap/progression/${courseId}`, {
          method: "GET",
        });
      }
      catch {
        // Fallback sur la route AI courses
        data = await apiFetch(`/api/ai/v1/courses/${courseId}`, {
          method: "GET",
        });
      }

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la récupération de la progression";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  // ==================== COURS AI AGENTS ====================

  /**
   * Générer un cours avec l'IA
   */
  async function generateCourse(topic: string, durationWeeks: number = 6) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/ai/v1/courses/generate", {
        method: "POST",
        body: JSON.stringify({
          topic,
          duration_weeks: durationWeeks,
        }),
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la génération du cours";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Récupérer un cours par son ID
   */
  async function getCourse(courseId: string) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch(`/api/ai/v1/courses/${courseId}`, {
        method: "GET",
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la récupération du cours";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Rechercher des cours
   */
  async function searchCourses(tags?: string, niveau?: string) {
    isLoading.value = true;
    error.value = null;

    try {
      const params = new URLSearchParams();
      if (tags)
        params.append("tags", tags);
      if (niveau)
        params.append("niveau", niveau);

      const data = await apiFetch(`/api/ai/v1/courses?${params.toString()}`, {
        method: "GET",
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la recherche de cours";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  // ==================== PROGRESSION ====================

  /**
   * Récupérer toutes les progressions de l'utilisateur
   */
  async function getAllProgressions() {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/ai/v1/progression", {
        method: "GET",
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la récupération des progressions";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Mettre à jour la progression d'un module
   */
  async function updateModuleProgress(request: ProgressUpdateRequest) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/profile/v1/roadmap/progress/module", {
        method: "POST",
        body: JSON.stringify(request),
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la mise à jour de la progression";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  // ==================== COMPLÉTION ====================

  /**
   * Compléter une leçon
   */
  async function completeLesson(request: LessonCompleteRequest) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/profile/v1/roadmap/complete/lesson", {
        method: "POST",
        body: JSON.stringify(request),
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la complétion de la leçon";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Compléter un module
   */
  async function completeModule(courseId: string, request: ModuleCompleteRequest) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch(`/api/ai/v1/progression/${courseId}/module/complete`, {
        method: "POST",
        body: JSON.stringify(request),
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la complétion du module";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Compléter une leçon (version AI)
   */
  async function completeLessonAI(courseId: string, request: { lesson_id: string; time_spent_minutes: number }) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch(`/api/ai/v1/progression/${courseId}/lesson/complete`, {
        method: "POST",
        body: JSON.stringify(request),
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la complétion de la leçon";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  // ==================== NOTES ====================

  /**
   * Ajouter une note
   */
  async function addNote(request: NoteRequest) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/profile/v1/roadmap/notes/add", {
        method: "POST",
        body: JSON.stringify(request),
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de l'ajout de la note";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  // ==================== PROJETS ====================

  /**
   * Soumettre un projet
   */
  async function submitProject(request: ProjectRequest) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/profile/v1/roadmap/projects/submit", {
        method: "POST",
        body: JSON.stringify(request),
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la soumission du projet";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  // ==================== STATISTIQUES ====================

  /**
   * Récupérer les statistiques de l'utilisateur
   */
  async function getStatistics() {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/profile/v1/roadmap/statistics", {
        method: "GET",
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la récupération des statistiques";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  // ==================== LEARNING PATH ====================

  /**
   * Récupérer le parcours d'apprentissage
   */
  async function getLearningPath() {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch("/api/ai/v1/learning-path", {
        method: "GET",
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la récupération du parcours";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Compléter une quête
   */
  async function completeQuest(questId: string, xpEarned: number = 100) {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch(`/api/ai/v1/learning-path/quest/${questId}/complete?xp_earned=${xpEarned}`, {
        method: "POST",
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la complétion de la quête";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  // ==================== RESSOURCES ====================

  /**
   * Recommander des ressources
   */
  async function recommendResources(topic: string, resourceType: string = "all") {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await apiFetch(`/api/ai/v1/resources/recommend?topic=${encodeURIComponent(topic)}&resource_type=${resourceType}`, {
        method: "GET",
      });

      return {
        success: true,
        data,
      };
    }
    catch (err: any) {
      error.value = err.data?.detail || "Erreur lors de la recommandation de ressources";
      return {
        success: false,
        error: error.value,
      };
    }
    finally {
      isLoading.value = false;
    }
  }

  return {
    isLoading,
    error,

    // Roadmap
    generateRoadmap,
    getActiveRoadmap,
    getCourseProgression,

    // Cours AI
    generateCourse,
    getCourse,
    searchCourses,

    // Progression
    getAllProgressions,
    updateModuleProgress,

    // Complétion
    completeLesson,
    completeModule,
    completeLessonAI,

    // Notes et Projets
    addNote,
    submitProject,

    // Statistiques
    getStatistics,

    // Learning Path
    getLearningPath,
    completeQuest,

    // Ressources
    recommendResources,
  };
}
