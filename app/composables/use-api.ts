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
      // GET /api/profile/v1/ ou /api/profile/v1/me
      getMyProfile: async () => {
        return await apiFetch("/api/profile/v1/me", {
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
  };
}
