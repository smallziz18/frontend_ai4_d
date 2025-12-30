<script setup lang="ts">
import { useQuestionnaireV2 } from "~/composables/use-questionnaire-v2";

definePageMeta({
  middleware: ["auth"],
  layout: "empty",
});

// Keep only the properties used in this page
const { session, currentQuestionIndex, answers, generateQuestionnaire, submitResponses, nextQuestion, previousQuestion, allQuestionsAnswered, loading } = useQuestionnaireV2();

const router = useRouter();
const pageError = ref("");
const submitting = ref(false);

onMounted(async () => {
  const accessToken = useCookie("access_token");
  if (!accessToken.value) {
    await navigateTo("/login");
    return;
  }

  // ✅ Vérifier si l'utilisateur a déjà un profil
  const profileModule = await import("~/composables/use-profile");
  const { hasProfile } = profileModule.useProfile();
  const alreadyHasProfile = await hasProfile();

  if (alreadyHasProfile) {
    // L'utilisateur a déjà complété le questionnaire, rediriger vers le dashboard
    await navigateTo("/dashboard");
    return;
  }

  // Générer si pas de session
  if (!session.value) {
    await startGeneration();
  }
});

async function startGeneration() {
  try {
    pageError.value = "";
    await generateQuestionnaire();
  }
  catch (e: any) {
    console.error("Erreur lors de la génération des questions:", e);
    pageError.value = e.message || "Erreur lors de la génération des questions";
  }
}

function getAnswerKey(index: number) {
  return `q_${index}`;
}

async function handleSubmit() {
  if (!allQuestionsAnswered.value) {
    pageError.value = "Veuillez répondre à au moins une question avant de soumettre.";
    return;
  }

  try {
    submitting.value = true;
    pageError.value = "";

    // ✅ Soumettre les réponses et créer le profil
    await submitResponses();

    // ✅ Invalider le cache pour forcer la vérification du profil
    const { invalidateHasProfileCache, hasProfile } = await import("~/composables/use-profile");
    invalidateHasProfileCache();

    // Marquer qu'on vient du questionnaire
    sessionStorage.setItem("from_questionnaire", "true");

    // Attendre un court délai pour laisser le backend persister le profil
    await new Promise(resolve => setTimeout(resolve, 1200));

    // Vérifier que le profil est bien créé avant de rediriger
    const created = await hasProfile();
    if (!created) {
      pageError.value = "Profil en cours de création, réessayez dans un instant.";
      return;
    }

    // Rediriger vers le dashboard
    await router.replace("/dashboard");
  }
  catch (e: any) {
    console.error("Erreur lors de l'envoi:", e);
    pageError.value = e.message || "Erreur lors de la soumission du questionnaire";
  }
  finally {
    submitting.value = false;
  }
}

function ensureRadioName(index: number) {
  return `question_${index}`; // unique name per question
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <div class="container mx-auto px-4 py-12">
      <div class="max-w-3xl mx-auto">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold">
            Questionnaire de Profilage
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Répondez aux questions pour personnaliser votre expérience d'apprentissage
          </p>
          <p class="text-xs text-primary">
            💡 Les questions sont optionnelles - répondez seulement à celles que vous connaissez
          </p>
        </div>

        <div v-if="pageError" class="alert alert-error mb-6">
          <div>{{ pageError }}</div>
          <button class="btn btn-sm btn-ghost" @click="startGeneration">
            Réessayer
          </button>
        </div>

        <div v-if="!session && loading" class="card p-6 text-center">
          <div class="loading loading-dots" />
          <p class="mt-4">
            Génération en cours...
          </p>
        </div>

        <div v-else-if="session && session.questions && session.questions.length > 0" class="space-y-6">
          <div class="card p-4">
            <div class="flex justify-between items-center">
              <div>Progress: {{ currentQuestionIndex + 1 }} / {{ session.questions.length }}</div>
              <div class="badge badge-primary">
                {{ Object.keys(answers || {}).length }} réponses
              </div>
            </div>
          </div>

          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="text-xl font-semibold mb-2">
                {{ session.questions[currentQuestionIndex]?.question }}
              </h2>

              <div class="mt-4">
                <template v-if="session.questions[currentQuestionIndex]?.type === 'ChoixMultiple'">
                  <div
                    v-for="(opt, idx) in session.questions[currentQuestionIndex]?.options || []"
                    :key="idx"
                    class="my-2"
                  >
                    <label class="label cursor-pointer p-3 rounded-lg border hover:bg-base-200 flex items-center gap-4">
                      <input
                        v-model="answers![getAnswerKey(currentQuestionIndex)]"
                        :name="ensureRadioName(currentQuestionIndex)"
                        type="radio"
                        class="radio radio-primary"
                        :value="opt"
                      >
                      <span>{{ opt }}</span>
                    </label>
                  </div>
                </template>

                <template v-else-if="session.questions[currentQuestionIndex]?.type === 'VraiOuFaux'">
                  <div class="flex gap-4">
                    <label class="label cursor-pointer p-3 rounded-lg border hover:bg-base-200 flex items-center gap-4">
                      <input
                        v-model="answers![getAnswerKey(currentQuestionIndex)]"
                        :name="ensureRadioName(currentQuestionIndex)"
                        type="radio"
                        class="radio radio-primary"
                        value="Vrai"
                      >
                      <span>Vrai</span>
                    </label>

                    <label class="label cursor-pointer p-3 rounded-lg border hover:bg-base-200 flex items-center gap-4">
                      <input
                        v-model="answers[getAnswerKey(currentQuestionIndex)]"
                        :name="ensureRadioName(currentQuestionIndex)"
                        type="radio"
                        class="radio radio-primary"
                        value="Faux"
                      >
                      <span>Faux</span>
                    </label>
                  </div>
                </template>

                <template v-else>
                  <textarea v-model="answers[getAnswerKey(currentQuestionIndex)]" class="textarea textarea-bordered h-32 w-full" />
                </template>
              </div>
            </div>
          </div>

          <div class="flex justify-between items-center">
            <button
              class="btn btn-outline"
              :disabled="currentQuestionIndex === 0"
              @click="previousQuestion"
            >
              Précédent
            </button>
            <div class="flex flex-col items-end gap-1">
              <button
                v-if="currentQuestionIndex < session.questions.length - 1"
                class="btn btn-primary"
                @click="nextQuestion"
              >
                Suivant
              </button>
              <button
                v-else
                class="btn btn-success"
                :disabled="!allQuestionsAnswered || submitting"
                @click="handleSubmit"
              >
                <span v-if="submitting" class="loading loading-spinner loading-sm" />
                {{ submitting ? "Envoi en cours..." : "Terminer" }}
              </button>
              <p v-if="currentQuestionIndex === session.questions.length - 1 && !allQuestionsAnswered" class="text-xs text-warning">
                Répondez à au moins 1 question
              </p>
            </div>
          </div>
        </div>

        <div v-else class="card p-6 text-center">
          <h3 class="text-lg font-medium">
            Prêt à commencer
          </h3>
          <p class="text-sm text-gray-600 my-4">
            Cliquez pour générer un questionnaire.
          </p>
          <button
            class="btn btn-primary"
            :disabled="loading"
            @click="startGeneration"
          >
            Commencer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
