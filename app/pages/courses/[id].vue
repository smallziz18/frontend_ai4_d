<script setup lang="ts">
import { useCourses } from "~/composables/use-courses";

definePageMeta({
  middleware: ["auth"],
});

const route = useRoute();
const courseId = computed(() => route.params.id as string);
const { getCourseProgression, completeLesson, completeModule, isLoading } = useCourses();
const toast = useToast();

// États
const course = ref<any>(null);
const progression = ref<any>(null);
const currentModuleIndex = ref(0);
const currentLessonIndex = ref(0);
const showCompletionModal = ref(false);

// Charger les données du cours
onMounted(async () => {
  await loadCourse();
});

async function loadCourse() {
  try {
    const result = await getCourseProgression(courseId.value);

    if (result.success && result.data) {
      course.value = result.data.roadmap;
      progression.value = result.data.progression;

      // Trouver le module et la leçon actuelle
      if (progression.value) {
        const lastCompletedModule = progression.value.modules_completed?.length || 0;
        currentModuleIndex.value = Math.min(lastCompletedModule, (course.value.modules?.length || 1) - 1);
      }
    }
  }
  catch (err: any) {
    console.error("Erreur chargement cours:", err);
    toast.add({
      title: "Erreur",
      description: "Impossible de charger le cours",
      color: "error",
    });
  }
}

// Module et leçon actuels
const currentModule = computed(() => {
  if (!course.value?.modules)
    return null;
  return course.value.modules[currentModuleIndex.value];
});

const currentLesson = computed(() => {
  if (!currentModule.value?.ressources)
    return null;
  return currentModule.value.ressources[currentLessonIndex.value];
});

const hasNextLesson = computed(() => {
  return currentLessonIndex.value < (currentModule.value?.ressources?.length || 0) - 1;
});

const hasNextModule = computed(() => {
  return currentModuleIndex.value < (course.value?.modules?.length || 0) - 1;
});

// Navigation
function goToNextLesson() {
  if (hasNextLesson.value) {
    currentLessonIndex.value++;
  }
  else if (hasNextModule.value) {
    // Passer au module suivant
    showCompletionModal.value = true;
  }
}

function goToPreviousLesson() {
  if (currentLessonIndex.value > 0) {
    currentLessonIndex.value--;
  }
  else if (currentModuleIndex.value > 0) {
    // Retourner au module précédent
    currentModuleIndex.value--;
    currentLessonIndex.value = (course.value.modules[currentModuleIndex.value].ressources?.length || 1) - 1;
  }
}

async function handleCompleteModule() {
  try {
    const result = await completeModule(courseId.value, {
      module_id: currentModule.value.id,
      evaluation_score: 80, // Score par défaut
    });

    if (result.success) {
      toast.add({
        title: "✅ Module complété !",
        description: `Vous avez gagné ${result.data?.xp_gained || 100} XP`,
        color: "success",
      });

      // Passer au module suivant
      if (hasNextModule.value) {
        currentModuleIndex.value++;
        currentLessonIndex.value = 0;
      }

      showCompletionModal.value = false;
      await loadCourse();
    }
  }
  catch (err: any) {
    console.error("Erreur complétion module:", err);
    toast.add({
      title: "Erreur",
      description: "Impossible de compléter le module",
      color: "error",
    });
  }
}

async function handleCompleteLesson() {
  try {
    await completeLesson({
      lesson_id: currentLesson.value.id || `lesson_${currentModuleIndex.value}_${currentLessonIndex.value}`,
      time_spent_minutes: 30,
    });

    goToNextLesson();
  }
  catch (err: any) {
    console.error("Erreur complétion leçon:", err);
  }
}

// Progression du module
const moduleProgress = computed(() => {
  if (!currentModule.value?.ressources?.length)
    return 0;
  return Math.round((currentLessonIndex.value / currentModule.value.ressources.length) * 100);
});
</script>

<script lang="ts">
function getResourceIcon(type: string): string {
  const icons: Record<string, string> = {
    video: "tabler:video",
    cours: "tabler:book",
    article: "tabler:article",
    exercice: "tabler:code",
    projet: "tabler:rocket",
  };
  return icons[type] || "tabler:file";
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary/5 via-background-light to-secondary/5 dark:from-primary/10 dark:via-background-dark dark:to-secondary/10">
    <!-- Navbar -->
    <div class="navbar bg-base-100/80 backdrop-blur-sm shadow-sm">
      <div class="flex-1">
        <NuxtLink to="/courses" class="btn btn-ghost normal-case text-xl">
          <Icon name="tabler:arrow-left" size="24" />
          Retour aux cours
        </NuxtLink>
      </div>
      <div class="flex-none gap-2">
        <ThemeToggle />
      </div>
    </div>

    <!-- Chargement -->
    <div v-if="isLoading" class="container mx-auto px-4 py-8">
      <loading-spinner message="Chargement du cours..." />
    </div>

    <!-- Contenu du cours -->
    <div v-else-if="course && currentModule && currentLesson" class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- En-tête du cours -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl font-bold">
                {{ course.titre }}
              </h1>
              <p class="text-sm opacity-70 mt-2">
                Module {{ currentModuleIndex + 1 }}/{{ course.modules?.length || 0 }} - {{ currentModule.titre }}
              </p>
            </div>
            <div class="text-right">
              <div class="text-4xl font-bold text-primary">
                {{ moduleProgress }}%
              </div>
              <p class="text-sm opacity-70">
                Progression
              </p>
            </div>
          </div>

          <!-- Barre de progression -->
          <progress
            class="progress progress-primary w-full mt-4"
            :value="moduleProgress"
            max="100"
          />
        </div>
      </div>

      <!-- Contenu de la leçon -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Leçon principale -->
        <div class="lg:col-span-2">
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <h2 class="card-title text-2xl mb-4">
                <Icon
                  :name="getResourceIcon(currentLesson.type)"
                  size="32"
                  class="text-primary"
                />
                {{ currentLesson.titre }}
              </h2>

              <div class="prose max-w-none">
                <p class="text-lg mb-4">
                  {{ currentLesson.description }}
                </p>

                <!-- Informations sur la ressource -->
                <div class="stats shadow w-full mb-6">
                  <div class="stat">
                    <div class="stat-figure text-primary">
                      <Icon name="tabler:clock" size="32" />
                    </div>
                    <div class="stat-title">
                      Durée
                    </div>
                    <div class="stat-value text-primary text-2xl">
                      {{ currentLesson.duree_estimee || "1h" }}
                    </div>
                  </div>

                  <div class="stat">
                    <div class="stat-figure text-secondary">
                      <Icon name="tabler:star" size="32" />
                    </div>
                    <div class="stat-title">
                      Niveau
                    </div>
                    <div class="stat-value text-secondary text-2xl">
                      {{ currentLesson.niveau_requis || "Débutant" }}
                    </div>
                  </div>

                  <div class="stat">
                    <div class="stat-figure text-success">
                      <Icon name="tabler:check" size="32" />
                    </div>
                    <div class="stat-title">
                      Gratuit
                    </div>
                    <div class="stat-value text-success text-2xl">
                      {{ currentLesson.gratuit ? "Oui" : "Non" }}
                    </div>
                  </div>
                </div>

                <!-- Lien vers la ressource -->
                <a
                  :href="currentLesson.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-primary btn-lg w-full mb-6"
                >
                  <Icon name="tabler:external-link" size="24" />
                  Accéder à la ressource
                </a>

                <!-- Pourquoi recommandé -->
                <div v-if="currentLesson.pourquoi_recommande" class="alert alert-info mb-6">
                  <Icon name="tabler:bulb" size="24" />
                  <div>
                    <h3 class="font-bold">
                      Pourquoi cette ressource ?
                    </h3>
                    <div class="text-sm">
                      {{ currentLesson.pourquoi_recommande }}
                    </div>
                  </div>
                </div>

                <!-- Navigation -->
                <div class="flex justify-between gap-4">
                  <button
                    class="btn btn-outline"
                    :disabled="currentModuleIndex === 0 && currentLessonIndex === 0"
                    @click="goToPreviousLesson"
                  >
                    <Icon name="tabler:arrow-left" size="20" />
                    Précédent
                  </button>

                  <button
                    class="btn btn-primary"
                    @click="handleCompleteLesson"
                  >
                    {{ hasNextLesson ? "Suivant" : "Terminer le module" }}
                    <Icon name="tabler:arrow-right" size="20" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar - Plan du cours -->
        <div class="lg:col-span-1">
          <div class="card bg-base-100 shadow-xl sticky top-4">
            <div class="card-body">
              <h3 class="card-title text-lg mb-4">
                <Icon name="tabler:list" size="24" />
                Plan du module
              </h3>

              <ul class="menu menu-compact p-0">
                <li
                  v-for="(lesson, idx) in currentModule.ressources"
                  :key="idx"
                  :class="{ active: idx === currentLessonIndex }"
                >
                  <a
                    class="flex items-center gap-2"
                    @click="currentLessonIndex = idx"
                  >
                    <Icon
                      :name="idx < currentLessonIndex ? 'tabler:check' : 'tabler:circle'"
                      size="16"
                      :class="idx < currentLessonIndex ? 'text-success' : ''"
                    />
                    <span class="flex-1 truncate">{{ lesson.titre }}</span>
                  </a>
                </li>
              </ul>

              <!-- Modules suivants -->
              <div v-if="hasNextModule" class="mt-6">
                <div class="divider" />
                <h4 class="font-semibold text-sm mb-2">
                  Module suivant
                </h4>
                <p class="text-sm opacity-70">
                  {{ course.modules[currentModuleIndex + 1]?.titre }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de complétion du module -->
    <dialog :open="showCompletionModal" class="modal">
      <div class="modal-box">
        <h3 class="font-bold text-lg">
          🎉 Module complété !
        </h3>
        <p class="py-4">
          Félicitations ! Vous avez terminé toutes les leçons de ce module.
        </p>
        <p class="text-sm opacity-70 mb-4">
          Voulez-vous passer au module suivant ?
        </p>
        <div class="modal-action">
          <button class="btn btn-ghost" @click="showCompletionModal = false">
            Rester ici
          </button>
          <button class="btn btn-primary" @click="handleCompleteModule">
            Module suivant
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button @click="showCompletionModal = false">
          fermer
        </button>
      </form>
    </dialog>
  </div>
</template>
