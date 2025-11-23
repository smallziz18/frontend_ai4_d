<script setup lang="ts">
import { useProfile } from "~/composables/use-profile";
import { useQuestionnaireV2 } from "~/composables/use-questionnaire-v2";
import { useAuth } from "~/data/use-auth";

definePageMeta({
  middleware: ["auth"],
});

const { user } = useAuth();
const { hasProfile, invalidateHasProfileCache } = useProfile();
const {
  session,
  currentQuestion,
  currentQuestionIndex,
  answers,
  analysisResult,
  loading,
  quizCompleted,
  progress,
  answeredCount,
  totalQuestions,
  allQuestionsAnswered,
  generateQuestionnaire,
  submitResponses,
  nextQuestion,
  previousQuestion,
  setAnswer,
  reset,
} = useQuestionnaireV2();

const error = ref("");
const showingResults = ref(false);

// Lancer la génération au montage
onMounted(async () => {
  // Vérifier l'authentification
  const accessToken = useCookie("access_token");
  if (!accessToken.value) {
    await navigateTo("/login");
    return;
  }

  // Vérifier si on a été redirigé ici depuis le dashboard
  const redirectedFromDashboard = sessionStorage.getItem("redirected_to_questionnaire");

  // Vérifier si l'utilisateur a déjà un profil
  const profileExists = await hasProfile();

  if (profileExists && !redirectedFromDashboard) {
    // L'utilisateur a déjà un profil ET n'a pas été redirigé
    // → rediriger vers le dashboard
    console.warn("Profil existe déjà, redirection vers dashboard");
    await navigateTo("/dashboard");
    return;
  }

  // Nettoyer le flag
  if (redirectedFromDashboard) {
    sessionStorage.removeItem("redirected_to_questionnaire");
  }

  // Générer le questionnaire si pas déjà fait
  if (!session.value && !quizCompleted.value) {
    await startGeneration();
  }
});

async function startGeneration() {
  try {
    error.value = "";
    await generateQuestionnaire();
  }
  catch (e: any) {
    error.value = e.message || "Erreur lors de la génération du questionnaire";
  }
}

function handlePrevious() {
  previousQuestion();
}

function handleNext() {
  nextQuestion();
}

async function handleSubmit() {
  try {
    error.value = "";
    await submitResponses();
    showingResults.value = true;

    // IMPORTANT : Invalider le cache du profil pour forcer un rechargement
    // Le backend vient de créer le profil MongoDB, on doit le récupérer
    invalidateHasProfileCache();
  }
  catch (e: any) {
    error.value = e.message || "Erreur lors de la soumission";
  }
}

function handleRetry() {
  reset();
  error.value = "";
  showingResults.value = false;
  startGeneration();
}

async function goToDashboard() {
  // Nettoyer l'état du questionnaire pour éviter la boucle
  reset(); // Reset le questionnaire

  // Invalider le cache du profil
  invalidateHasProfileCache();

  // Attendre un peu pour laisser le backend sauvegarder le profil
  await new Promise(resolve => setTimeout(resolve, 500));

  // Vérifier que le profil existe maintenant
  const profileExists = await hasProfile();

  if (!profileExists) {
    // Si le profil n'existe toujours pas, afficher une erreur
    error.value = "Le profil n'a pas pu être créé. Veuillez réessayer ou contacter le support.";
    console.error("Le profil n'existe pas après la soumission du questionnaire");
    return;
  }

  // Marquer qu'on vient du questionnaire pour éviter la boucle
  sessionStorage.setItem("from_questionnaire", "true");

  // Rediriger vers le dashboard
  await navigateTo("/dashboard");
}

// Fonction pour obtenir la clé de la question actuelle
const currentQuestionKey = computed(() => {
  if (!currentQuestion.value)
    return "";
  return `q_${currentQuestion.value.numero - 1}`;
});

// Réponse de l'utilisateur pour la question actuelle
const currentAnswer = computed({
  get: () => answers.value[currentQuestionKey.value] || "",
  set: (value: string) => {
    setAnswer(currentQuestionKey.value, value);
  },
});

// Options de la question actuelle (avec fallback pour VraiOuFaux)
const currentQuestionOptions = computed(() => {
  if (!currentQuestion.value)
    return [];

  // Si la question a déjà des options, les utiliser
  if (currentQuestion.value.options && currentQuestion.value.options.length > 0) {
    return currentQuestion.value.options;
  }

  // Si c'est VraiOuFaux et pas d'options, utiliser les options par défaut
  if (currentQuestion.value.type === "VraiOuFaux") {
    return ["A. Vrai", "B. Faux"];
  }

  return [];
});

// Calculer le niveau et la couleur du badge
const levelInfo = computed(() => {
  if (!analysisResult.value)
    return { text: "En attente", color: "badge-ghost" };

  const niveau = analysisResult.value.niveau_final;
  if (niveau >= 8)
    return { text: `Expert (${niveau}/10)`, color: "badge-success" };
  if (niveau >= 6)
    return { text: `Avancé (${niveau}/10)`, color: "badge-info" };
  if (niveau >= 4)
    return { text: `Intermédiaire (${niveau}/10)`, color: "badge-warning" };
  return { text: `Débutant (${niveau}/10)`, color: "badge-error" };
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary/5 via-background-light to-secondary/5 dark:from-primary/10 dark:via-background-dark dark:to-secondary/10">
    <!-- Navbar simplifiée -->
    <div class="navbar bg-base-100/80 backdrop-blur-sm shadow-sm sticky top-0 z-50">
      <div class="flex-1">
        <div class="flex items-center gap-2 text-primary dark:text-secondary px-4">
          <Icon name="tabler:school" size="32" />
          <h2 class="text-xl font-bold">
            AI-Edu
          </h2>
        </div>
      </div>
      <div class="flex-none">
        <!-- Theme Toggle -->
        <ThemeToggle />

        <p class="text-sm font-semibold mr-4">
          {{ user?.username }}
        </p>
      </div>
    </div>

    <div class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- Erreur -->
      <div v-if="error" class="alert alert-error mb-6">
        <Icon name="tabler:alert-circle" size="24" />
        <span>{{ error }}</span>
        <button class="btn btn-sm btn-ghost" @click="handleRetry">
          Réessayer
        </button>
      </div>

      <!-- Chargement initial -->
      <div v-if="loading && !session" class="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <span class="loading loading-spinner loading-lg text-primary" />
        <p class="text-lg font-medium">
          🤖 L'IA prépare vos questions personnalisées...
        </p>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Cela peut prendre quelques instants
        </p>
      </div>

      <!-- Résultats et parcours -->
      <div v-else-if="quizCompleted && analysisResult && showingResults" class="space-y-6">
        <!-- En-tête des résultats -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body text-center">
            <h2 class="card-title text-3xl justify-center mb-4">
              ✅ Questionnaire terminé !
            </h2>
            <div class="flex flex-col items-center gap-4">
              <div
                class="radial-progress text-primary"
                :style="`--value:${analysisResult.evaluation.score_percentage}; --size:8rem; --thickness:8px;`"
                role="progressbar"
              >
                <span class="text-2xl font-bold">{{ Math.round(analysisResult.evaluation.score_percentage) }}%</span>
              </div>
              <div class="badge badge-lg" :class="levelInfo.color">
                {{ levelInfo.text }}
              </div>
            </div>

            <!-- Gamification -->
            <div v-if="analysisResult.gamification" class="mt-4 flex flex-wrap justify-center gap-2">
              <div class="badge badge-info gap-2">
                <Icon name="tabler:star-filled" />
                +{{ analysisResult.gamification.xp_gained }} XP
              </div>
              <div v-if="analysisResult.gamification.level_up" class="badge badge-success gap-2">
                <Icon name="tabler:arrow-up" />
                Level Up!
              </div>
              <div
                v-for="badge in analysisResult.gamification.badges_earned"
                :key="badge"
                class="badge badge-warning gap-2"
              >
                <Icon name="tabler:award" />
                {{ badge }}
              </div>
            </div>
          </div>
        </div>

        <!-- Parcours d'apprentissage RPG -->
        <div v-if="analysisResult.parcours_apprentissage" class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h3 class="card-title text-2xl mb-4">
              🎮 {{ analysisResult.parcours_apprentissage.titre }}
            </h3>
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              ⏱️ Durée estimée : {{ analysisResult.parcours_apprentissage.duree_estimee }}
            </p>

            <!-- Quêtes principales -->
            <div v-if="analysisResult.parcours_apprentissage.quetes_principales?.length" class="space-y-4">
              <h4 class="text-xl font-semibold">
                🎯 Quêtes Principales
              </h4>
              <div
                v-for="quete in analysisResult.parcours_apprentissage.quetes_principales"
                :key="quete.id"
                class="card bg-primary/5 border-2 border-primary/20"
              >
                <div class="card-body">
                  <div class="flex justify-between items-start">
                    <h5 class="card-title text-lg">
                      {{ quete.titre }}
                    </h5>
                    <div class="badge badge-primary">
                      {{ quete.xp }} XP
                    </div>
                  </div>
                  <p class="text-sm opacity-80">
                    {{ quete.description }}
                  </p>
                  <div v-if="quete.objectifs?.length" class="mt-2">
                    <p class="text-sm font-semibold mb-1">
                      Objectifs :
                    </p>
                    <ul class="list-disc list-inside text-sm space-y-1">
                      <li v-for="(obj, idx) in quete.objectifs" :key="idx">
                        {{ obj }}
                      </li>
                    </ul>
                  </div>
                  <div v-if="quete.badge" class="mt-2">
                    <span class="badge badge-outline gap-2">
                      <Icon name="tabler:award" />
                      {{ quete.badge }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Boss Fights -->
            <div v-if="analysisResult.parcours_apprentissage.boss_fights?.length" class="space-y-4 mt-6">
              <h4 class="text-xl font-semibold">
                ⚔️ Boss Fights
              </h4>
              <div
                v-for="boss in analysisResult.parcours_apprentissage.boss_fights"
                :key="boss.id"
                class="card bg-error/5 border-2 border-error/20"
              >
                <div class="card-body">
                  <div class="flex justify-between items-start">
                    <h5 class="card-title text-lg">
                      {{ boss.titre }}
                    </h5>
                    <div class="badge badge-error">
                      {{ boss.xp }} XP
                    </div>
                  </div>
                  <p class="text-sm opacity-80">
                    {{ boss.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommandations -->
        <div v-if="analysisResult.recommendations?.length" class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h3 class="card-title text-xl mb-4">
              💡 Recommandations
            </h3>
            <ul class="space-y-2">
              <li
                v-for="(rec, idx) in analysisResult.recommendations"
                :key="idx"
                class="flex gap-2"
              >
                <Icon name="tabler:check" class="text-success mt-1 flex-shrink-0" />
                <span>{{ rec }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Bouton pour aller au dashboard -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body text-center">
            <h3 class="text-xl font-semibold mb-4">
              Prêt à commencer votre aventure ?
            </h3>
            <button class="btn btn-primary btn-lg" @click="goToDashboard">
              <Icon name="tabler:arrow-right" size="24" />
              Aller au Dashboard
            </button>
          </div>
        </div>
      </div>

      <!-- Questions -->
      <div v-else-if="session && !quizCompleted" class="space-y-6">
        <!-- Barre de progression -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <div class="flex justify-between items-center mb-2">
              <h3 class="text-lg font-semibold">
                Question {{ currentQuestionIndex + 1 }} / {{ totalQuestions }}
              </h3>
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ answeredCount }} / {{ totalQuestions }} réponses
              </span>
            </div>
            <progress
              class="progress progress-primary"
              :value="progress"
              max="100"
            />
          </div>
        </div>

        <!-- Question actuelle -->
        <div v-if="currentQuestion" class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title text-2xl mb-6">
              {{ currentQuestion.question }}
            </h2>

            <!-- QCM ou Vrai/Faux -->
            <div v-if="currentQuestion.type === 'ChoixMultiple' || currentQuestion.type === 'VraiOuFaux'" class="space-y-3">
              <div
                v-for="option in currentQuestionOptions"
                :key="option"
                class="form-control"
              >
                <label class="label cursor-pointer justify-start gap-4 p-4 rounded-lg border-2 transition-all" :class="{ 'border-primary bg-primary/5': currentAnswer === option, 'border-base-300 hover:border-primary/50': currentAnswer !== option }">
                  <input
                    v-model="currentAnswer"
                    type="radio"
                    name="answer"
                    :value="option"
                    class="radio radio-primary"
                  >
                  <span class="label-text text-base">{{ option }}</span>
                </label>
              </div>
            </div>

            <!-- Question ouverte -->
            <div v-else-if="currentQuestion.type === 'QuestionOuverte' || currentQuestion.type === 'ListeOuverte'" class="form-control">
              <textarea
                v-model="currentAnswer"
                class="textarea textarea-bordered textarea-lg h-32"
                :placeholder="currentQuestion.type === 'ListeOuverte' ? 'Séparez vos réponses par des virgules' : 'Écrivez votre réponse ici...'"
              />
              <label v-if="currentQuestion.type === 'ListeOuverte'" class="label">
                <span class="label-text-alt">💡 Conseil: Séparez vos réponses par des virgules</span>
              </label>
            </div>

            <!-- Navigation -->
            <div class="card-actions justify-between mt-6">
              <button
                class="btn btn-outline"
                :disabled="currentQuestionIndex === 0"
                @click="handlePrevious"
              >
                <Icon name="tabler:arrow-left" />
                Précédent
              </button>

              <div class="flex gap-2">
                <button
                  v-if="currentQuestionIndex < totalQuestions - 1"
                  class="btn btn-primary"
                  @click="handleNext"
                >
                  Suivant
                  <Icon name="tabler:arrow-right" />
                </button>

                <button
                  v-else
                  class="btn btn-success"
                  :disabled="!allQuestionsAnswered || loading"
                  @click="handleSubmit"
                >
                  <Icon v-if="loading" name="svg-spinners:ring-resize" />
                  <Icon v-else name="tabler:check" />
                  Terminer
                </button>
              </div>
            </div>

            <!-- Indicateur de réponses -->
            <div class="flex flex-wrap gap-2 mt-6 pt-6 border-t">
              <button
                v-for="(q, idx) in session.questions"
                :key="idx"
                class="btn btn-xs btn-circle"
                :class="{ 'btn-primary': answers[`q_${idx}`], 'btn-outline': !answers[`q_${idx}`], 'btn-active': idx === currentQuestionIndex }"
                @click="currentQuestionIndex = idx"
              >
                {{ idx + 1 }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
