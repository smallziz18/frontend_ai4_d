<script setup lang="ts">
import { useAiAgents } from "~/composables/use-ai-agents";
import { useAuth } from "~/data/use-auth";

definePageMeta({
  middleware: ["auth"],
});

const { user } = useAuth();
const {
  currentSession,
  sessionHistory,
  isLoading,
  error,
  startSession,
  sendMessage,
  getConversationHistory,
} = useAiAgents();

const messageInput = ref("");
const chatContainer = ref<HTMLElement | null>(null);
const isInitializing = ref(false);

// Initialiser la session au montage
onMounted(async () => {
  isInitializing.value = true;
  try {
    await startSession();
    if (currentSession.value) {
      await getConversationHistory(currentSession.value.session_id);
    }
  }
  catch (e) {
    console.error("Erreur initialisation:", e);
  }
  finally {
    isInitializing.value = false;
  }
});

// Envoyer un message
async function handleSendMessage() {
  if (!messageInput.value.trim() || !currentSession.value)
    return;

  const message = messageInput.value.trim();
  messageInput.value = "";

  try {
    const response = await sendMessage(currentSession.value.session_id, message);

    // Ajouter la réponse de l'assistant
    if (response?.message) {
      sessionHistory.value.push({
        role: "assistant",
        content: response.message,
        timestamp: new Date().toISOString(),
      });
    }

    // Scroller en bas
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    });
  }
  catch (e) {
    console.error("Erreur envoi message:", e);
  }
}

// Gérer la touche Entrée
function handleKeyPress(event: KeyboardEvent) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleSendMessage();
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary/5 via-background-light to-secondary/5 dark:from-primary/10 dark:via-background-dark dark:to-secondary/10">
    <!-- Navbar -->
    <div class="navbar bg-base-100/80 backdrop-blur-sm shadow-sm">
      <div class="flex-1">
        <NuxtLink to="/dashboard" class="btn btn-ghost normal-case text-xl">
          <Icon name="tabler:arrow-left" size="24" />
          Retour au Dashboard
        </NuxtLink>
      </div>
      <div class="flex-none gap-2">
        <ThemeToggle />
        <div class="flex items-center gap-2">
          <Icon
            name="tabler:robot"
            size="24"
            class="text-primary"
          />
          <span class="font-semibold">AI Tutor</span>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- Header -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <h1 class="card-title text-3xl">
            <Icon
              name="tabler:message-chatbot"
              size="36"
              class="text-primary"
            />
            Chat avec votre Tuteur AI
          </h1>
          <p class="text-sm opacity-70">
            Posez vos questions et obtenez des réponses personnalisées instantanément
          </p>
        </div>
      </div>

      <!-- Error -->
      <alert-message
        v-if="error"
        type="error"
        :message="error"
        :dismissible="true"
        class="mb-4"
        @dismiss="error = ''"
      />

      <!-- Loading Initial -->
      <div v-if="isInitializing" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <loading-spinner message="Initialisation du tuteur AI..." />
        </div>
      </div>

      <!-- Chat Container -->
      <div v-else class="card bg-base-100 shadow-xl">
        <div class="card-body p-0">
          <!-- Messages -->
          <div
            ref="chatContainer"
            class="overflow-y-auto h-[500px] p-6 space-y-4"
          >
            <!-- Welcome Message -->
            <div v-if="sessionHistory.length === 0" class="text-center py-12">
              <Icon
                name="tabler:message-circle-2"
                size="64"
                class="mx-auto text-primary opacity-50 mb-4"
              />
              <h3 class="text-xl font-semibold mb-2">
                Bienvenue, {{ user?.username }} !
              </h3>
              <p class="opacity-70">
                Je suis votre tuteur AI. Posez-moi n'importe quelle question sur vos cours !
              </p>
            </div>

            <!-- Messages History -->
            <div
              v-for="(msg, idx) in sessionHistory"
              :key="idx"
              class="chat"
              :class="msg.role === 'user' ? 'chat-end' : 'chat-start'"
            >
              <div class="chat-image avatar">
                <div class="w-10 rounded-full">
                  <div
                    class="w-full h-full flex items-center justify-center"
                    :class="msg.role === 'user' ? 'bg-primary' : 'bg-secondary'"
                  >
                    <Icon
                      :name="msg.role === 'user' ? 'tabler:user' : 'tabler:robot'"
                      size="24"
                      class="text-white"
                    />
                  </div>
                </div>
              </div>
              <div class="chat-header mb-1">
                {{ msg.role === "user" ? user?.username : "AI Tutor" }}
                <time class="text-xs opacity-50 ml-2">
                  {{ new Date(msg.timestamp).toLocaleTimeString() }}
                </time>
              </div>
              <div
                class="chat-bubble"
                :class="msg.role === 'user' ? 'chat-bubble-primary' : 'chat-bubble-secondary'"
              >
                {{ msg.content }}
              </div>
            </div>

            <!-- Loading indicator -->
            <div v-if="isLoading" class="chat chat-start">
              <div class="chat-image avatar">
                <div class="w-10 rounded-full bg-secondary flex items-center justify-center">
                  <Icon
                    name="tabler:robot"
                    size="24"
                    class="text-white"
                  />
                </div>
              </div>
              <div class="chat-bubble chat-bubble-secondary">
                <span class="loading loading-dots loading-sm" />
              </div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="border-t border-base-300 p-4">
            <div class="flex gap-2">
              <textarea
                v-model="messageInput"
                placeholder="Tapez votre message..."
                class="textarea textarea-bordered flex-1 resize-none"
                rows="2"
                :disabled="isLoading || !currentSession"
                @keypress="handleKeyPress"
              />
              <button
                class="btn btn-primary btn-square"
                :disabled="!messageInput.trim() || isLoading || !currentSession"
                @click="handleSendMessage"
              >
                <Icon name="tabler:send" size="24" />
              </button>
            </div>
            <p class="text-xs opacity-50 mt-2">
              Appuyez sur Entrée pour envoyer, Shift+Entrée pour une nouvelle ligne
            </p>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <button class="btn btn-outline">
          <Icon name="tabler:lightbulb" size="20" />
          Suggestions
        </button>
        <button class="btn btn-outline">
          <Icon name="tabler:history" size="20" />
          Historique
        </button>
        <button class="btn btn-outline">
          <Icon name="tabler:download" size="20" />
          Exporter
        </button>
      </div>
    </div>
  </div>
</template>
