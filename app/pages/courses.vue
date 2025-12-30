<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
});

const { getAllProgressions, getActiveRoadmap, isLoading } = useCourses();
const toast = useToast();

// États
const courses = ref<any[]>([]);
const roadmap = ref<any>(null);
const selectedFilter = ref("all");
const searchQuery = ref("");
const isGeneratingCourse = ref(false);
const showGenerateModal = ref(false);
const newCourseTopic = ref("");
const newCourseDuration = ref(6);

// Charger les cours au montage
onMounted(async () => {
  await loadCourses();
});

/**
 * Charger les cours depuis l'API
 */
async function loadCourses() {
  try {
    // Récupérer la roadmap active
    const roadmapResult = await getActiveRoadmap();

    // Récupérer toutes les progressions
    const progressionsResult = await getAllProgressions();

    if (roadmapResult.success && roadmapResult.data?.roadmap) {
      // Mapper les modules de la roadmap en cours
      roadmap.value = roadmapResult.data.roadmap;
      const progressions = progressionsResult.success ? progressionsResult.data?.progressions || [] : [];

      courses.value = roadmap.value.modules?.map((module: any, index: number) => {
        // Trouver la progression correspondante
        const progression = progressions.find((p: any) => p.course_id === roadmap.value.course_id);
        const moduleProgress = progression?.modules_completed?.includes(module.id) ? 100 : 0;

        return {
          id: module.id || `module_${index}`,
          title: module.titre || module.title || `Module ${index + 1}`,
          description: module.description || "Description du module",
          level: mapLevel(module.niveau || roadmap.value.niveau || "Débutant"),
          duration: module.duree_estimee || module.duree_totale || `${module.semaines || 2} semaines`,
          modules: module.ressources?.length || module.lecons?.length || module.lessons?.length || 5,
          enrolled: !!progression,
          progress: moduleProgress,
          image: getModuleIcon(module.titre || module.title),
          color: getModuleColor(index),
          tags: module.tags || extractTags(module.titre || module.title || ""),
        };
      }) || [];
    }

    // Si pas de roadmap, afficher un message
    if (courses.value.length === 0) {
      toast.add({
        title: "Aucun cours disponible",
        description: "Générez votre roadmap personnalisée pour commencer !",
        color: "info",
      });
    }
  }
  catch (error: any) {
    console.error("Erreur lors du chargement des cours:", error);
    toast.add({
      title: "Erreur",
      description: "Impossible de charger les cours",
      color: "error",
    });
  }
}

/**
 * Mapper le niveau
 */
function mapLevel(level: string): string {
  const levelMap: Record<string, string> = {
    débutant: "Débutant",
    beginner: "Débutant",
    intermédiaire: "Intermédiaire",
    intermediate: "Intermédiaire",
    avancé: "Avancé",
    advanced: "Avancé",
  };
  return levelMap[level.toLowerCase()] || level;
}

/**
 * Obtenir l'icône du module
 */
function getModuleIcon(title: string): string {
  const lowerTitle = title.toLowerCase();
  if (lowerTitle.includes("réseau") || lowerTitle.includes("neural"))
    return "tabler:network";
  if (lowerTitle.includes("vision") || lowerTitle.includes("image"))
    return "tabler:camera";
  if (lowerTitle.includes("nlp") || lowerTitle.includes("langage") || lowerTitle.includes("language"))
    return "tabler:message-language";
  if (lowerTitle.includes("génératif") || lowerTitle.includes("gan") || lowerTitle.includes("generative"))
    return "tabler:wand";
  if (lowerTitle.includes("renforcement") || lowerTitle.includes("reinforcement"))
    return "tabler:robot";
  return "tabler:brain";
}

/**
 * Obtenir la couleur du module
 */
function getModuleColor(index: number): string {
  const colors = ["primary", "secondary", "accent", "success", "warning", "error"];
  return colors[index % colors.length];
}

/**
 * Extraire les tags du titre
 */
function extractTags(title: string): string[] {
  const tags: string[] = [];
  const lowerTitle = title.toLowerCase();

  if (lowerTitle.includes("ia") || lowerTitle.includes("ai"))
    tags.push("IA");
  if (lowerTitle.includes("ml") || lowerTitle.includes("machine learning"))
    tags.push("ML");
  if (lowerTitle.includes("deep learning"))
    tags.push("Deep Learning");
  if (lowerTitle.includes("nlp"))
    tags.push("NLP");
  if (lowerTitle.includes("cnn") || lowerTitle.includes("vision"))
    tags.push("Computer Vision");
  if (lowerTitle.includes("gan"))
    tags.push("GAN");
  if (lowerTitle.includes("transformer"))
    tags.push("Transformers");

  return tags.length > 0 ? tags : ["IA"];
}

/**
 * Générer un nouveau cours avec l'IA
 */
async function generateNewCourse() {
  if (!newCourseTopic.value.trim()) {
    toast.add({
      title: "Erreur",
      description: "Veuillez entrer un sujet de cours",
      color: "error",
    });
    return;
  }

  isGeneratingCourse.value = true;

  try {
    const { generateCourse } = useCourses();
    const result = await generateCourse(newCourseTopic.value, newCourseDuration.value);

    if (result.success) {
      toast.add({
        title: "Cours généré !",
        description: "Votre nouveau cours a été créé avec succès",
        color: "success",
      });

      showGenerateModal.value = false;
      newCourseTopic.value = "";
      await loadCourses();
    }
    else {
      toast.add({
        title: "Erreur",
        description: result.error || "Impossible de générer le cours",
        color: "error",
      });
    }
  }
  catch {
    toast.add({
      title: "Erreur",
      description: "Une erreur s'est produite lors de la génération",
      color: "error",
    });
  }
  finally {
    isGeneratingCourse.value = false;
  }
}

// Filtrer les cours
const filteredCourses = computed(() => {
  let filtered = courses.value;

  // Filtre par statut
  if (selectedFilter.value === "enrolled") {
    filtered = filtered.filter(c => c.enrolled);
  }
  else if (selectedFilter.value === "available") {
    filtered = filtered.filter(c => !c.enrolled);
  }
  else if (selectedFilter.value === "beginner") {
    filtered = filtered.filter(c => c.level === "Débutant");
  }
  else if (selectedFilter.value === "intermediate") {
    filtered = filtered.filter(c => c.level === "Intermédiaire");
  }
  else if (selectedFilter.value === "advanced") {
    filtered = filtered.filter(c => c.level === "Avancé");
  }

  // Filtre par recherche
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(
      c =>
        c.title.toLowerCase().includes(query)
        || c.description.toLowerCase().includes(query)
        || c.tags.some(tag => tag.toLowerCase().includes(query)),
    );
  }

  return filtered;
});

// Statistiques
const stats = computed(() => ({
  total: courses.value.length,
  enrolled: courses.value.filter(c => c.enrolled).length,
  completed: 0,
  inProgress: courses.value.filter(c => c.enrolled && c.progress > 0).length,
}));

function getLevelBadgeColor(level: string) {
  if (level === "Débutant")
    return "badge-success";
  if (level === "Intermédiaire")
    return "badge-warning";
  return "badge-error";
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
            name="tabler:book-2"
            size="48"
            class="text-primary"
          />
          Catalogue de Cours
        </h1>
        <p class="text-xl opacity-70">
          Explorez nos cours d'Intelligence Artificielle
        </p>
      </div>

      <!-- Stats et Bouton Génération -->
      <div class="flex flex-col md:flex-row gap-4 mb-8">
        <div class="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
          <stat-card
            title="Cours Disponibles"
            icon="tabler:book"
            :value="stats.total"
            color="primary"
          />
          <stat-card
            title="Mes Cours"
            icon="tabler:book-open"
            :value="stats.enrolled"
            color="secondary"
          />
          <stat-card
            title="En Cours"
            icon="tabler:progress"
            :value="stats.inProgress"
            color="warning"
          />
          <stat-card
            title="Terminés"
            icon="tabler:check-circle"
            :value="stats.completed"
            color="success"
          />
        </div>

        <!-- Bouton Générer un Cours -->
        <button
          class="btn btn-primary gap-2"
          @click="showGenerateModal = true"
        >
          <Icon name="tabler:sparkles" size="20" />
          Générer un Cours IA
        </button>
      </div>

      <!-- Filters and Search -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <div class="flex flex-col md:flex-row gap-4">
            <!-- Search -->
            <div class="flex-1">
              <div class="form-control">
                <div class="input-group">
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Rechercher un cours..."
                    class="input input-bordered w-full"
                  >
                  <button class="btn btn-square">
                    <Icon name="tabler:search" size="20" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Filters -->
            <div class="flex gap-2 flex-wrap">
              <button
                class="btn btn-sm"
                :class="selectedFilter === 'all' ? 'btn-primary' : 'btn-ghost'"
                @click="selectedFilter = 'all'"
              >
                Tous
              </button>
              <button
                class="btn btn-sm"
                :class="selectedFilter === 'enrolled' ? 'btn-primary' : 'btn-ghost'"
                @click="selectedFilter = 'enrolled'"
              >
                Mes Cours
              </button>
              <button
                class="btn btn-sm"
                :class="selectedFilter === 'available' ? 'btn-primary' : 'btn-ghost'"
                @click="selectedFilter = 'available'"
              >
                Disponibles
              </button>
              <div class="divider divider-horizontal" />
              <button
                class="btn btn-sm"
                :class="selectedFilter === 'beginner' ? 'btn-success' : 'btn-ghost'"
                @click="selectedFilter = 'beginner'"
              >
                Débutant
              </button>
              <button
                class="btn btn-sm"
                :class="selectedFilter === 'intermediate' ? 'btn-warning' : 'btn-ghost'"
                @click="selectedFilter = 'intermediate'"
              >
                Intermédiaire
              </button>
              <button
                class="btn btn-sm"
                :class="selectedFilter === 'advanced' ? 'btn-error' : 'btn-ghost'"
                @click="selectedFilter = 'advanced'"
              >
                Avancé
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Courses Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="course in filteredCourses"
          :key="course.id"
          class="card bg-base-100 shadow-xl hover:shadow-2xl transition-all"
        >
          <div class="card-body">
            <!-- Header -->
            <div class="flex justify-between items-start mb-4">
              <div
                class="w-16 h-16 rounded-lg flex items-center justify-center"
                :class="`bg-${course.color}/10`"
              >
                <Icon
                  :name="course.image"
                  size="32"
                  :class="`text-${course.color}`"
                />
              </div>
              <div
                class="badge"
                :class="getLevelBadgeColor(course.level)"
              >
                {{ course.level }}
              </div>
            </div>

            <!-- Content -->
            <h3 class="card-title text-lg mb-2">
              {{ course.title }}
            </h3>
            <p class="text-sm opacity-70 mb-4">
              {{ course.description }}
            </p>

            <!-- Tags -->
            <div class="flex flex-wrap gap-1 mb-4">
              <div
                v-for="tag in course.tags"
                :key="tag"
                class="badge badge-sm badge-outline"
              >
                {{ tag }}
              </div>
            </div>

            <!-- Info -->
            <div class="flex gap-4 text-sm mb-4">
              <div class="flex items-center gap-1">
                <Icon name="tabler:clock" size="16" />
                {{ course.duration }}
              </div>
              <div class="flex items-center gap-1">
                <Icon name="tabler:book" size="16" />
                {{ course.modules }} modules
              </div>
            </div>

            <!-- Progress (if enrolled) -->
            <div v-if="course.enrolled" class="mb-4">
              <div class="flex justify-between text-xs mb-1">
                <span>Progression</span>
                <span>{{ course.progress }}%</span>
              </div>
              <progress
                class="progress progress-primary"
                :value="course.progress"
                max="100"
              />
            </div>

            <!-- Actions -->
            <div class="card-actions justify-end">
              <NuxtLink
                v-if="course.enrolled && roadmap?.course_id"
                :to="`/courses/${roadmap.course_id}/module/${course.id}`"
                class="btn btn-primary btn-sm"
              >
                <Icon name="tabler:arrow-right" size="16" />
                Commencer
              </NuxtLink>
              <button
                v-else
                class="btn btn-outline btn-sm"
                @click="toast.add({ title: 'Bientôt disponible', description: 'Cette fonctionnalité sera disponible prochainement', color: 'info' })"
              >
                <Icon name="tabler:lock" size="16" />
                Verrouillé
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="filteredCourses.length === 0 && !isLoading"
        class="card bg-base-100 shadow-xl"
      >
        <div class="card-body text-center py-16">
          <Icon
            name="tabler:search-off"
            size="64"
            class="mx-auto opacity-50 mb-4"
          />
          <h3 class="text-2xl font-semibold mb-2">
            Aucun cours trouvé
          </h3>
          <p class="opacity-70 mb-4">
            Essayez de modifier vos filtres ou générez votre roadmap personnalisée
          </p>
          <button
            class="btn btn-primary gap-2"
            @click="$router.push('/dashboard')"
          >
            <Icon name="tabler:route" size="20" />
            Générer ma Roadmap
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div
        v-if="isLoading"
        class="flex justify-center items-center py-16"
      >
        <loading-spinner size="lg" />
      </div>
    </div>

    <!-- Modal Génération de Cours -->
    <div
      v-if="showGenerateModal"
      class="modal modal-open"
    >
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">
          🤖 Générer un Cours avec l'IA
        </h3>

        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Sujet du cours</span>
          </label>
          <input
            v-model="newCourseTopic"
            type="text"
            placeholder="Ex: Transformers en NLP, GANs, etc."
            class="input input-bordered"
          >
        </div>

        <div class="form-control mb-6">
          <label class="label">
            <span class="label-text">Durée (semaines)</span>
          </label>
          <input
            v-model.number="newCourseDuration"
            type="number"
            min="2"
            max="16"
            class="input input-bordered"
          >
        </div>

        <div class="modal-action">
          <button
            class="btn"
            :disabled="isGeneratingCourse"
            @click="showGenerateModal = false"
          >
            Annuler
          </button>
          <button
            class="btn btn-primary gap-2"
            :disabled="isGeneratingCourse"
            @click="generateNewCourse"
          >
            <Icon
              v-if="!isGeneratingCourse"
              name="tabler:sparkles"
              size="20"
            />
            <span
              v-if="isGeneratingCourse"
              class="loading loading-spinner loading-sm"
            />
            {{ isGeneratingCourse ? "Génération..." : "Générer" }}
          </button>
        </div>
      </div>
      <div
        class="modal-backdrop"
        @click="showGenerateModal = false"
      />
    </div>
  </div>
</template>
