import type { Ref } from "vue";

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  intention?: Record<string, any>;
};

export type ChatResponse = {
  response: string;
  intention: Record<string, any>;
  conversation_id: string;
  timestamp: string;
  suggestions: string[];
};

export function useAiTutor() {
  const api = useApi();
  const chatHistory = useState<ChatMessage[]>("chatMessages", () => []);
  const sessionId = useState<string | null>("chatSessionId", () => null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Envoyer un message au chatbot
   */
  async function sendMessage(message: string): Promise<ChatResponse | null> {
    if (!message.trim()) {
      error.value = "Le message ne peut pas être vide";
      return null;
    }

    isLoading.value = true;
    error.value = null;

    try {
      // Ajouter le message utilisateur localement
      const userMessage: ChatMessage = {
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
      };
      chatHistory.value.push(userMessage);

      // Appeler l'API avec la bonne méthode
      const response = await api.ai.chat(message, sessionId.value || undefined);

      if (!response) {
        throw new Error("Aucune réponse du serveur");
      }

      // Mettre à jour le sessionId
      if (response.conversation_id) {
        sessionId.value = response.conversation_id;
      }

      // Ajouter la réponse du bot
      const botMessage: ChatMessage = {
        role: "assistant",
        content: response.response,
        timestamp: response.timestamp,
        intention: response.intention,
      };
      chatHistory.value.push(botMessage);

      return response;
    }
    catch (e: any) {
      error.value = e?.message || "Erreur lors de l'envoi du message";
      console.error("Erreur chat:", e);
      // Retirer le message utilisateur en cas d'erreur
      chatHistory.value.pop();
      return null;
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Charger l'historique des conversations
   */
  async function loadHistory(limit = 50) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.ai.getChatHistory(sessionId.value || undefined, limit);

      if (!response) {
        throw new Error("Aucune réponse du serveur");
      }

      // Charger les messages depuis la conversation
      if (response.conversations && response.conversations.length > 0) {
        const conversation = response.conversations[0];
        chatHistory.value = conversation.messages || [];
        sessionId.value = conversation.session_id;
      }
    }
    catch (e: any) {
      error.value = e?.message || "Erreur lors du chargement de l'historique";
      console.error("Erreur historique:", e);
    }
    finally {
      isLoading.value = false;
    }
  }

  /**
   * Réinitialiser la conversation
   */
  function resetConversation() {
    chatHistory.value = [];
    sessionId.value = null;
    error.value = null;
  }

  return {
    chatHistory: readonly(chatHistory) as Readonly<Ref<ChatMessage[]>>,
    sessionId: readonly(sessionId) as Readonly<Ref<string | null>>,
    isLoading: readonly(isLoading),
    error: readonly(error),
    sendMessage,
    loadHistory,
    resetConversation,
  };
}
