<script setup lang="ts">
import { useQuestionnaire } from "~/composables/use-questionnaire";
import { useAuth } from "~/data/use-auth";

definePageMeta({
  middleware: ["auth", "check-profile"],
  layout: "empty",
});

const { user } = useAuth();
const {
  questions,
  currentQuestionIndex,
  answers,
  quizCompleted,
  evaluationResult,
  questionTaskId,
  analysisTaskId,
  taskCheckAttempts,
  generateQuestionnaire,
  checkTaskStatus,
  checkAnalysisStatus,
  parseQuestionsPayload,
  submitQuestionnaire,
  resetQuestionnaire,
} = useQuestionnaire();

const router = useRouter();
const loading = ref(false);
const error = ref("");
const generationStartTime = ref<number | null>(null);

// Computed pour obtenir la question actuelle de manière sûre
const currentQuestion = computed(() => {
  if (!questions.value || questions.value.length === 0) {
    return null;
  }
  return questions.value[currentQuestionIndex.value];
});

// Lancer la génération du questionnaire au montage
onMounted(async () => {
  // Vérifier l'authentification
  const accessToken = useCookie("access_token");
  if (!accessToken.value) {
    await navigateTo("/login");
    return;
  }

  // ✅ Vérifier si l'utilisateur a déjà un profil
  // Si oui, le questionnaire a déjà été fait -> rediriger vers dashboard
  const { hasProfile: checkProfile } = useProfile();
  const profileExists = await checkProfile();

  if (profileExists) {
    console.warn("⚠️ Profil déjà existant - Redirection vers dashboard");
    await navigateTo("/dashboard");
    return;
  }

  // Pas de profil -> lancer le questionnaire
  if (!questions.value && !questionTaskId.value && !quizCompleted.value) {
    await startGeneration();
  }
});

async function startGeneration() {
  try {
    loading.value = true;
    error.value = "";
    generationStartTime.value = Date.now();
    await generateQuestionnaire();
  }
  catch (e: any) {
    error.value = e.message || "Erreur lors de la génération du questionnaire";
  }
  finally {
    loading.value = false;
  }
}

// Vérifier le statut de la tâche périodiquement
const checkingTask = ref(false);
watch(questionTaskId, async (taskId) => {
  if (taskId && !questions.value && !checkingTask.value) {
    checkingTask.value = true;
    await pollTaskStatus(taskId);
  }
}, { immediate: true });

// Watcher pour l'analyse du profil - AUTOMATIQUE
const checkingAnalysis = ref(false);
watch(analysisTaskId, async (taskId) => {
  if (taskId && quizCompleted.value && !checkingAnalysis.value) {
    checkingAnalysis.value = true;
    // 🚀 Automatiquement vérifier le statut de l'analyse et rediriger quand prêt
    await pollAnalysisStatus(taskId);
  }
}, { immediate: true });

async function pollTaskStatus(taskId: string) {
  const maxAttempts = 60; // 60 * 3s = 3 minutes max

  while (taskCheckAttempts.value < maxAttempts && !questions.value) {
    await new Promise(resolve => setTimeout(resolve, 3000)); // Attendre 3s

    const taskData = await checkTaskStatus(taskId);

    if (!taskData) {
      taskCheckAttempts.value++;
      continue;
    }

    const status = taskData.status?.toLowerCase();

    if (status === "success" || status === "succeeded") {
      const resultData = taskData.result;
      const parsedQuestions = parseQuestionsPayload(resultData);

      if (parsedQuestions && parsedQuestions.length > 0) {
        questions.value = parsedQuestions;
        questionTaskId.value = null;
        taskCheckAttempts.value = 0;
        checkingTask.value = false;
        return;
      }
      else {
        error.value = "Format de questions invalide. Le serveur n'a pas retourné les questions dans le bon format.";
        checkingTask.value = false;
        return;
      }
    }
    else if (status === "failure" || status === "failed") {
      error.value = taskData.error || "La génération a échoué. Veuillez réessayer.";
      questionTaskId.value = null;
      checkingTask.value = false;
      return;
    }

    taskCheckAttempts.value++;
  }

  if (taskCheckAttempts.value >= maxAttempts) {
    error.value = "La génération prend plus de temps que prévu (timeout après 3 minutes). Veuillez réessayer.";
    questionTaskId.value = null;
  }

  checkingTask.value = false;
}

// 🚀 Fonction pour vérifier automatiquement le statut de l'analyse et rediriger
async function pollAnalysisStatus(taskId: string) {
  const maxAttempts = 60; // 60 * 3s = 3 minutes max
  let attempts = 0;

  console.warn(`🔍 Démarrage du polling pour l'analyse (task_id: ${taskId})`);

  while (attempts < maxAttempts) {
    await new Promise(resolve => setTimeout(resolve, 3000)); // Attendre 3s

    const taskData = await checkAnalysisStatus(taskId);

    if (!taskData) {
      attempts++;
      console.warn(`⏱️ Tentative ${attempts}/${maxAttempts} - Pas de données reçues`);
      continue;
    }

    const status = taskData.status?.toLowerCase();
    console.warn(`📊 Tentative ${attempts}/${maxAttempts} - Statut: ${status}`);

    if (status === "success" || status === "succeeded") {
      // ✅ L'analyse est terminée et le profil a été créé côté backend
      console.warn("✅ Profil créé avec succès - Vérification finale avant redirection...");

      analysisTaskId.value = null;
      checkingAnalysis.value = false;

      // Invalider le cache du profil
      const { invalidateHasProfileCache, hasProfile: checkProfile } = useProfile();
      invalidateHasProfileCache();

      // Attendre un peu pour que le backend finalise
      await new Promise(r => setTimeout(r, 2000));

      // Vérifier que le profil existe réellement
      const profileExists = await checkProfile();

      if (profileExists) {
        console.warn("✅ Profil confirmé - Redirection vers dashboard...");

        // Marquer qu'on vient de compléter le questionnaire
        sessionStorage.setItem("from_questionnaire", "true");

        // ✅ Rediriger automatiquement vers le dashboard
        await router.push("/dashboard");
        return;
      }
      else {
        console.error("❌ Le profil n'existe pas malgré le statut success");
        error.value = "❌ Le profil n'a pas été créé correctement. Veuillez contacter le support.";
        return;
      }
    }
    else if (status === "failure" || status === "failed") {
      console.error(`❌ Échec de l'analyse: ${taskData.error || "Raison inconnue"}`);
      error.value = `❌ La création du profil a échoué: ${taskData.error || "Erreur inconnue"}. Veuillez réessayer.`;
      analysisTaskId.value = null;
      checkingAnalysis.value = false;
      return;
    }

    // Statut en cours (pending, started, etc.)
    attempts++;
  }

  // Timeout - mais on affiche un message moins effrayant
  console.warn("⏱️ Timeout lors de la vérification de l'analyse (3 minutes)");
  error.value = "⏱️ La création du profil prend plus de temps que prévu. Vous pouvez cliquer sur le bouton pour accéder au dashboard.";
  checkingAnalysis.value = false;
}

function handlePrevious() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
  }
}

function handleNext() {
  // ✅ Permettre de passer des questions sans réponse (l'utilisateur ne connaît pas)
  // On efface juste l'erreur si elle existe
  error.value = "";

  if (questions.value && currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++;
  }
}

async function handleSubmit() {
  // Vérifier qu'au moins une question a été répondue
  // eslint-disable-next-line ts/no-use-before-define
  if (atLeastOneAnswered.value) {
    try {
      loading.value = true;
      error.value = "";
      const result = await submitQuestionnaire();

      // Stocker le task_id de l'analyse pour vérifier son statut
      if (result && result.analysisTaskId) {
        analysisTaskId.value = result.analysisTaskId;
      }
      else {
        // Si pas de task_id retourné, afficher une erreur
        error.value = "❌ Aucune tâche d'analyse n'a été créée. Le profil ne sera pas créé. Veuillez réessayer.";
      }
    }
    catch (e: any) {
      error.value = e.message || "Erreur lors de la soumission";
    }
    finally {
      loading.value = false;
    }
  }
  else {
    error.value = "❌ Veuillez répondre à au moins une question avant de soumettre.";
  }
}

function handleRetry() {
  resetQuestionnaire();
  generationStartTime.value = null;
  startGeneration();
}

async function goToDashboard() {
  loading.value = true;
  error.value = "";

  try {
    // Si nous avons un task_id d'analyse, vérifier son statut
    if (analysisTaskId.value) {
      const maxAttempts = 30; // 30 * 2s = 1 minute max
      let attempts = 0;

      while (attempts < maxAttempts) {
        const taskData = await checkAnalysisStatus(analysisTaskId.value);

        if (!taskData) {
          attempts++;
          await new Promise(resolve => setTimeout(resolve, 2000));
          continue;
        }

        const status = taskData.status?.toLowerCase();

        if (status === "success" || status === "succeeded") {
          // L'analyse est terminée et le profil a été créé côté backend
          analysisTaskId.value = null;

          // Profil créé avec succès - invalider le cache et rediriger
          const { invalidateHasProfileCache } = useProfile();
          invalidateHasProfileCache();

          // ✅ Marquer qu'on vient de compléter le questionnaire
          sessionStorage.setItem("from_questionnaire", "true");

          // Attendre un peu pour que le backend finalise
          await new Promise(r => setTimeout(r, 1500));

          // Rediriger vers le dashboard
          await router.push("/dashboard");
          return;
        }
        else if (status === "failure" || status === "failed") {
          error.value = "La création du profil a échoué. Veuillez réessayer.";
          analysisTaskId.value = null;
          return;
        }

        // Statut en cours (pending, started, etc.)
        attempts++;
        await new Promise(resolve => setTimeout(resolve, 2000));
      }

      // Timeout
      error.value = "La création du profil prend plus de temps que prévu. Veuillez patienter encore quelques instants puis réessayer.";
    }
    else {
      // Pas de task_id: vérifier directement si le profil existe
      const { hasProfile: checkProfile, invalidateHasProfileCache } = useProfile();
      invalidateHasProfileCache();
      const profileExists = await checkProfile();

      if (profileExists) {
        // ✅ Marquer qu'on vient de compléter le questionnaire
        sessionStorage.setItem("from_questionnaire", "true");
        await router.push("/dashboard");
      }
      else {
        error.value = "Votre profil n'a pas encore été créé. Veuillez patienter.";
      }
    }
  }
  catch (e: any) {
    console.error("Erreur lors de la vérification du profil:", e);
    error.value = "Impossible de vérifier le profil. Veuillez réessayer.";
  }
  finally {
    loading.value = false;
  }
}

const elapsedTime = computed(() => {
  if (!generationStartTime.value)
    return 0;
  return Math.floor((Date.now() - generationStartTime.value) / 1000);
});

const progressValue = computed(() => {
  if (!questionTaskId.value)
    return 0;
  const estimatedTime = 120; // 120 secondes (2 minutes)
  return Math.min(Math.floor((elapsedTime.value / estimatedTime) * 95), 95); // Maximum 95% pendant le chargement, 100% quand c'est terminé
});

// Vérifier si la question actuelle a une réponse
const currentQuestionAnswered = computed(() => {
  const answer = answers.value[`q_${currentQuestionIndex.value}`];
  return answer !== undefined && answer !== null && answer.toString().trim() !== "";
});

// Vérifier si au moins UNE question a été répondue
const atLeastOneAnswered = computed(() => {
  if (!questions.value)
    return false;
  return Object.keys(answers.value).some((key) => {
    const answer = answers.value[key];
    return answer !== undefined && answer !== null && answer.toString().trim() !== "";
  });
});

// Computed pour savoir si on peut soumettre le questionnaire
// ✅ Permettre de soumettre même avec des réponses vides (au moins 1 réponse suffit)
const canSubmit = computed(() => {
  return atLeastOneAnswered.value && !loading.value;
});
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <!-- Header -->
    <div class="navbar bg-base-100 shadow-sm">
      <div class="flex-1">
        <div class="flex items-center gap-2 text-primary dark:text-secondary px-4">
          <Icon name="tabler:school" size="32" />
          <h2 class="text-xl font-bold">
            AI-Edu
          </h2>
        </div>
      </div>
      <div class="flex-none">
        <div class="flex items-center gap-2 mr-4">
          <Icon name="tabler:user-filled" size="20" />
          <span class="text-sm">{{ user?.username }}</span>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-4 py-12">
      <div class="max-w-4xl mx-auto">
        <!-- En-tête -->
        <div class="text-center mb-8">
          <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-3">
            ❓ Questionnaire de Diagnostic
          </h1>
          <p class="text-lg text-gray-600 dark:text-gray-400">
            Répondez à ces questions pour que notre IA puisse personnaliser votre expérience d'apprentissage
          </p>
        </div>

        <!-- Erreur -->
        <div v-if="error" class="alert alert-error mb-6">
          <Icon name="tabler:alert-circle" size="24" />
          <div>
            <span>{{ error }}</span>
          </div>
          <button class="btn btn-sm btn-ghost" @click="handleRetry">
            Réessayer
          </button>
        </div>

        <!-- Génération en cours -->
        <div v-if="questionTaskId && !questions" class="card bg-base-100 shadow-xl">
          <div class="card-body text-center">
            <Icon
              name="tabler:robot"
              size="64"
              class="mx-auto mb-4 text-primary animate-pulse"
            />
            <h2 class="card-title justify-center text-2xl mb-4">
              🤖 L'IA prépare vos questions personnalisées
            </h2>

            <div class="alert alert-info mb-4">
              <Icon name="tabler:info-circle" size="24" />
              <div class="text-left">
                <p class="font-semibold">
                  ⏰ La génération peut prendre 1 à 2 minutes
                </p>
                <p class="text-sm mt-1">
                  L'IA analyse votre profil et génère des questions adaptées à votre niveau. Merci de votre patience ! 🙏
                </p>
              </div>
            </div>

            <div class="space-y-4">
              <progress
                class="progress progress-primary w-full"
                :value="progressValue"
                max="100"
              />

              <div class="text-sm text-gray-600 dark:text-gray-400">
                <div class="flex items-center justify-center gap-2 mb-2">
                  <span class="loading loading-spinner loading-sm" />
                  <p v-if="elapsedTime < 30" class="font-medium">
                    🔍 Analyse de votre profil en cours...
                  </p>
                  <p v-else-if="elapsedTime < 60" class="font-medium">
                    ✍️ Génération des questions personnalisées...
                  </p>
                  <p v-else-if="elapsedTime < 90" class="font-medium">
                    🎯 Ajustement de la difficulté...
                  </p>
                  <p v-else class="font-medium">
                    ⏳ Finalisation (presque terminé)...
                  </p>
                </div>
                <p class="text-xs opacity-70">
                  ⏱️ Temps écoulé: {{ elapsedTime }}s / ~90-120s estimé
                </p>
              </div>

              <div class="flex gap-2 justify-center mt-4">
                <span class="loading loading-dots loading-lg text-primary" />
              </div>

              <!-- Astuce pour patienter -->
              <div class="mt-6 p-4 bg-base-200 rounded-lg">
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  💡 <strong>Le saviez-vous ?</strong> L'IA génère des questions uniques basées sur votre profil d'étudiant ou de professeur pour une expérience d'apprentissage optimale.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quiz terminé -->
        <div v-else-if="quizCompleted && evaluationResult" class="space-y-6">
          <div class="alert alert-success">
            <Icon name="tabler:check" size="24" />
            <span>✅ Questionnaire terminé!</span>
          </div>

          <!-- Info création profil -->
          <div class="alert alert-info">
            <Icon name="tabler:info-circle" size="24" />
            <div>
              <h3 class="font-bold">
                Création de votre profil en cours
              </h3>
              <p class="text-sm">
                Notre IA analyse vos réponses pour créer votre profil personnalisé. Cela peut prendre quelques instants.
              </p>
            </div>
          </div>

          <div class="stats stats-vertical lg:stats-horizontal shadow w-full">
            <div class="stat">
              <div class="stat-figure text-primary">
                <Icon name="tabler:trophy" size="48" />
              </div>
              <div class="stat-title">
                Score
              </div>
              <div class="stat-value text-primary">
                {{ evaluationResult.score }}
              </div>
              <div class="stat-desc">
                {{ evaluationResult.score_percentage }}% de réussite
              </div>
            </div>

            <div class="stat">
              <div class="stat-figure text-secondary">
                <Icon name="tabler:checklist" size="48" />
              </div>
              <div class="stat-title">
                Questions
              </div>
              <div class="stat-value text-secondary">
                {{ evaluationResult.questions_data.length }}
              </div>
              <div class="stat-desc">
                questions répondues
              </div>
            </div>
          </div>

          <!-- Détails des réponses -->
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title">
                📋 Détails de vos réponses
              </h2>

              <div class="space-y-4 mt-4">
                <div
                  v-for="(item, index) in evaluationResult.questions_data"
                  :key="index"
                  class="p-4 rounded-lg"
                  :class="{
                    'bg-success/10': item.is_correct === true,
                    'bg-error/10': item.is_correct === false,
                    'bg-warning/10': typeof item.is_correct === 'string',
                  }"
                >
                  <div class="flex items-start gap-3">
                    <div class="mt-1">
                      <Icon
                        v-if="item.is_correct === true"
                        name="tabler:check"
                        size="24"
                        class="text-success"
                      />
                      <Icon
                        v-else-if="item.is_correct === false"
                        name="tabler:x"
                        size="24"
                        class="text-error"
                      />
                      <Icon
                        v-else
                        name="tabler:alert-circle"
                        size="24"
                        class="text-warning"
                      />
                    </div>
                    <div class="flex-1">
                      <p class="font-semibold mb-2">
                        Question {{ item.numero }}: {{ item.question }}
                      </p>
                      <p class="text-sm">
                        <span class="font-medium">Votre réponse:</span> {{ item.user_answer || "(Non répondu)" }}
                      </p>
                      <p
                        v-if="typeof item.is_correct !== 'string'"
                        class="text-sm mt-1"
                      >
                        <span class="font-medium">Réponse attendue:</span> {{ item.correct_answer }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col gap-4 items-center">
            <div class="alert alert-info max-w-2xl">
              <Icon name="tabler:info-circle" size="24" />
              <div>
                <p class="font-semibold">
                  ℹ️ Questionnaire unique
                </p>
                <p class="text-sm">
                  Ce questionnaire ne peut être fait qu'une seule fois pour créer votre profil. Une fois votre profil créé, vous pourrez améliorer votre niveau en suivant des cours.
                </p>
              </div>
            </div>

            <button
              class="btn btn-primary btn-lg"
              :class="{ loading }"
              :disabled="loading"
              @click="goToDashboard"
            >
              <Icon
                v-if="!loading"
                name="tabler:home"
                size="20"
              />
              {{ loading ? "Vérification du profil..." : "Aller au Dashboard" }}
            </button>
          </div>
        </div>

        <!-- Questions -->
        <div v-else-if="questions && questions.length > 0" class="space-y-6">
          <!-- Barre de progression -->
          <div class="card bg-base-100 shadow">
            <div class="card-body py-4">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm font-medium">Progression</span>
                <span class="text-sm font-medium">
                  Question {{ currentQuestionIndex + 1 }} / {{ questions.length }}
                </span>
              </div>
              <progress
                class="progress progress-primary w-full"
                :value="currentQuestionIndex + 1"
                :max="questions.length"
              />
            </div>
          </div>

          <!-- Question actuelle -->
          <div v-if="currentQuestion" class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title text-2xl mb-4">
                {{ currentQuestion.question }}
              </h2>

              <div class="divider" />

              <!-- Choix multiple -->
              <div
                v-if="currentQuestion.type === 'ChoixMultiple'"
                class="space-y-3"
              >
                <div
                  v-for="(option, idx) in currentQuestion.options"
                  :key="idx"
                  class="form-control"
                >
                  <label class="label cursor-pointer justify-start gap-4 p-4 rounded-lg border hover:bg-base-200">
                    <input
                      v-model="answers[`q_${currentQuestionIndex}`]"
                      type="radio"
                      :value="option"
                      class="radio radio-primary"
                    >
                    <span class="label-text text-base">{{ option }}</span>
                  </label>
                </div>
              </div>

              <!-- Vrai ou Faux -->
              <div
                v-else-if="currentQuestion.type === 'VraiOuFaux'"
                class="space-y-3"
              >
                <div class="form-control">
                  <label class="label cursor-pointer justify-start gap-4 p-4 rounded-lg border hover:bg-base-200">
                    <input
                      v-model="answers[`q_${currentQuestionIndex}`]"
                      type="radio"
                      value="Vrai"
                      class="radio radio-primary"
                    >
                    <span class="label-text text-base">✅ Vrai</span>
                  </label>
                </div>
                <div class="form-control">
                  <label class="label cursor-pointer justify-start gap-4 p-4 rounded-lg border hover:bg-base-200">
                    <input
                      v-model="answers[`q_${currentQuestionIndex}`]"
                      type="radio"
                      value="Faux"
                      class="radio radio-primary"
                    >
                    <span class="label-text text-base">❌ Faux</span>
                  </label>
                </div>
              </div>

              <!-- Question ouverte -->
              <div
                v-else-if="currentQuestion.type === 'QuestionOuverte' || currentQuestion.type === 'ListeOuverte'"
                class="form-control"
              >
                <label class="label">
                  <span class="label-text">Votre réponse</span>
                  <span
                    v-if="currentQuestion.type === 'ListeOuverte'"
                    class="label-text-alt"
                  >
                    💡 Séparez vos réponses par des virgules
                  </span>
                </label>
                <textarea
                  v-model="answers[`q_${currentQuestionIndex}`]"
                  class="textarea textarea-bordered h-32"
                  placeholder="Écrivez votre réponse ici..."
                />
              </div>
            </div>
          </div>

          <!-- Navigation -->
          <div class="flex justify-between items-center">
            <button
              class="btn btn-outline"
              :disabled="currentQuestionIndex === 0"
              @click="handlePrevious"
            >
              <Icon name="tabler:arrow-left" size="20" />
              Précédent
            </button>

            <div class="badge badge-lg badge-primary">
              {{ Object.keys(answers).length }} / {{ questions.length }} réponses
            </div>

            <button
              v-if="currentQuestionIndex < questions.length - 1"
              class="btn btn-primary"
              @click="handleNext"
            >
              Suivant
              <Icon name="tabler:arrow-right" size="20" />
            </button>
            <button
              v-else
              class="btn btn-success"
              :disabled="!canSubmit"
              :class="{ 'btn-disabled': !canSubmit }"
              @click="handleSubmit"
            >
              <Icon name="tabler:check" size="20" />
              {{ loading ? "Envoi..." : "Terminer" }}
            </button>
          </div>

          <!-- Message d'aide si aucune question n'est répondue -->
          <div v-if="!atLeastOneAnswered" class="alert alert-warning">
            <Icon name="tabler:alert-triangle" size="24" />
            <div>
              <p class="font-semibold">
                ⚠️ Attention
              </p>
              <p class="text-sm">
                Vous devez répondre à au moins une question pour soumettre le questionnaire.
              </p>
            </div>
          </div>

          <!-- Message d'info pour laisser des questions vides -->
          <div v-else-if="!currentQuestionAnswered" class="alert alert-info">
            <Icon name="tabler:info-circle" size="24" />
            <div>
              <p class="text-sm">
                💡 Vous pouvez laisser des questions sans réponse si vous ne connaissez pas la réponse. Cliquez sur "Suivant" pour continuer.
              </p>
            </div>
          </div>
        </div>

        <!-- État initial: bouton pour lancer -->
        <div v-else class="card bg-base-100 shadow-xl">
          <div class="card-body text-center">
            <Icon
              name="tabler:clipboard-check"
              size="64"
              class="mx-auto mb-4 text-primary"
            />
            <h2 class="card-title justify-center text-2xl mb-4">
              Prêt à commencer?
            </h2>
            <p class="text-gray-600 dark:text-gray-400 mb-6">
              Ce questionnaire nous aidera à personnaliser votre expérience d'apprentissage.
              Cela prendra environ 10-15 minutes.
            </p>
            <button
              class="btn btn-primary btn-lg"
              :disabled="loading"
              @click="startGeneration"
            >
              <Icon name="tabler:sparkles" size="20" />
              {{ loading ? "Chargement..." : "Commencer le questionnaire" }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
