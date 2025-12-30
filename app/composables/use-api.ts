// Composable centralisé pour gérer tous les appels API selon l'OpenAPI spec
export function useApi() {
  const config = useRuntimeConfig();
  const baseURL = config.public.apiBase || "http://127.0.0.1:8000";

  // Helper pour les appels API avec authentification
  const apiFetch = async <T>(endpoint: string, options: any = {}): Promise<T> => {
    const accessToken = useCookie("access_token").value;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (accessToken && options.auth !== false) {
      headers.Authorization = `Bearer ${accessToken}`;
    }

    return await $fetch<T>(`${baseURL}${endpoint}`, {
      ...options,
      headers,
    });
  };

  return {
    // ============== AUTH ENDPOINTS ==============
    auth: {
      // POST /api/auth/v1/signup
      signup: async (data: any) => {
        return await apiFetch("/api/auth/v1/signup", {
          method: "POST",
          body: data,
          auth: false,
        });
      },

      // POST /api/auth/v1/login
      login: async (email: string, password: string) => {
        return await apiFetch<{
          message: string;
          access_token: string;
          refresh_token: string;
          user: {
            id: string;
            username: string;
            email: string;
          };
        }>("/api/auth/v1/login", {
          method: "POST",
          body: { email, password },
          auth: false,
        });
      },

      // GET /api/auth/v1/logout
      logout: async () => {
        return await apiFetch("/api/auth/v1/logout", {
          method: "GET",
        });
      },

      // GET /api/auth/v1/me
      getCurrentUser: async () => {
        return await apiFetch("/api/auth/v1/me", {
          method: "GET",
        });
      },

      // GET /api/auth/v1/verify/{token}
      verifyEmail: async (token: string) => {
        return await apiFetch(`/api/auth/v1/verify/${token}`, {
          method: "GET",
          auth: false,
        });
      },

      // POST /api/auth/v1/resend_verification
      resendVerification: async (email: string) => {
        return await apiFetch("/api/auth/v1/resend_verification", {
          method: "POST",
          body: { mails: [email], subject: "Verification Email", body: "" },
          auth: false,
        });
      },

      // GET /api/auth/v1/refresh_token
      refreshToken: async () => {
        const refreshToken = useCookie("refresh_token").value;
        return await apiFetch("/api/auth/v1/refresh_token", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${refreshToken}`,
          },
          auth: false,
        });
      },

      // POST /api/auth/v1/password_reset_request
      passwordResetRequest: async (email: string) => {
        return await apiFetch("/api/auth/v1/password_reset_request", {
          method: "POST",
          body: { email },
          auth: false,
        });
      },

      // POST /api/auth/v1/password_reset_confirm/{token}
      passwordResetConfirm: async (token: string, newPassword: string, confirmPassword: string) => {
        return await apiFetch(`/api/auth/v1/password_reset_confirm/${token}`, {
          method: "POST",
          body: {
            new_password: newPassword,
            confirm_new_password: confirmPassword,
          },
          auth: false,
        });
      },
    },

    // ============== PROFILE ENDPOINTS ==============
    profile: {
      // GET /api/profile/v1/me ou /api/profile/v1/me
      getMyProfile: async () => {
        return await apiFetch("/api/profile/v1/me", {
          method: "GET",
        });
      },

      // GET /api/profile/v1/has-profile
      hasProfile: async () => {
        return await apiFetch<{
          has_profile: boolean;
          questionnaire_completed: boolean;
        }>("/api/profile/v1/has-profile", {
          method: "GET",
        });
      },

      // POST /api/profile/v1/
      createProfile: async (data: any) => {
        return await apiFetch("/api/profile/v1/", {
          method: "POST",
          body: data,
        });
      },

      // PUT /api/profile/v1/
      updateProfile: async (data: any) => {
        return await apiFetch("/api/profile/v1/", {
          method: "PUT",
          body: data,
        });
      },

      // DELETE /api/profile/v1/
      deleteProfile: async () => {
        return await apiFetch("/api/profile/v1/", {
          method: "DELETE",
        });
      },

      // POST /api/profile/v1/xp
      addXP: async (xpPoints: number) => {
        return await apiFetch("/api/profile/v1/xp", {
          method: "POST",
          body: { xp_points: xpPoints },
        });
      },

      // GET /api/profile/v1/stats
      getStats: async () => {
        return await apiFetch("/api/profile/v1/stats", {
          method: "GET",
        });
      },

      // GET /api/profile/v1/recommendations
      getRecommendations: async () => {
        return await apiFetch("/api/profile/v1/recommendations", {
          method: "GET",
        });
      },

      // GET /api/profile/v1/leaderboard
      getLeaderboard: async (limit: number = 10) => {
        return await apiFetch(`/api/profile/v1/leaderboard?limit=${limit}`, {
          method: "GET",
        });
      },

      // GET /api/profile/v1/activities
      getActivities: async (limit: number = 50) => {
        return await apiFetch(`/api/profile/v1/activities?limit=${limit}`, {
          method: "GET",
        });
      },

      // POST /api/profile/v1/activities
      completeActivity: async (activityType: string, xpReward: number = 0) => {
        return await apiFetch("/api/profile/v1/activities", {
          method: "POST",
          body: {
            activity_type: activityType,
            xp_reward: xpReward,
          },
        });
      },

      // POST /api/profile/v1/badges
      addBadge: async (badge: string) => {
        return await apiFetch("/api/profile/v1/badges", {
          method: "POST",
          body: { badge },
        });
      },
    },

    // ============== QUESTIONNAIRE & ANALYSIS ENDPOINTS ==============
    questionnaire: {
      // GET /api/profile/v1/question
      generateQuestions: async () => {
        return await apiFetch<{ task_id: string }>("/api/profile/v1/question", {
          method: "GET",
        });
      },

      // GET /api/profile/v1/question_result/{task_id}
      getQuestionResult: async (taskId: string) => {
        return await apiFetch(`/api/profile/v1/question_result/${taskId}`, {
          method: "GET",
        });
      },

      // POST /api/profile/v1/analyze_quiz
      analyzeQuiz: async (evaluation: any) => {
        return await apiFetch<{ task_id: string }>("/api/profile/v1/analyze_quiz", {
          method: "POST",
          body: evaluation,
        });
      },

      // GET /api/profile/v1/analysis_result/{task_id}
      getAnalysisResult: async (taskId: string) => {
        return await apiFetch(`/api/profile/v1/analysis_result/${taskId}`, {
          method: "GET",
        });
      },
    },

    // ============== QUESTIONNAIRE V2 (LangGraph Multi-Agents) ==============
    questionnaireV2: {
      // POST /api/profile/v1/v2/generate-questions
      generateQuestions: async () => {
        return await apiFetch<{
          session_id: string;
          questions: Array<{
            numero: number;
            question: string;
            type: string;
            options?: string[];
            correction: string;
          }>;
          profiler_analysis: {
            niveau_estime: number;
            style_apprentissage: string;
            motivation: string;
          };
          timestamp: string;
        }>("/api/profile/v1/v2/generate-questions", {
          method: "POST",
        });
      },

      // POST /api/profile/v1/v2/submit-responses
      submitResponses: async (sessionId: string, responses: Array<{
        numero: number;
        reponse: string;
        type: string;
      }>) => {
        return await apiFetch<{
          session_id: string;
          niveau_final: number;
          evaluation: {
            score_total: number;
            score_percentage: number;
            details_par_question: any[];
          };
          parcours_apprentissage: {
            titre: string;
            duree_estimee: string;
            quetes_principales: any[];
            boss_fights: any[];
          };
          tutorials: any[];
          gamification: {
            badges_earned: string[];
            xp_gained: number;
            level_up: boolean;
          };
          recommendations: string[];
          timestamp: string;
        }>("/api/profile/v1/v2/submit-responses", {
          method: "POST",
          body: { session_id: sessionId, responses },
        });
      },

      // GET /api/profile/v1/v2/learning-path
      getLearningPath: async () => {
        return await apiFetch("/api/profile/v1/v2/learning-path", {
          method: "GET",
        });
      },

      // GET /api/profile/v1/v2/workflow-state/{session_id}
      getWorkflowState: async (sessionId: string) => {
        return await apiFetch(`/api/profile/v1/v2/workflow-state/${sessionId}`, {
          method: "GET",
        });
      },
    },

    // ============== GAMIFICATION ENDPOINTS ==============
    gamification: {
      // GET /api/profile/v1/gamification/badges
      getAvailableBadges: async () => {
        return await apiFetch("/api/profile/v1/gamification/badges", {
          method: "GET",
        });
      },

      // GET /api/profile/v1/gamification/my-badges
      getMyBadges: async () => {
        return await apiFetch("/api/profile/v1/gamification/my-badges", {
          method: "GET",
        });
      },

      // GET /api/profile/v1/gamification/streak
      getStreak: async () => {
        return await apiFetch("/api/profile/v1/gamification/streak", {
          method: "GET",
        });
      },

      // GET /api/profile/v1/gamification/progression
      getProgression: async () => {
        return await apiFetch("/api/profile/v1/gamification/progression", {
          method: "GET",
        });
      },

      // GET /api/profile/v1/gamification/leaderboard-enriched
      getEnrichedLeaderboard: async (limit: number = 10) => {
        return await apiFetch(`/api/profile/v1/gamification/leaderboard-enriched?limit=${limit}`, {
          method: "GET",
        });
      },

      // GET /api/profile/v1/gamification/dashboard
      getDashboard: async () => {
        return await apiFetch("/api/profile/v1/gamification/dashboard", {
          method: "GET",
        });
      },
    },

    // ============== UTILITY ENDPOINTS ==============
    utils: {
      // GET /api/profile/v1/healthcheck
      healthCheck: async () => {
        return await apiFetch("/api/profile/v1/healthcheck", {
          method: "GET",
          auth: false,
        });
      },

      // GET /api/profile/v1/debug-token-detailed
      debugToken: async () => {
        return await apiFetch("/api/profile/v1/debug-token-detailed", {
          method: "GET",
        });
      },
    },

    // ============== AI AGENTS ENDPOINTS ==============
    ai: {
      // POST /api/ai/v1/agents/start - Démarrer une tâche agent asynchrone
      startAgentTask: async (agentType: string, params: Record<string, any> = {}) => {
        return await apiFetch<{
          task_id: string;
          status: string;
          agent_type: string;
          message: string;
        }>("/api/ai/v1/agents/start", {
          method: "POST",
          body: {
            agent_type: agentType,
            params,
          },
        });
      },

      // GET /api/ai/v1/agents/status/{task_id} - Vérifier le statut d'une tâche
      getAgentTaskStatus: async (taskId: string) => {
        return await apiFetch<{
          task_id: string;
          state: string;
          status: string;
          result?: any;
          error?: string;
          progress?: number;
        }>(`/api/ai/v1/agents/status/${taskId}`, {
          method: "GET",
        });
      },

      // POST /api/ai/v1/chat - Chat avec le bot IA
      chat: async (message: string, sessionId?: string) => {
        return await apiFetch<{
          response: string;
          intention: Record<string, any>;
          conversation_id: string;
          timestamp: string;
          suggestions: string[];
        }>("/api/ai/v1/chat", {
          method: "POST",
          body: {
            message,
            session_id: sessionId,
          },
        });
      },

      // GET /api/ai/v1/chat/history - Historique des conversations
      getChatHistory: async (sessionId?: string, limit: number = 50) => {
        const params = new URLSearchParams();
        if (sessionId)
          params.append("session_id", sessionId);
        params.append("limit", limit.toString());

        return await apiFetch(`/api/ai/v1/chat/history?${params.toString()}`, {
          method: "GET",
        });
      },

      // POST /api/ai/v1/courses/generate - Générer une roadmap de cours
      generateCourseRoadmap: async (topic: string, durationWeeks: number = 6) => {
        return await apiFetch<{
          message: string;
          course_id: string;
          roadmap: any;
        }>("/api/ai/v1/courses/generate", {
          method: "POST",
          body: {
            topic,
            duration_weeks: durationWeeks,
          },
        });
      },

      // GET /api/ai/v1/courses/{course_id} - Récupérer un cours
      getCourse: async (courseId: string) => {
        return await apiFetch<{
          course: any;
          progression: any;
        }>(`/api/ai/v1/courses/${courseId}`, {
          method: "GET",
        });
      },

      // GET /api/ai/v1/courses - Rechercher des cours
      searchCourses: async (tags?: string, niveau?: string) => {
        const params = new URLSearchParams();
        if (tags)
          params.append("tags", tags);
        if (niveau)
          params.append("niveau", niveau);

        return await apiFetch<{
          courses: any[];
        }>(`/api/ai/v1/courses?${params.toString()}`, {
          method: "GET",
        });
      },

      // GET /api/ai/v1/progression - Toutes les progressions
      getAllProgressions: async () => {
        return await apiFetch<{
          progressions: any[];
        }>("/api/ai/v1/progression", {
          method: "GET",
        });
      },

      // POST /api/ai/v1/progression/{course_id}/module/complete - Compléter un module
      completeModule: async (courseId: string, moduleId: string, evaluationScore: number, timeSpentMinutes: number) => {
        return await apiFetch(`/api/ai/v1/progression/${courseId}/module/complete`, {
          method: "POST",
          body: {
            module_id: moduleId,
            evaluation_score: evaluationScore,
            time_spent_minutes: timeSpentMinutes,
          },
        });
      },

      // POST /api/ai/v1/progression/{course_id}/lesson/complete - Compléter une leçon
      completeLesson: async (courseId: string, lessonId: string, timeSpentMinutes: number) => {
        return await apiFetch<{
          success: boolean;
          message: string;
        }>(`/api/ai/v1/progression/${courseId}/lesson/complete`, {
          method: "POST",
          body: {
            lesson_id: lessonId,
            time_spent_minutes: timeSpentMinutes,
          },
        });
      },

      // GET /api/ai/v1/learning-path - Parcours d'apprentissage
      getLearningPath: async () => {
        return await apiFetch<{
          learning_path: any;
        }>("/api/ai/v1/learning-path", {
          method: "GET",
        });
      },

      // POST /api/ai/v1/learning-path/quest/{quest_id}/complete - Compléter une quête
      completeQuest: async (questId: string, xpEarned: number = 100) => {
        return await apiFetch<{
          success: boolean;
          xp_earned: number;
          message: string;
        }>(`/api/ai/v1/learning-path/quest/${questId}/complete?xp_earned=${xpEarned}`, {
          method: "POST",
        });
      },

      // GET /api/ai/v1/resources/recommend - Recommander des ressources
      recommendResources: async (topic: string, resourceType: string = "all") => {
        return await apiFetch<{
          topic: string;
          user_level: number;
          resources: any[];
        }>(`/api/ai/v1/resources/recommend?topic=${encodeURIComponent(topic)}&resource_type=${resourceType}`, {
          method: "GET",
        });
      },
    },

    // ============== AI REALTIME ENDPOINTS (WebSocket + Streaming) ==============
    aiRealtime: {
      // POST /api/ai/v1/realtime/chat/start - Démarrer chat asynchrone
      startChatAsync: async (message: string, sessionId?: string) => {
        const params = new URLSearchParams();
        params.append("message", message);
        if (sessionId)
          params.append("session_id", sessionId);

        return await apiFetch<{
          task_id: string;
          status: string;
          session_id: string;
          estimated_time_seconds: number;
          poll_url: string;
          websocket_url: string;
        }>(`/api/ai/v1/realtime/chat/start?${params.toString()}`, {
          method: "POST",
        });
      },

      // GET /api/ai/v1/realtime/connections - Connexions actives (monitoring)
      getActiveConnections: async () => {
        return await apiFetch<{
          active_connections: number;
          connections: string[];
        }>("/api/ai/v1/realtime/connections", {
          method: "GET",
        });
      },

      // POST /api/ai/v1/realtime/broadcast - Broadcast message
      broadcastMessage: async (message: string) => {
        return await apiFetch<{
          message: string;
          broadcast_to: number;
        }>(`/api/ai/v1/realtime/broadcast?message=${encodeURIComponent(message)}`, {
          method: "POST",
        });
      },

      // WebSocket connection helper
      connectWebSocket: (userId: string) => {
        const wsUrl = `${baseURL.replace("http", "ws")}/api/ai/v1/realtime/chat/${userId}`;
        return new WebSocket(wsUrl);
      },
    },

    // Raw apiFetch pour custom requests
    apiFetch,
  };
}

// Type exports pour TypeScript
export type ApiClient = ReturnType<typeof useApi>;
