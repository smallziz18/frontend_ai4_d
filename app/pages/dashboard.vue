<script setup lang="ts">
import { useProfile } from "~/composables/use-profile";
import { useAuth } from "~/data/use-auth";

definePageMeta({
  middleware: ["auth"],
});

const { user, logout, loadUserFromCookie } = useAuth();
const { profile, profileLoading, fetchProfile, fetchRecommendations, hasProfile } = useProfile();
const router = useRouter();

// État local
const error = ref("");
const showBadges = ref(false);

// Computed
const userLevel = computed(() => {
  if (!profile.value)
    return "Débutant";
  const niveau = profile.value.niveau || 1;
  if (niveau >= 8)
    return "Expert";
  if (niveau >= 6)
    return "Avancé";
  if (niveau >= 4)
    return "Intermédiaire";
  return "Débutant";
});

const levelColor = computed(() => {
  const level = userLevel.value.toLowerCase();
  if (level.includes("expert"))
    return "success";
  if (level.includes("avancé"))
    return "info";
  if (level.includes("intermédiaire"))
    return "warning";
  return "error";
});

const userXP = computed(() => profile.value?.xp || 0);
const userBadges = computed(() => profile.value?.badges || []);
const userCompetences = computed(() => profile.value?.competences || []);

// Charger les données au montage
onMounted(async () => {
  const accessToken = useCookie("access_token");
  if (!accessToken.value) {
    await navigateTo("/login");
    return;
  }

  await loadUserFromCookie();

  // Vérifier le flag de redirection pour éviter les boucles infinies
  const fromQuestionnaire = sessionStorage.getItem("from_questionnaire");

  // Vérifier si l'utilisateur a un profil
  const profileExists = await hasProfile();

  if (!profileExists && !fromQuestionnaire) {
    // Nouvel utilisateur sans profil -> rediriger vers questionnaire
    // Marquer qu'on vient du dashboard pour éviter la boucle
    sessionStorage.setItem("redirected_to_questionnaire", "true");
    await navigateTo("/questionnaire-v2");
    return;
  }

  if (!profileExists && fromQuestionnaire) {
    // Si on revient du questionnaire mais pas de profil, c'est une erreur
    error.value = "Erreur : Le profil n'a pas été créé correctement. Veuillez contacter le support.";
    sessionStorage.removeItem("from_questionnaire");
    return;
  }

  // Nettoyer le flag
  sessionStorage.removeItem("from_questionnaire");
  sessionStorage.removeItem("redirected_to_questionnaire");

  // Utilisateur existant -> charger le profil
  try {
    await fetchProfile();
    await fetchRecommendations();
  }
  catch (e: any) {
    error.value = "Erreur lors du chargement du profil";
    console.error(e);
  }
});

async function handleLogout() {
  await logout();
  await navigateTo("/login");
}

function goToQuestionnaire() {
  router.push("/questionnaire-v2");
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary/5 via-background-light to-secondary/5 dark:from-primary/10 dark:via-background-dark dark:to-secondary/10">
    <!-- Navbar -->
    <div class="navbar bg-base-100/80 backdrop-blur-sm shadow-sm sticky top-0 z-50">
      <div class="flex-1">
        <div class="flex items-center gap-2 text-primary dark:text-secondary px-4">
          <Icon name="tabler:school" size="32" />
          <h2 class="text-xl font-bold">
            AI-Edu
          </h2>
        </div>
      </div>
      <div class="flex-none gap-2">
        <!-- Theme Toggle -->
        <ThemeToggle />

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
        <button class="btn btn-ghost btn-sm" @click="handleLogout">
          <Icon name="tabler:logout" size="20" />
          Déconnexion
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="profileLoading" class="container mx-auto px-4 py-16">
      <LoadingSpinner message="Chargement de votre profil..." />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="container mx-auto px-4 py-8">
      <AlertMessage
        type="error"
        :message="error"
        :dismissible="true"
        @dismiss="error = ''"
      />
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="profile" class="container mx-auto px-4 py-8">
      <!-- Header -->
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
          <div class="badge badge-lg" :class="`badge-${levelColor}`">
            <Icon
              name="tabler:award"
              size="20"
              class="mr-1"
            />
            {{ userLevel }}
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Niveau"
          icon="tabler:trending-up"
          :value="profile.niveau || 1"
          description="Votre niveau actuel"
          color="primary"
        />
        <StatCard
          title="Expérience"
          icon="tabler:star-filled"
          :value="`${userXP} XP`"
          description="Points d'expérience gagnés"
          color="warning"
        />
        <StatCard
          title="Badges"
          icon="tabler:award-filled"
          :value="userBadges.length"
          description="Badges débloqués"
          color="success"
        />
      </div>

      <!-- Analyse du Profil -->
      <div v-if="profile.analyse_detaillee" class="card bg-base-100 shadow-xl mb-8">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">
            <Icon name="tabler:brain" size="28" />
            Analyse de votre Profil
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Points Forts -->
            <div>
              <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
                <Icon
                  name="tabler:check-circle"
                  size="24"
                  class="text-success"
                />
                Points Forts
              </h3>
              <ul class="space-y-2">
                <li
                  v-for="(point, idx) in profile.analyse_detaillee.points_forts || []"
                  :key="idx"
                  class="flex items-start gap-2"
                >
                  <Icon
                    name="tabler:check"
                    size="20"
                    class="text-success mt-0.5"
                  />
                  <span>{{ point }}</span>
                </li>
              </ul>
            </div>

            <!-- Points à Améliorer -->
            <div>
              <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
                <Icon
                  name="tabler:target"
                  size="24"
                  class="text-warning"
                />
                Points à Améliorer
              </h3>
              <ul class="space-y-2">
                <li
                  v-for="(point, idx) in profile.analyse_detaillee.points_ameliorer || []"
                  :key="idx"
                  class="flex items-start gap-2"
                >
                  <Icon
                    name="tabler:arrow-up"
                    size="20"
                    class="text-warning mt-0.5"
                  />
                  <span>{{ point }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Style d'apprentissage -->
          <div v-if="profile.analyse_detaillee.style_apprentissage" class="mt-6 p-4 bg-primary/5 rounded-lg">
            <h3 class="text-lg font-semibold mb-2 flex items-center gap-2">
              <Icon
                name="tabler:bulb"
                size="24"
                class="text-primary"
              />
              Votre Style d'Apprentissage
            </h3>
            <p class="text-sm">
              {{ profile.analyse_detaillee.style_apprentissage }}
            </p>
          </div>
        </div>
      </div>

      <!-- Compétences -->
      <div v-if="userCompetences.length > 0" class="card bg-base-100 shadow-xl mb-8">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">
            <Icon name="tabler:code" size="28" />
            Vos Compétences
          </h2>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(competence, idx) in userCompetences"
              :key="idx"
              class="badge badge-lg badge-primary gap-2"
            >
              <Icon name="tabler:check" size="16" />
              {{ competence }}
            </div>
          </div>
        </div>
      </div>

      <!-- Recommandations -->
      <div v-if="profile.recommandations && profile.recommandations.length > 0" class="card bg-base-100 shadow-xl mb-8">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">
            <Icon name="tabler:lightbulb" size="28" />
            Recommandations Personnalisées
          </h2>
          <ul class="space-y-3">
            <li
              v-for="(rec, idx) in profile.recommandations"
              :key="idx"
              class="flex items-start gap-3 p-3 bg-base-200 rounded-lg"
            >
              <Icon
                name="tabler:arrow-right"
                size="20"
                class="text-primary mt-1 flex-shrink-0"
              />
              <span>{{ rec }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Badges -->
      <div v-if="userBadges.length > 0" class="mb-8">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold flex items-center gap-2">
            <Icon name="tabler:award" size="28" />
            Vos Badges
          </h2>
          <button class="btn btn-sm btn-ghost" @click="showBadges = !showBadges">
            <Icon :name="showBadges ? 'tabler:chevron-up' : 'tabler:chevron-down'" size="20" />
          </button>
        </div>
        <div v-if="showBadges" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <BadgeCard
            v-for="(badge, idx) in userBadges"
            :key="idx"
            :name="badge"
            :earned="true"
            icon="tabler:award-filled"
          />
        </div>
      </div>

      <!-- Actions -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">
            <Icon name="tabler:rocket" size="28" />
            Actions Rapides
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <NuxtLink to="/courses" class="btn btn-primary btn-lg">
              <Icon name="tabler:book" size="24" />
              Parcourir les Cours
            </NuxtLink>
            <NuxtLink to="/ai-tutor" class="btn btn-secondary btn-lg">
              <Icon name="tabler:message-chatbot" size="24" />
              Chat avec l'IA
            </NuxtLink>
            <NuxtLink to="/leaderboard" class="btn btn-accent btn-lg">
              <Icon name="tabler:trophy" size="24" />
              Classement
            </NuxtLink>
            <NuxtLink to="/profile" class="btn btn-outline btn-lg">
              <Icon name="tabler:user" size="24" />
              Mon Profil
            </NuxtLink>
            <button class="btn btn-outline btn-lg" @click="goToQuestionnaire">
              <Icon name="tabler:clipboard-check" size="24" />
              Refaire le Questionnaire
            </button>
            <button class="btn btn-outline btn-lg">
              <Icon name="tabler:settings" size="24" />
              Paramètres
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Fallback si pas de profil -->
    <div v-else class="container mx-auto px-4 py-16 text-center">
      <Icon
        name="tabler:alert-circle"
        size="64"
        class="mx-auto text-warning mb-4"
      />
      <h2 class="text-2xl font-bold mb-4">
        Aucun profil trouvé
      </h2>
      <p class="mb-6">
        Vous devez d'abord compléter le questionnaire pour créer votre profil.
      </p>
      <button class="btn btn-primary btn-lg" @click="goToQuestionnaire">
        <Icon name="tabler:arrow-right" size="24" />
        Commencer le Questionnaire
      </button>
    </div>
  </div>
</template>
