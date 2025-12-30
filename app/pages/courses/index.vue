<script setup lang="ts">
import { useCourses } from "~/composables/use-courses";

definePageMeta({
  middleware: ["auth"],
});

const { getActiveRoadmap, isLoading } = useCourses();
const router = useRouter();

// États
const roadmap = ref<any>(null);
const hasError = ref(false);

// Charger la roadmap au montage
onMounted(async () => {
  await loadRoadmap();
});

async function loadRoadmap() {
  try {
    const result = await getActiveRoadmap();

    if (result.success && result.data) {
      const data = result.data as any;
      if (data.roadmap) {
        roadmap.value = data.roadmap;
      }
      else {
        hasError.value = true;
      }
    }
    else {
      hasError.value = true;
    }
  }
  catch (err: any) {
    console.error("Erreur chargement roadmap:", err);
    hasError.value = true;
  }
}

// Naviguer vers un cours
function goToCourse(courseId: string) {
  router.push(`/courses/${courseId}`);
}

// Calculer la progression totale
const totalProgress = computed(() => {
  if (!roadmap.value?.modules)
    return 0;

  const totalModules = roadmap.value.modules.length;
  const completedModules = roadmap.value.modules.filter((m: any) => m.completed).length;

  return Math.round((completedModules / totalModules) * 100);
});
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
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="container mx-auto px-4 py-8 max-w-7xl">
      <!-- En-tête -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold mb-2">
          📚 Mes Cours
        </h1>
        <p class="text-lg opacity-70">
          Votre parcours d'apprentissage personnalisé en Intelligence Artificielle
        </p>
      </div>

      <!-- Chargement -->
      <div v-if="isLoading" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <loading-spinner message="Chargement de votre roadmap..." />
        </div>
      </div>

      <!-- Erreur -->
      <div v-else-if="hasError" class="card bg-base-100 shadow-xl">
        <div class="card-body text-center py-12">
          <Icon
            name="tabler:alert-circle"
            size="64"
            class="mx-auto text-error mb-4"
          />
          <h3 class="text-2xl font-bold mb-4">
            Aucune roadmap trouvée
          </h3>
          <p class="mb-6">
            Vous n'avez pas encore de parcours d'apprentissage personnalisé.
          </p>
          <NuxtLink to="/dashboard" class="btn btn-primary">
            Générer ma roadmap
          </NuxtLink>
        </div>
      </div>

      <!-- Roadmap chargée -->
      <div v-else-if="roadmap">
        <!-- Carte de progression globale -->
        <div class="card bg-base-100 shadow-xl mb-8">
          <div class="card-body">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h2 class="text-2xl font-bold">
                  {{ roadmap.titre }}
                </h2>
                <p class="opacity-70">
                  {{ roadmap.description }}
                </p>
              </div>
              <div class="text-right">
                <div class="text-4xl font-bold text-primary">
                  {{ totalProgress }}%
                </div>
                <p class="text-sm opacity-70">
                  Complétion
                </p>
              </div>
            </div>

            <!-- Barre de progression -->
            <progress
              class="progress progress-primary w-full"
              :value="totalProgress"
              max="100"
            />

            <!-- Informations additionnelles -->
            <div class="stats shadow mt-4">
              <div class="stat">
                <div class="stat-figure text-primary">
                  <Icon name="tabler:book" size="32" />
                </div>
                <div class="stat-title">
                  Modules
                </div>
                <div class="stat-value text-primary">
                  {{ roadmap.modules?.length || 0 }}
                </div>
              </div>

              <div class="stat">
                <div class="stat-figure text-secondary">
                  <Icon name="tabler:clock" size="32" />
                </div>
                <div class="stat-title">
                  Durée
                </div>
                <div class="stat-value text-secondary">
                  {{ roadmap.duree_totale }}
                </div>
              </div>

              <div class="stat">
                <div class="stat-figure text-accent">
                  <Icon name="tabler:target" size="32" />
                </div>
                <div class="stat-title">
                  Niveau
                </div>
                <div class="stat-value text-accent">
                  {{ roadmap.niveau }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Liste des modules -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="(module, idx) in roadmap.modules"
            :key="idx"
            class="card bg-base-100 shadow-xl hover:shadow-2xl transition-all cursor-pointer"
            @click="goToCourse(roadmap.course_id)"
          >
            <div class="card-body">
              <!-- Badge étape -->
              <div class="badge badge-primary mb-2">
                Étape {{ module.etape || idx + 1 }}
              </div>

              <!-- Titre -->
              <h3 class="card-title text-xl mb-2">
                {{ module.titre }}
              </h3>

              <!-- Objectif -->
              <p class="text-sm opacity-70 mb-4">
                {{ module.objectif }}
              </p>

              <!-- Durée -->
              <div class="flex items-center gap-2 text-sm mb-4">
                <Icon name="tabler:clock" size="16" />
                <span>{{ module.duree_totale || "2-4h" }}</span>
              </div>

              <!-- Ressources -->
              <div class="flex items-center gap-2 text-sm mb-4">
                <Icon name="tabler:books" size="16" />
                <span>{{ module.ressources?.length || 0 }} ressources</span>
              </div>

              <!-- Progression -->
              <div class="mt-auto">
                <div class="flex items-center justify-between text-sm mb-2">
                  <span>Progression</span>
                  <span class="font-semibold">{{ module.completed ? 100 : 0 }}%</span>
                </div>
                <progress
                  class="progress progress-primary w-full"
                  :value="module.completed ? 100 : 0"
                  max="100"
                />
              </div>

              <!-- Actions -->
              <div class="card-actions justify-end mt-4">
                <button
                  class="btn btn-primary btn-sm"
                  @click.stop="goToCourse(roadmap.course_id)"
                >
                  {{ module.completed ? "Revoir" : "Commencer" }}
                  <Icon name="tabler:arrow-right" size="16" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Ressources globales -->
        <div v-if="roadmap.ressources_globales" class="mt-8">
          <h2 class="text-2xl font-bold mb-4">
            📖 Ressources complémentaires
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Vidéos YouTube -->
            <div v-if="roadmap.ressources_globales.videos_youtube?.length" class="card bg-base-100 shadow-xl">
              <div class="card-body">
                <h3 class="card-title">
                  <Icon
                    name="tabler:brand-youtube"
                    size="24"
                    class="text-error"
                  />
                  Vidéos YouTube
                </h3>
                <ul class="space-y-2">
                  <li
                    v-for="(video, idx) in roadmap.ressources_globales.videos_youtube.slice(0, 3)"
                    :key="idx"
                  >
                    <a
                      :href="video.url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="link link-hover flex items-center gap-2"
                    >
                      <Icon name="tabler:external-link" size="16" />
                      {{ video.titre }}
                    </a>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Cours en ligne -->
            <div v-if="roadmap.ressources_globales.cours_en_ligne?.length" class="card bg-base-100 shadow-xl">
              <div class="card-body">
                <h3 class="card-title">
                  <Icon
                    name="tabler:school"
                    size="24"
                    class="text-primary"
                  />
                  Cours en ligne
                </h3>
                <ul class="space-y-2">
                  <li
                    v-for="(cours, idx) in roadmap.ressources_globales.cours_en_ligne.slice(0, 3)"
                    :key="idx"
                  >
                    <a
                      :href="cours.url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="link link-hover flex items-center gap-2"
                    >
                      <Icon name="tabler:external-link" size="16" />
                      {{ cours.titre }}
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
