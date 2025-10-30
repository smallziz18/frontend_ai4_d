<script setup lang="ts">
import { useSignup } from "~~/composables/use-signup";
import { onMounted, ref } from "vue";

const { signupEtudiant, baseData } = useSignup();
const router = useRouter();

const techLevel = ref(7);
const energyLevel = ref(5);
const skills = ref<string[]>([]);
const newSkill = ref("");
const learningObjectives = ref("");
const motivation = ref("");
const error = ref("");
const loading = ref(false);

// Rediriger si pas de données de base
onMounted(() => {
  if (!baseData.value) {
    router.push("/sign-up");
  }
});

function addSkill() {
  const trimmedSkill = newSkill.value.trim();
  if (trimmedSkill && !skills.value.includes(trimmedSkill)) {
    skills.value.push(trimmedSkill);
    newSkill.value = "";
    console.log("Compétences actuelles:", skills.value);
  }
}

function removeSkill(index: number) {
  skills.value.splice(index, 1);
  console.log("Compétences après suppression:", skills.value);
}

function getTechLevelLabel(value: number) {
  if (value <= 3)
    return "Débutant";
  if (value <= 6)
    return "Intermédiaire";
  if (value <= 8)
    return "Avancé";
  return "Expert";
}

async function handleSubmit() {
  error.value = "";
  loading.value = true;

  try {
    await signupEtudiant({
      niveau_technique: techLevel.value,
      competences: skills.value,
      objectifs_apprentissage: learningObjectives.value,
      motivation: motivation.value,
      niveau_energie: energyLevel.value,
    });

    // Rediriger vers la page de vérification email après inscription réussie
    await router.push(`/verify-email?email=${encodeURIComponent(baseData.value?.email || "")}`);
  }
  catch (e: any) {
    error.value = e.message || "Erreur lors de l'inscription. Veuillez réessayer.";
    console.error("Erreur complète:", e);
  }
  finally {
    loading.value = false;
  }
}

function handleBack() {
  router.push("/sign-up");
}
</script>

<template>
  <body class="bg-background-light dark:bg-background-dark font-display">
    <div class="relative flex min-h-screen w-full flex-col overflow-x-hidden py-12">
      <div class="w-full max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col gap-8">
          <!-- Header -->
          <div>
            <h1 class="text-3xl md:text-4xl font-black text-gray-900 dark:text-white">
              Tell Us About Yourself
            </h1>
            <p class="mt-2 text-base text-gray-600 dark:text-gray-400">
              This will help our AI tailor the best experience for you.
            </p>
          </div>

          <!-- Progress Bar -->
          <div class="flex flex-col gap-2">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300">
              Step 2 of 2
            </p>
            <div class="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
              <div class="h-2 w-full rounded-full bg-primary" />
            </div>
          </div>

          <div v-if="error" class="p-3 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-sm">
            {{ error }}
          </div>

          <!-- Form -->
          <form class="space-y-8" @submit.prevent="handleSubmit">
            <!-- Niveau Technique -->
            <div class="w-full">
              <div class="flex justify-between items-center mb-2">
                <span class="text-base font-medium text-gray-900 dark:text-white">Niveau Technique</span>
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ techLevel }}/10 - {{ getTechLevelLabel(techLevel) }}</span>
              </div>
              <input
                v-model="techLevel"
                type="range"
                min="1"
                max="10"
                class="range range-primary w-full"
              >
              <div class="w-full flex justify-between text-xs text-gray-500 dark:text-gray-400 px-2 mt-2">
                <span>1</span>
                <span>5</span>
                <span>10</span>
              </div>
            </div>

            <!-- Compétences -->
            <div class="w-full">
              <label class="block text-base font-medium text-gray-900 dark:text-white mb-2">
                Compétences
              </label>
              <div class="join w-full">
                <input
                  v-model="newSkill"
                  type="text"
                  class="input input-bordered join-item flex-1"
                  placeholder="Enter a skill and press Enter"
                  @keyup.enter.prevent="addSkill"
                >
                <button
                  type="button"
                  class="btn btn-primary join-item"
                  @click="addSkill"
                >
                  <Icon name="tabler:plus" size="20" />
                </button>
              </div>
              <div v-if="skills.length > 0" class="flex gap-2 flex-wrap mt-3">
                <div
                  v-for="(skill, index) in skills"
                  :key="index"
                  class="badge badge-primary badge-lg gap-2"
                >
                  {{ skill }}
                  <button
                    type="button"
                    class="btn btn-ghost btn-xs btn-circle"
                    @click="removeSkill(index)"
                  >
                    <Icon name="tabler:x" size="16" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Objectifs d'apprentissage -->
            <div class="w-full">
              <label class="block text-base font-medium text-gray-900 dark:text-white mb-2">
                Objectifs d'apprentissage
              </label>
              <textarea
                v-model="learningObjectives"
                class="textarea textarea-bordered w-full h-28"
                placeholder="e.g., Master advanced prototyping techniques, improve my visual design skills..."
                required
              />
            </div>

            <!-- Motivation -->
            <div class="w-full">
              <label class="block text-base font-medium text-gray-900 dark:text-white mb-2">
                Motivation
              </label>
              <textarea
                v-model="motivation"
                class="textarea textarea-bordered w-full h-28"
                placeholder="What drives you to learn? What are you passionate about?"
                required
              />
            </div>

            <!-- Niveau d'énergie -->
            <div class="w-full">
              <div class="flex justify-between items-center mb-2">
                <span class="text-base font-medium text-gray-900 dark:text-white">Niveau d'énergie</span>
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ energyLevel }}/10</span>
              </div>
              <input
                v-model="energyLevel"
                type="range"
                min="1"
                max="10"
                class="range range-primary w-full"
              >
              <div class="w-full flex justify-between text-xs text-gray-500 dark:text-gray-400 px-2 mt-2">
                <span>1</span>
                <span>5</span>
                <span>10</span>
              </div>
            </div>

            <!-- Buttons -->
            <div class="flex justify-between items-center pt-4">
              <button
                type="button"
                class="btn btn-ghost"
                :disabled="loading"
                @click="handleBack"
              >
                Back
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="loading"
              >
                {{ loading ? "Création en cours..." : "Create Account" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </body>
</template>
