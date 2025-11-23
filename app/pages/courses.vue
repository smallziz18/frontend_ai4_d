<script setup lang="ts">
definePageMeta({
  middleware: ["auth"],
});

// Données simulées des cours (à remplacer par des vraies données de l'API)
const courses = ref([
  {
    id: 1,
    title: "Introduction à l'Intelligence Artificielle",
    description: "Découvrez les fondamentaux de l'IA et du Machine Learning",
    level: "Débutant",
    duration: "4 semaines",
    modules: 8,
    enrolled: false,
    progress: 0,
    image: "tabler:brain",
    color: "primary",
    tags: ["IA", "ML", "Débutant"],
  },
  {
    id: 2,
    title: "Réseaux de Neurones Profonds",
    description: "Maîtrisez les architectures de deep learning modernes",
    level: "Intermédiaire",
    duration: "6 semaines",
    modules: 12,
    enrolled: true,
    progress: 45,
    image: "tabler:network",
    color: "secondary",
    tags: ["Deep Learning", "Neural Networks"],
  },
  {
    id: 3,
    title: "Traitement du Langage Naturel",
    description: "Apprenez à traiter et comprendre le langage humain",
    level: "Intermédiaire",
    duration: "5 semaines",
    modules: 10,
    enrolled: false,
    progress: 0,
    image: "tabler:message-language",
    color: "accent",
    tags: ["NLP", "Transformers", "LLM"],
  },
  {
    id: 4,
    title: "Vision par Ordinateur",
    description: "Maîtrisez le traitement d'images et la reconnaissance visuelle",
    level: "Avancé",
    duration: "8 semaines",
    modules: 15,
    enrolled: false,
    progress: 0,
    image: "tabler:camera",
    color: "success",
    tags: ["Computer Vision", "CNN", "Image Processing"],
  },
  {
    id: 5,
    title: "IA Générative et GANs",
    description: "Créez des contenus avec les modèles génératifs",
    level: "Avancé",
    duration: "6 semaines",
    modules: 12,
    enrolled: false,
    progress: 0,
    image: "tabler:wand",
    color: "warning",
    tags: ["GAN", "Diffusion", "Génératif"],
  },
  {
    id: 6,
    title: "Apprentissage par Renforcement",
    description: "Entraînez des agents intelligents par essai-erreur",
    level: "Avancé",
    duration: "7 semaines",
    modules: 14,
    enrolled: true,
    progress: 20,
    image: "tabler:robot",
    color: "error",
    tags: ["RL", "Q-Learning", "Policy Gradient"],
  },
]);

const selectedFilter = ref("all");
const searchQuery = ref("");

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

      <!-- Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
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
              <button
                v-if="!course.enrolled"
                class="btn btn-primary btn-sm"
              >
                <Icon name="tabler:plus" size="16" />
                S'inscrire
              </button>
              <button
                v-else
                class="btn btn-primary btn-sm"
              >
                <Icon name="tabler:arrow-right" size="16" />
                Continuer
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="filteredCourses.length === 0"
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
          <p class="opacity-70">
            Essayez de modifier vos filtres ou votre recherche
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
