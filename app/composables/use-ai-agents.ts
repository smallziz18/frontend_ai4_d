type AgentSession = {
  session_id: string;
  user_id: string;
  agent_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
};

type ConversationMessage = {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
};

export function useAiAgents() {
  // État
  const currentSession = ref<AgentSession | null>(null);
  const sessionHistory = ref<ConversationMessage[]>([]);
  const isLoading = ref(false);
  const error = ref<string>("");

  // Lister tous les agents disponibles
  const listAgents = async () => {
    try {
      isLoading.value = true;
      error.value = "";
      const response = await $fetch("/api/v1/ai/agents/", {
        baseURL: useRuntimeConfig().public.apiBase,
      });
      return response;
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors de la récupération des agents";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  };

  // Démarrer une nouvelle session avec un agent
  const startSession = async () => {
    try {
      isLoading.value = true;
      error.value = "";
      const token = useCookie("access_token").value;

      const response = await $fetch("/api/v1/ai/agents/start", {
        method: "POST",
        baseURL: useRuntimeConfig().public.apiBase,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      currentSession.value = response as AgentSession;
      return response;
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors du démarrage de la session";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  };

  // Récupérer toutes les sessions de l'utilisateur
  const listSessions = async () => {
    try {
      isLoading.value = true;
      error.value = "";
      const token = useCookie("access_token").value;

      const response = await $fetch("/api/v1/ai/agents/sessions", {
        baseURL: useRuntimeConfig().public.apiBase,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return response;
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors de la récupération des sessions";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  };

  // Récupérer l'état d'une session spécifique
  const getSessionState = async (sessionId: string) => {
    try {
      isLoading.value = true;
      error.value = "";
      const token = useCookie("access_token").value;

      const response = await $fetch(`/api/v1/ai/agents/sessions/${sessionId}`, {
        baseURL: useRuntimeConfig().public.apiBase,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return response;
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors de la récupération de l'état";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  };

  // Supprimer une session
  const deleteSession = async (sessionId: string) => {
    try {
      isLoading.value = true;
      error.value = "";
      const token = useCookie("access_token").value;

      await $fetch(`/api/v1/ai/agents/sessions/${sessionId}`, {
        method: "DELETE",
        baseURL: useRuntimeConfig().public.apiBase,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (currentSession.value?.session_id === sessionId) {
        currentSession.value = null;
        sessionHistory.value = [];
      }
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors de la suppression de la session";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  };

  // Soumettre des réponses à une session
  const submitResponses = async (sessionId: string, responses: any[]) => {
    try {
      isLoading.value = true;
      error.value = "";
      const token = useCookie("access_token").value;

      const response = await $fetch(`/api/v1/ai/agents/sessions/${sessionId}/responses`, {
        method: "POST",
        baseURL: useRuntimeConfig().public.apiBase,
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: responses,
      });

      return response;
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors de la soumission des réponses";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  };

  // Récupérer l'historique de conversation
  const getConversationHistory = async (sessionId: string) => {
    try {
      isLoading.value = true;
      error.value = "";
      const token = useCookie("access_token").value;

      const response = await $fetch(`/api/v1/ai/agents/sessions/${sessionId}/history`, {
        baseURL: useRuntimeConfig().public.apiBase,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      sessionHistory.value = response as ConversationMessage[];
      return response;
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors de la récupération de l'historique";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  };

  // Envoyer un message dans une session
  const sendMessage = async (sessionId: string, content: string) => {
    try {
      isLoading.value = true;
      error.value = "";
      const token = useCookie("access_token").value;

      const response = await $fetch(`/api/v1/ai/agents/sessions/${sessionId}/message`, {
        method: "POST",
        baseURL: useRuntimeConfig().public.apiBase,
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: { content },
      });

      // Ajouter le message à l'historique local
      sessionHistory.value.push({
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      });

      return response;
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors de l'envoi du message";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  };

  // Récupérer le résumé d'une session
  const getSessionSummary = async (sessionId: string) => {
    try {
      isLoading.value = true;
      error.value = "";
      const token = useCookie("access_token").value;

      const response = await $fetch(`/api/v1/ai/agents/sessions/${sessionId}/summary`, {
        baseURL: useRuntimeConfig().public.apiBase,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return response;
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors de la récupération du résumé";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  };

  return {
    // État
    currentSession,
    sessionHistory,
    isLoading,
    error,

    // Méthodes
    listAgents,
    startSession,
    listSessions,
    getSessionState,
    deleteSession,
    submitResponses,
    getConversationHistory,
    sendMessage,
    getSessionSummary,
  };
}
