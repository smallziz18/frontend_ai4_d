/**
 * Composable pour gérer les agents IA multi-tâches
 * Correspond aux routes /api/ai/v1/agents/*
 */
export function useAiAgents() {
  const api = useApi();

  // État de la session agent en cours
  const currentSession = ref<{
    task_id: string | null;
    agent_type: string | null;
    status: string | null;
    result: any | null;
    error: string | null;
  }>({
    task_id: null,
    agent_type: null,
    status: null,
    result: null,
    error: null,
  });

  const isProcessing = computed(() => currentSession.value.status === "PENDING" || currentSession.value.status === "STARTED");

  /**
   * Démarre une session d'agent asynchrone
   * @param agentType - Type d'agent: "chatbot", "course", "module"
   * @param params - Paramètres spécifiques à l'agent
   */
  async function startAgentSession(agentType: string, params: Record<string, any> = {}) {
    try {
      const response = await api.ai.startAgentTask(agentType, params);

      currentSession.value = {
        task_id: response.task_id,
        agent_type: agentType,
        status: response.status,
        result: null,
        error: null,
      };

      return response;
    }
    catch (error: any) {
      currentSession.value.error = error?.message || "Erreur lors du démarrage de l'agent";
      throw error;
    }
  }

  /**
   * Vérifie le statut d'une tâche agent
   * @param taskId - ID de la tâche
   */
  async function checkAgentStatus(taskId: string) {
    try {
      const response = await api.ai.getAgentTaskStatus(taskId);

      currentSession.value.status = response.state || response.status;

      if (response.result) {
        currentSession.value.result = response.result;
      }

      if (response.error) {
        currentSession.value.error = response.error;
      }

      return response;
    }
    catch (error: any) {
      currentSession.value.error = error?.message || "Erreur lors de la vérification du statut";
      throw error;
    }
  }

  /**
   * Polling automatique d'une tâche jusqu'à complétion
   * @param taskId - ID de la tâche
   * @param onProgress - Callback appelé à chaque poll
   * @param maxAttempts - Nombre maximal de tentatives
   * @param intervalMs - Intervalle entre les polls en ms
   */
  async function pollAgentTask(
    taskId: string,
    onProgress?: (status: any) => void,
    maxAttempts: number = 60,
    intervalMs: number = 2000,
  ) {
    let attempts = 0;

    return new Promise((resolve, reject) => {
      const intervalId = setInterval(async () => {
        attempts++;

        try {
          const status = await checkAgentStatus(taskId);

          if (onProgress) {
            onProgress(status);
          }

          // États terminaux
          if (status.state === "SUCCESS" || status.status === "success") {
            clearInterval(intervalId);
            resolve(status.result);
          }
          else if (status.state === "FAILURE" || status.status === "failed") {
            clearInterval(intervalId);
            reject(new Error(status.error || "Tâche échouée"));
          }
          else if (attempts >= maxAttempts) {
            clearInterval(intervalId);
            reject(new Error("Timeout: tâche non terminée après max tentatives"));
          }
        }
        catch (error) {
          clearInterval(intervalId);
          reject(error);
        }
      }, intervalMs);
    });
  }

  /**
   * Reset la session en cours
   */
  function resetSession() {
    currentSession.value = {
      task_id: null,
      agent_type: null,
      status: null,
      result: null,
      error: null,
    };
  }

  // Chat avec l'IA
  const chatHistory = ref<Array<{
    role: "user" | "assistant";
    content: string;
    timestamp: string;
  }>>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  async function sendChatMessage(message: string, sessionId?: string) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.ai.chat(message, sessionId);

      chatHistory.value.push(
        {
          role: "user",
          content: message,
          timestamp: new Date().toISOString(),
        },
        {
          role: "assistant",
          content: response.response,
          timestamp: response.timestamp,
        },
      );

      return response;
    }
    catch (e: any) {
      error.value = e?.message || "Erreur lors de l'envoi du message";
      throw e;
    }
    finally {
      isLoading.value = false;
    }
  }

  async function loadChatHistory(sessionId?: string, limit: number = 50) {
    isLoading.value = true;
    error.value = null;

    try {
      const history = await api.ai.getChatHistory(sessionId, limit);
      if (history?.conversation && Array.isArray(history.conversation.messages)) {
        chatHistory.value = history.conversation.messages;
      }
      else if (history?.conversations && Array.isArray(history.conversations)) {
        // Merge all conversations
        chatHistory.value = history.conversations.flatMap((conv: any) => conv.messages || []);
      }
      else {
        // Aucun historique, initialiser à un tableau vide
        chatHistory.value = [];
      }
      return history;
    }
    catch (e: any) {
      error.value = e?.message || "Erreur lors du chargement de l'historique";
      console.error("Erreur loadChatHistory:", e);
      // Initialiser à un tableau vide en cas d'erreur
      chatHistory.value = [];
      // Ne pas throw, juste log l'erreur
      return null;
    }
    finally {
      isLoading.value = false;
    }
  }

  // Génération de cours
  async function generateCourse(topic: string, durationWeeks: number = 6) {
    return await api.ai.generateCourseRoadmap(topic, durationWeeks);
  }

  async function getCourse(courseId: string) {
    return await api.ai.getCourse(courseId);
  }

  async function searchCourses(tags?: string, niveau?: string) {
    return await api.ai.searchCourses(tags, niveau);
  }

  // Progression
  async function getAllProgressions() {
    return await api.ai.getAllProgressions();
  }

  async function completeModule(courseId: string, moduleId: string, score: number, timeSpent: number) {
    return await api.ai.completeModule(courseId, moduleId, score, timeSpent);
  }

  async function completeLesson(courseId: string, lessonId: string, timeSpent: number) {
    return await api.ai.completeLesson(courseId, lessonId, timeSpent);
  }

  // Learning path
  async function getLearningPath() {
    return await api.ai.getLearningPath();
  }

  async function completeQuest(questId: string, xpEarned: number = 100) {
    return await api.ai.completeQuest(questId, xpEarned);
  }

  // Ressources
  async function recommendResources(topic: string, resourceType: string = "all") {
    return await api.ai.recommendResources(topic, resourceType);
  }

  return {
    // Session state
    currentSession: readonly(currentSession),
    isProcessing,

    // Session management
    startAgentSession,
    checkAgentStatus,
    pollAgentTask,
    resetSession,

    // Chat
    chatHistory: readonly(chatHistory),
    isLoading: readonly(isLoading),
    error: readonly(error),
    sendChatMessage,
    loadChatHistory,

    // Courses
    generateCourse,
    getCourse,
    searchCourses,

    // Progression
    getAllProgressions,
    completeModule,
    completeLesson,

    // Learning path
    getLearningPath,
    completeQuest,

    // Resources
    recommendResources,
  };
}
