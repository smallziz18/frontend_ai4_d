<script setup lang="ts">
import { useProfile } from "~~/composables/use-profile";
import { useQuestionnaire } from "~~/composables/use-questionnaire";

import { useAuth } from "~/data/use-auth";

const { user, logout, loadUserFromCookie } = useAuth();
const { profile, profileLoading, fetchProfile, fetchRecommendations } = useProfile();
const { evaluationResult } = useQuestionnaire();
const router = useRouter();
const hasCompletedQuestionnaire = useCookie("questionnaire_completed", { default: () => false });
const showWelcomeModal = ref(false);

// Calculer le niveau d'après le score
const userLevel = computed(() => {
  if (!evaluationResult.value) {
    return profile.value?.analysis?.niveau_global || "Débutant";
  }
  const percentage = evaluationResult.value.score_percentage;
  if (percentage >= 80)
    return "Expert";
  if (percentage >= 60)
    return "Avancé";
  if (percentage >= 40)
    return "Intermédiaire";
  return "Débutant";
});

const levelColor = computed(() => {
  const level = userLevel.value.toLowerCase();
  if (level.includes("expert"))
    return "badge-success";
  if (level.includes("avancé"))
    return "badge-info";
  if (level.includes("intermédiaire"))
    return "badge-warning";
  return "badge-error";
});

// Charger l'utilisateur depuis les cookies au montage
onMounted(async () => {
  // Vérifier l'authentification
  const accessToken = useCookie("access_token");
  if (!accessToken.value) {
    await navigateTo("/login");
    return;
  }

  await loadUserFromCookie();

  // Si le questionnaire est complété, charger le profil
  if (hasCompletedQuestionnaire.value) {
    await fetchProfile();
    await fetchRecommendations();

    // Si pas de profil du backend, utiliser des données de fallback pour le développement
    if (!profile.value && evaluationResult.value) {
      profile.value = {
        analysis: {
          niveau_global: userLevel.value,
          points_forts: [
            "Bonne compréhension des concepts de base",
            "Capacité d'analyse logique",
            "Motivation pour apprendre",
          ],
          points_ameliorer: [
            "Pratique régulière recommandée",
            "Approfondissement des sujets avancés",
          ],
          style_apprentissage: "Visuel et pratique avec des exemples concrets",
        },
        recommendations: [
          `Commencez par les cours de niveau ${userLevel.value}`,
          "Pratiquez régulièrement avec des exercices interactifs",
          "Rejoignez une communauté d'apprentissage",
        ],
        next_steps: [
          "Complétez le module d'introduction",
          "Réalisez 3 exercices pratiques par semaine",
          "Participez aux sessions de groupe en ligne",
        ],
      };
    }
  }
  else {
    // Sinon afficher le modal de bienvenue
    showWelcomeModal.value = true;
  }
});

async function handleLogout() {
  await logout();
  await navigateTo("/login");
}

function goToQuestionnaire() {
  showWelcomeModal.value = false;
  router.push("/questionnaire");
}

function skipQuestionnaire() {
  showWelcomeModal.value = false;
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <!-- Modal de bienvenue -->
    <dialog
      :open="showWelcomeModal"
      class="modal"
      :class="{ 'modal-open': showWelcomeModal }"
    >
      <div class="modal-box max-w-2xl">
        <div class="text-center">
          <Icon
            name="tabler:sparkles"
            size="64"
            class="mx-auto mb-4 text-primary"
          />
          <h3 class="font-bold text-3xl mb-4">
            Bienvenue sur AI-Edu ! 🎉
          </h3>
          <p class="text-lg mb-6">
            Pour personnaliser votre expérience d'apprentissage, nous vous invitons à répondre à un questionnaire de diagnostic.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div class="p-4 bg-base-200 rounded-lg">
              <Icon
                name="tabler:brain"
                size="32"
                class="mx-auto mb-2 text-primary"
              />
              <p class="font-semibold mb-1">
                Personnalisé
              </p>
              <p class="text-sm opacity-70">
                L'IA adapte le contenu à votre niveau
              </p>
            </div>
            <div class="p-4 bg-base-200 rounded-lg">
              <Icon
                name="tabler:clock"
                size="32"
                class="mx-auto mb-2 text-primary"
              />
              <p class="font-semibold mb-1">
                10-15 minutes
              </p>
              <p class="text-sm opacity-70">
                Questions aléatoires adaptées
              </p>
            </div>
            <div class="p-4 bg-base-200 rounded-lg">
              <Icon
                name="tabler:chart-line"
                size="32"
                class="mx-auto mb-2 text-primary"
              />
              <p class="font-semibold mb-1">
                Suivi des progrès
              </p>
              <p class="text-sm opacity-70">
                Analyse détaillée de vos compétences
              </p>
            </div>
          </div>
        </div>

        <div class="modal-action justify-center gap-3">
          <button
            class="btn btn-primary btn-lg"
            @click="goToQuestionnaire"
          >
            <Icon name="tabler:clipboard-check" size="20" />
            Commencer maintenant
          </button>
          <button
            class="btn btn-ghost btn-lg"
            @click="skipQuestionnaire"
          >
            Plus tard
          </button>
        </div>
      </div>
      <form
        method="dialog"
        class="modal-backdrop"
        @click="skipQuestionnaire"
      >
        <button>close</button>
      </form>
    </dialog>

    <!-- Navbar -->
    <div class="navbar bg-base-100 shadow-sm">
      <div class="flex-1">
        <div class="flex items-center gap-2 text-primary dark:text-secondary px-4">
          <Icon name="tabler:school" size="32" />
          <h2 class="text-xl font-bold">
            AI-Edu
          </h2>
        </div>
      </div>
      <div class="flex-none gap-2">
        <div class="flex items-center gap-2 mr-4">
          <div class="avatar placeholder">
            <div class="bg-primary text-primary-content rounded-full w-10">
              <span class="text-lg">{{ user?.username?.charAt(0).toUpperCase() }}</span>
            </div>
          </div>
          <div class="hidden md:block">
            <p class="text-sm font-semibold">
              {{ user?.username }}
            </p>
            <p class="text-xs opacity-70">
              {{ user?.email }}
            </p>
          </div>
        </div>
        <button
          class="btn btn-ghost btn-sm"
          @click="handleLogout"
        >
          <Icon name="tabler:logout" size="20" />
          Déconnexion
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="profileLoading" class="container mx-auto px-4 py-16">
      <div class="flex justify-center items-center min-h-[400px]">
        <span class="loading loading-spinner loading-lg text-primary" />
      </div>
    </div>

    <!-- Dashboard with profile -->
    <div v-else-if="hasCompletedQuestionnaire && (profile || evaluationResult)" class="container mx-auto px-4 py-8">
      <!-- Header avec score -->
      <div class="mb-8">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Bienvenue, {{ user?.username }} ! 👋
            </h1>
            <p class="text-lg text-gray-600 dark:text-gray-400">
              Voici votre tableau de bord personnalisé
            </p>
          </div>
          <div class="badge badge-lg" :class="levelColor">
            <Icon
              name="tabler:award"
              size="20"
              class="mr-1"
            />
            Niveau {{ userLevel }}
          </div>
        </div>
      </div>

      <!-- Stats cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <!-- Score -->
        <div class="card bg-gradient-to-br from-primary to-primary/80 text-white shadow-xl">
          <div class="card-body">
            <div class="flex justify-between items-start">
              <div>
                <p class="text-sm opacity-80 mb-1">
                  Score du questionnaire
                </p>
                <p class="text-4xl font-bold">
                  {{ evaluationResult?.score_percentage || 0 }}%
                </p>
                <p class="text-sm opacity-80 mt-2">
                  {{ evaluationResult?.score || "0/0" }}
                </p>
              </div>
              <Icon
                name="tabler:trophy"
                size="48"
                class="opacity-80"
              />
            </div>
          </div>
        </div>

        <!-- Points forts -->
        <div class="card bg-gradient-to-br from-success to-success/80 text-white shadow-xl">
          <div class="card-body">
            <div class="flex justify-between items-start">
              <div>
                <p class="text-sm opacity-80 mb-1">
                  Points forts
                </p>
                <p class="text-4xl font-bold">
                  {{ profile?.analysis?.points_forts?.length || 0 }}
                </p>
                <p class="text-sm opacity-80 mt-2">
                  Compétences identifiées
                </p>
              </div>
              <Icon
                name="tabler:chart-line"
                size="48"
                class="opacity-80"
              />
            </div>
          </div>
        </div>

        <!-- Recommandations -->
        <div class="card bg-gradient-to-br from-info to-info/80 text-white shadow-xl">
          <div class="card-body">
            <div class="flex justify-between items-start">
              <div>
                <p class="text-sm opacity-80 mb-1">
                  Recommandations IA
                </p>
                <p class="text-4xl font-bold">
                  {{ (profile?.recommendations?.length || 0) + (profile?.next_steps?.length || 0) }}
                </p>
                <p class="text-sm opacity-80 mt-2">
                  Actions suggérées
                </p>
              </div>
              <Icon
                name="tabler:bulb"
                size="48"
                class="opacity-80"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Contenu principal en 2 colonnes -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Colonne gauche: Analyse -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Analyse du profil -->
          <div v-if="profile?.analysis" class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title text-2xl">
                <Icon name="tabler:brain" size="28" />
                Analyse de votre profil
              </h2>

              <div class="divider" />

              <!-- Style d'apprentissage -->
              <div v-if="profile.analysis.style_apprentissage" class="mb-4">
                <div class="flex items-center gap-2 mb-2">
                  <Icon
                    name="tabler:palette"
                    size="20"
                    class="text-primary"
                  />
                  <h3 class="font-semibold text-lg">
                    Style d'apprentissage
                  </h3>
                </div>
                <p class="text-gray-600 dark:text-gray-400 ml-7">
                  {{ profile.analysis.style_apprentissage }}
                </p>
              </div>

              <!-- Points forts -->
              <div v-if="profile.analysis.points_forts && profile.analysis.points_forts.length > 0" class="mb-4">
                <div class="flex items-center gap-2 mb-2">
                  <Icon
                    name="tabler:check"
                    size="20"
                    class="text-success"
                  />
                  <h3 class="font-semibold text-lg">
                    Points forts
                  </h3>
                </div>
                <ul class="space-y-2 ml-7">
                  <li
                    v-for="(point, idx) in profile.analysis.points_forts"
                    :key="idx"
                    class="flex items-start gap-2"
                  >
                    <Icon
                      name="tabler:circle-check-filled"
                      size="18"
                      class="text-success mt-0.5"
                    />
                    <span>{{ point }}</span>
                  </li>
                </ul>
              </div>

              <!-- Points à améliorer -->
              <div v-if="profile.analysis.points_ameliorer && profile.analysis.points_ameliorer.length > 0">
                <div class="flex items-center gap-2 mb-2">
                  <Icon
                    name="tabler:target"
                    size="20"
                    class="text-warning"
                  />
                  <h3 class="font-semibold text-lg">
                    Points à améliorer
                  </h3>
                </div>
                <ul class="space-y-2 ml-7">
                  <li
                    v-for="(point, idx) in profile.analysis.points_ameliorer"
                    :key="idx"
                    class="flex items-start gap-2"
                  >
                    <Icon
                      name="tabler:circle-dotted"
                      size="18"
                      class="text-warning mt-0.5"
                    />
                    <span>{{ point }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Recommandations de l'IA -->
          <div v-if="profile?.recommendations && profile.recommendations.length > 0" class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title text-2xl">
                <Icon name="tabler:sparkles" size="28" />
                Recommandations de l'IA
              </h2>

              <div class="divider" />

              <div class="space-y-3">
                <div
                  v-for="(rec, idx) in profile.recommendations"
                  :key="idx"
                  class="alert"
                >
                  <Icon
                    name="tabler:bulb-filled"
                    size="20"
                    class="text-info"
                  />
                  <span>{{ rec }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Prochaines étapes -->
          <div v-if="profile?.next_steps && profile.next_steps.length > 0" class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title text-2xl">
                <Icon name="tabler:road-sign" size="28" />
                Prochaines étapes
              </h2>

              <div class="divider" />

              <div class="space-y-3">
                <div
                  v-for="(step, idx) in profile.next_steps"
                  :key="idx"
                  class="flex items-start gap-3 p-3 bg-base-200 rounded-lg"
                >
                  <div class="badge badge-lg badge-primary">
                    {{ idx + 1 }}
                  </div>
                  <p class="flex-1">
                    {{ step }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Colonne droite: Actions rapides -->
        <div class="space-y-6">
          <!-- Informations utilisateur -->
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title">
                <Icon name="tabler:user" size="24" />
                Mon profil
              </h2>

              <div class="divider" />

              <div class="space-y-3">
                <div>
                  <p class="text-sm opacity-70">
                    Nom d'utilisateur
                  </p>
                  <p class="font-semibold">
                    {{ user?.username }}
                  </p>
                </div>
                <div>
                  <p class="text-sm opacity-70">
                    Email
                  </p>
                  <p class="font-semibold text-sm">
                    {{ user?.email }}
                  </p>
                </div>
                <div>
                  <p class="text-sm opacity-70">
                    Niveau actuel
                  </p>
                  <div class="badge badge-lg mt-1" :class="levelColor">
                    {{ userLevel }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions rapides -->
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title">
                <Icon name="tabler:rocket" size="24" />
                Actions rapides
              </h2>

              <div class="divider" />

              <div class="space-y-3">
                <button
                  class="btn btn-primary w-full justify-start"
                  @click="goToQuestionnaire"
                >
                  <Icon name="tabler:clipboard-check" size="20" />
                  Refaire le questionnaire
                </button>
                <button class="btn btn-outline btn-primary w-full justify-start">
                  <Icon name="tabler:book" size="20" />
                  Parcourir les cours
                </button>
                <button class="btn btn-outline w-full justify-start">
                  <Icon name="tabler:certificate" size="20" />
                  Mes certifications
                </button>
                <button class="btn btn-outline w-full justify-start">
                  <Icon name="tabler:chart-bar" size="20" />
                  Mes statistiques
                </button>
              </div>
            </div>
          </div>

          <!-- Progression -->
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title">
                <Icon name="tabler:trending-up" size="24" />
                Progression
              </h2>

              <div class="divider" />

              <div class="space-y-4">
                <div>
                  <div class="flex justify-between mb-1">
                    <span class="text-sm">Questionnaire complété</span>
                    <span class="text-sm font-semibold">100%</span>
                  </div>
                  <progress
                    class="progress progress-primary"
                    value="100"
                    max="100"
                  />
                </div>
                <div>
                  <div class="flex justify-between mb-1">
                    <span class="text-sm">Cours suivis</span>
                    <span class="text-sm font-semibold">0%</span>
                  </div>
                  <progress
                    class="progress"
                    value="0"
                    max="100"
                  />
                </div>
                <div>
                  <div class="flex justify-between mb-1">
                    <span class="text-sm">Exercices réalisés</span>
                    <span class="text-sm font-semibold">0%</span>
                  </div>
                  <progress
                    class="progress"
                    value="0"
                    max="100"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Dashboard simple sans questionnaire -->
    <div v-else class="container mx-auto px-4 py-16">
      <div class="max-w-2xl mx-auto">
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body text-center">
            <div class="avatar placeholder mx-auto mb-6">
              <div class="bg-primary text-primary-content rounded-full w-24">
                <span class="text-3xl">{{ user?.username?.charAt(0).toUpperCase() }}</span>
              </div>
            </div>

            <h2 class="card-title text-3xl font-bold justify-center mb-2">
              Bienvenue ! 🎉
            </h2>

            <p class="text-lg mb-6">
              Vous êtes connecté, mais vous n'avez pas encore complété le questionnaire.
            </p>

            <div class="alert alert-info">
              <Icon name="tabler:info-circle" size="24" />
              <span>Complétez le questionnaire pour obtenir des recommandations personnalisées de notre IA.</span>
            </div>            <p class="text-center text-lg mb-6">
              Bienvenue sur votre tableau de bord
            </p>

            <div class="divider" />

            <div class="space-y-4">
              <div class="flex items-center gap-3 p-4 bg-base-200 rounded-lg">
                <Icon
                  name="tabler:user-filled"
                  size="24"
                  class="text-primary"
                />
                <div>
                  <p class="text-sm opacity-70">
                    Nom d'utilisateur
                  </p>
                  <p class="font-semibold">
                    {{ user?.username }}
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-3 p-4 bg-base-200 rounded-lg">
                <Icon
                  name="tabler:mail"
                  size="24"
                  class="text-primary"
                />
                <div>
                  <p class="text-sm opacity-70">
                    Email
                  </p>
                  <p class="font-semibold">
                    {{ user?.email }}
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-3 p-4 bg-base-200 rounded-lg">
                <Icon
                  name="tabler:id"
                  size="24"
                  class="text-primary"
                />
                <div>
                  <p class="text-sm opacity-70">
                    ID
                  </p>
                  <p class="font-semibold text-xs">
                    {{ user?.id }}
                  </p>
                </div>
              </div>
            </div>

            <div class="card-actions justify-center mt-6 gap-3">
              <button
                class="btn btn-primary"
                @click="goToQuestionnaire"
              >
                <Icon name="tabler:clipboard-check" size="20" />
                Questionnaire de diagnostic
              </button>
              <button class="btn btn-outline btn-primary">
                <Icon name="tabler:book" size="20" />
                Commencer les cours
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
