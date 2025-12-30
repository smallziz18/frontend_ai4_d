<script setup lang="ts">
import { useAiAgents } from "~/composables/use-ai-agents";
import { useAuth } from "~/data/use-auth";

definePageMeta({
  middleware: ["auth"],
});

const { user } = useAuth();
const {
  currentSession,
  isProcessing,
  chatHistory,
  sendChatMessage,
  loadChatHistory,
  generateCourse,
  searchCourses,
  getLearningPath,
} = useAiAgents();

// État de la page
const activeTab = ref<"chat" | "courses" | "learning-path">("chat");
const loading = ref(false);
const error = ref<string | null>(null);

// Chat
const chatMessage = ref("");
const chatSessionId = ref<string>("");

async function handleSendMessage() {
  if (!chatMessage.value.trim())
    return;

  loading.value = true;
  error.value = null;

  try {
    await sendChatMessage(chatMessage.value, chatSessionId.value || undefined);
    chatMessage.value = "";
  }
  catch (e: any) {
    error.value = e?.message || "Erreur lors de l'envoi du message";
  }
  finally {
    loading.value = false;
  }
}

// Cours
const courseTopic = ref("");
const courseDuration = ref(6);
const generatedCourse = ref<any>(null);
const availableCourses = ref<any[]>([]);

async function handleGenerateCourse() {
  if (!courseTopic.value.trim())
    return;

  loading.value = true;
  error.value = null;

  try {
    const response = await generateCourse(courseTopic.value, courseDuration.value);
    generatedCourse.value = response;
  }
  catch (e: any) {
    error.value = e?.message || "Erreur lors de la génération du cours";
  }
  finally {
    loading.value = false;
  }
}

async function handleSearchCourses() {
  loading.value = true;
  error.value = null;

  try {
    const response = await searchCourses();
    availableCourses.value = response.courses || [];
  }
  catch (e: any) {
    error.value = e?.message || "Erreur lors de la recherche de cours";
  }
  finally {
    loading.value = false;
  }
}

// Learning Path
const learningPath = ref<any>(null);

async function handleLoadLearningPath() {
  loading.value = true;
  error.value = null;

  try {
    const response = await getLearningPath();
    learningPath.value = response.learning_path;
  }
  catch (e: any) {
    error.value = e?.message || "Erreur lors du chargement du parcours";
  }
  finally {
    loading.value = false;
  }
}

onMounted(async () => {
  // Charger l'historique de chat par défaut
  try {
    await loadChatHistory();
  }
  catch {
    // Ignorer si pas d'historique
  }
});
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow">
      <div class="container mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold">
          🤖 Agents IA
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mt-2">
          Chatbot, générateur de cours, et parcours d'apprentissage personnalisés
        </p>

        <div v-if="user" class="mt-4 flex items-center gap-2 text-sm">
          <span class="font-medium">Connecté en tant que:</span>
          <span class="text-primary">{{ user.username }}</span>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="container mx-auto px-4 py-6">
      <div class="tabs tabs-boxed bg-base-200">
        <button
          class="tab"
          :class="{ 'tab-active': activeTab === 'chat' }"
          @click="activeTab = 'chat'"
        >
          💬 Chat
        </button>
        <button
          class="tab"
          :class="{ 'tab-active': activeTab === 'courses' }"
          @click="activeTab = 'courses'"
        >
          📚 Cours
        </button>
        <button
          class="tab"
          :class="{ 'tab-active': activeTab === 'learning-path' }"
          @click="activeTab = 'learning-path'"
        >
          🎯 Parcours
        </button>
      </div>

      <!-- Session Status -->
      <div v-if="currentSession.task_id" class="mt-4 alert alert-info">
        <div class="flex items-center gap-2">
          <span v-if="isProcessing" class="loading loading-spinner loading-sm" />
          <div>
            <div class="font-semibold">
              Session active: {{ currentSession.agent_type }}
            </div>
            <div class="text-sm">
              Statut: {{ currentSession.status }}
            </div>
          </div>
        </div>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="mt-4 alert alert-error">
        <span>{{ error }}</span>
      </div>

      <!-- Content -->
      <div class="mt-6">
        <!-- Chat Tab -->
        <div v-show="activeTab === 'chat'" class="space-y-6">
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title">
                💬 Chat avec votre Tuteur AI
              </h2>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Posez vos questions et obtenez des réponses personnalisées instantanément
              </p>

              <!-- Chat History -->
              <div class="mt-4 space-y-3 max-h-96 overflow-y-auto">
                <div
                  v-for="(msg, idx) in chatHistory"
                  :key="idx"
                  class="chat"
                  :class="msg.role === 'user' ? 'chat-end' : 'chat-start'"
                >
                  <div class="chat-bubble" :class="msg.role === 'user' ? 'chat-bubble-primary' : 'chat-bubble-secondary'">
                    {{ msg.content }}
                  </div>
                </div>

                <div v-if="chatHistory.length === 0" class="text-center text-gray-500 py-8">
                  <p>Bienvenue, {{ user?.username || "visiteur" }} !</p>
                  <p class="text-sm mt-2">
                    Je suis votre tuteur AI. Posez-moi n'importe quelle question sur vos cours !
                  </p>
                </div>
              </div>

              <!-- Chat Input -->
              <div class="mt-4 flex gap-2">
                <input
                  v-model="chatMessage"
                  type="text"
                  placeholder="Tapez votre message..."
                  class="input input-bordered flex-1"
                  :disabled="loading"
                  @keyup.enter="handleSendMessage"
                >
                <button
                  class="btn btn-primary"
                  :disabled="!chatMessage.trim() || loading"
                  @click="handleSendMessage"
                >
                  <span v-if="loading" class="loading loading-spinner loading-sm" />
                  <span v-else>Envoyer</span>
                </button>
              </div>

              <p class="text-xs text-gray-500 mt-2">
                Appuyez sur Entrée pour envoyer, Shift+Entrée pour une nouvelle ligne
              </p>
            </div>
          </div>
        </div>

        <!-- Courses Tab -->
        <div v-show="activeTab === 'courses'" class="space-y-6">
          <!-- Generate Course -->
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title">
                📚 Générer une Roadmap de Cours
              </h2>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Sujet du cours</span>
                </label>
                <input
                  v-model="courseTopic"
                  type="text"
                  placeholder="Ex: Deep Learning, NLP, Computer Vision..."
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Durée (semaines)</span>
                </label>
                <input
                  v-model.number="courseDuration"
                  type="number"
                  min="2"
                  max="16"
                  class="input input-bordered"
                >
              </div>

              <button
                class="btn btn-primary mt-4"
                :disabled="!courseTopic.trim() || loading"
                @click="handleGenerateCourse"
              >
                <span v-if="loading" class="loading loading-spinner loading-sm" />
                <span v-else>Générer la Roadmap</span>
              </button>

              <!-- Generated Course -->
              <div v-if="generatedCourse" class="mt-6 p-4 bg-base-200 rounded-lg">
                <h3 class="font-semibold mb-2">
                  ✅ Roadmap générée !
                </h3>
                <p class="text-sm text-gray-600">
                  Course ID: {{ generatedCourse.course_id }}
                </p>
                <pre class="text-xs mt-2 overflow-x-auto">{{ JSON.stringify(generatedCourse.roadmap, null, 2) }}</pre>
              </div>
            </div>
          </div>

          <!-- Search Courses -->
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title">
                🔍 Cours Disponibles
              </h2>

              <button
                class="btn btn-secondary"
                :disabled="loading"
                @click="handleSearchCourses"
              >
                <span v-if="loading" class="loading loading-spinner loading-sm" />
                <span v-else>Charger les cours</span>
              </button>

              <div v-if="availableCourses.length > 0" class="mt-4 space-y-2">
                <div
                  v-for="course in availableCourses"
                  :key="course.id"
                  class="p-4 bg-base-200 rounded-lg"
                >
                  <h3 class="font-semibold">
                    {{ course.titre }}
                  </h3>
                  <p class="text-sm text-gray-600">
                    Niveau: {{ course.niveau }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Learning Path Tab -->
        <div v-show="activeTab === 'learning-path'" class="space-y-6">
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title">
                🎯 Mon Parcours d'Apprentissage
              </h2>

              <button
                class="btn btn-primary"
                :disabled="loading"
                @click="handleLoadLearningPath"
              >
                <span v-if="loading" class="loading loading-spinner loading-sm" />
                <span v-else>Charger mon parcours</span>
              </button>

              <div v-if="learningPath" class="mt-6">
                <pre class="text-xs overflow-x-auto">{{ JSON.stringify(learningPath, null, 2) }}</pre>
              </div>

              <div v-else class="text-center text-gray-500 py-8">
                <p>Complétez d'abord le questionnaire de profilage pour accéder à votre parcours personnalisé.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat {
  display: flex;
}

.chat-start {
  justify-content: flex-start;
}

.chat-end {
  justify-content: flex-end;
}

.chat-bubble {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
}
</style>
