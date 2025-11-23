<script setup lang="ts">
import { useProfile } from "~/composables/use-profile";
import { useAuth } from "~/data/use-auth";

definePageMeta({
  middleware: ["auth"],
});

const { user } = useAuth();
const { profile } = useProfile();

const leaderboard = ref<any[]>([]);
const isLoading = ref(false);
const error = ref("");
const selectedFilter = ref("xp");

// Charger le leaderboard
async function loadLeaderboard() {
  isLoading.value = true;
  error.value = "";

  try {
    const token = useCookie("access_token").value;
    const response = await $fetch("/api/profile/v1/gamification/leaderboard-enriched?limit=50", {
      baseURL: useRuntimeConfig().public.apiBase,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    leaderboard.value = response as any[];
  }
  catch (e: any) {
    error.value = "Erreur lors du chargement du classement";
    console.error(e);
  }
  finally {
    isLoading.value = false;
  }
}

// Filtrer et trier le leaderboard
const filteredLeaderboard = computed(() => {
  if (!leaderboard.value)
    return [];

  const sorted = [...leaderboard.value];

  if (selectedFilter.value === "xp") {
    sorted.sort((a, b) => (b.xp || 0) - (a.xp || 0));
  }
  else if (selectedFilter.value === "level") {
    sorted.sort((a, b) => (b.niveau || 0) - (a.niveau || 0));
  }
  else if (selectedFilter.value === "badges") {
    sorted.sort((a, b) => (b.badges?.length || 0) - (a.badges?.length || 0));
  }
  else if (selectedFilter.value === "streak") {
    sorted.sort((a, b) => (b.streak || 0) - (a.streak || 0));
  }

  return sorted;
});

// Position de l'utilisateur actuel
const userPosition = computed(() => {
  return filteredLeaderboard.value.findIndex(p => p.is_me) + 1;
});

onMounted(() => {
  loadLeaderboard();
});

// Obtenir l'icône de médaille
function getMedalIcon(position: number) {
  if (position === 1)
    return "tabler:trophy";
  if (position === 2)
    return "tabler:medal";
  if (position === 3)
    return "tabler:medal-2";
  return null;
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
      <div class="flex-none">
        <ThemeToggle />
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto px-4 py-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-5xl font-bold mb-4 flex items-center justify-center gap-3">
          <Icon
            name="tabler:trophy"
            size="48"
            class="text-warning"
          />
          Classement
        </h1>
        <p class="text-xl opacity-70">
          Comparez vos performances avec les autres apprenants
        </p>
      </div>

      <!-- Votre Position -->
      <div v-if="profile" class="card bg-gradient-to-r from-primary to-secondary text-primary-content shadow-xl mb-6">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="avatar placeholder">
                <div class="bg-base-100 text-primary rounded-full w-16">
                  <span class="text-2xl">{{ user?.username?.charAt(0).toUpperCase() }}</span>
                </div>
              </div>
              <div>
                <h3 class="text-2xl font-bold">
                  {{ user?.username }}
                </h3>
                <p class="opacity-80">
                  Votre Position
                </p>
              </div>
            </div>
            <div class="text-right">
              <div class="text-4xl font-bold">
                #{{ userPosition }}
              </div>
              <div class="flex gap-2 mt-2">
                <div class="badge badge-lg">
                  <Icon
                    name="tabler:star"
                    size="16"
                    class="mr-1"
                  />
                  {{ profile.xp }} XP
                </div>
                <div class="badge badge-lg">
                  Niv. {{ profile.niveau }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtres -->
      <div class="flex justify-center gap-2 mb-6">
        <button
          class="btn"
          :class="selectedFilter === 'xp' ? 'btn-primary' : 'btn-ghost'"
          @click="selectedFilter = 'xp'"
        >
          <Icon name="tabler:star" size="20" />
          XP
        </button>
        <button
          class="btn"
          :class="selectedFilter === 'level' ? 'btn-primary' : 'btn-ghost'"
          @click="selectedFilter = 'level'"
        >
          <Icon name="tabler:trending-up" size="20" />
          Niveau
        </button>
        <button
          class="btn"
          :class="selectedFilter === 'badges' ? 'btn-primary' : 'btn-ghost'"
          @click="selectedFilter = 'badges'"
        >
          <Icon name="tabler:award" size="20" />
          Badges
        </button>
        <button
          class="btn"
          :class="selectedFilter === 'streak' ? 'btn-primary' : 'btn-ghost'"
          @click="selectedFilter = 'streak'"
        >
          <Icon name="tabler:flame" size="20" />
          Série
        </button>
      </div>

      <!-- Error -->
      <alert-message
        v-if="error"
        type="error"
        :message="error"
        :dismissible="true"
        class="mb-6"
        @dismiss="error = ''"
      />

      <!-- Loading -->
      <div v-if="isLoading" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <loading-spinner message="Chargement du classement..." />
        </div>
      </div>

      <!-- Leaderboard -->
      <div v-else class="card bg-base-100 shadow-xl">
        <div class="card-body p-0">
          <div class="overflow-x-auto">
            <table class="table table-zebra">
              <thead>
                <tr>
                  <th class="text-center">
                    Position
                  </th>
                  <th>Utilisateur</th>
                  <th class="text-center">
                    Niveau
                  </th>
                  <th class="text-center">
                    XP
                  </th>
                  <th class="text-center">
                    Badges
                  </th>
                  <th class="text-center">
                    Série
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, idx) in filteredLeaderboard"
                  :key="idx"
                  :class="{
                    'bg-primary/10': item.is_me,
                    'hover': !item.is_me,
                  }"
                >
                  <td class="text-center">
                    <div class="flex items-center justify-center gap-2">
                      <Icon
                        v-if="getMedalIcon(idx + 1)"
                        :name="getMedalIcon(idx + 1)!"
                        size="24"
                        :class="{
                          'text-warning': idx === 0,
                          'text-base-300': idx === 1,
                          'text-accent': idx === 2,
                        }"
                      />
                      <span class="font-bold text-lg">{{ idx + 1 }}</span>
                    </div>
                  </td>
                  <td>
                    <div class="flex items-center gap-3">
                      <div class="avatar placeholder">
                        <div
                          class="rounded-full w-10"
                          :class="item.is_me ? 'bg-primary text-primary-content' : 'bg-base-300'"
                        >
                          <span>{{ item.username?.charAt(0).toUpperCase() }}</span>
                        </div>
                      </div>
                      <div>
                        <div class="font-semibold flex items-center gap-2">
                          {{ item.username }}
                          <span v-if="item.is_me" class="badge badge-primary badge-sm">
                            Vous
                          </span>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="text-center">
                    <div class="badge badge-lg badge-ghost">
                      Niv. {{ item.niveau || 1 }}
                    </div>
                  </td>
                  <td class="text-center">
                    <div class="flex items-center justify-center gap-1">
                      <Icon
                        name="tabler:star-filled"
                        size="16"
                        class="text-warning"
                      />
                      <span class="font-semibold">{{ item.xp || 0 }}</span>
                    </div>
                  </td>
                  <td class="text-center">
                    <div class="badge badge-lg">
                      <Icon
                        name="tabler:award"
                        size="16"
                        class="mr-1"
                      />
                      {{ item.badges?.length || 0 }}
                    </div>
                  </td>
                  <td class="text-center">
                    <div class="flex items-center justify-center gap-1">
                      <Icon
                        name="tabler:flame"
                        size="16"
                        class="text-error"
                      />
                      <span class="font-semibold">{{ item.streak || 0 }}</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <stat-card
          title="Total Participants"
          icon="tabler:users"
          :value="leaderboard.length"
          description="Apprenants actifs"
          color="primary"
        />
        <stat-card
          title="Votre Position"
          icon="tabler:trophy"
          :value="`#${userPosition}`"
          :description="`Top ${Math.round((userPosition / leaderboard.length) * 100)}%`"
          color="warning"
        />
        <stat-card
          title="XP Moyen"
          icon="tabler:chart-line"
          :value="Math.round(leaderboard.reduce((sum, p) => sum + (p.xp || 0), 0) / leaderboard.length)"
          description="Sur la plateforme"
          color="success"
        />
      </div>
    </div>
  </div>
</template>
