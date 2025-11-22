<script setup lang="ts">
import { onMounted, ref } from "vue";

import { useSignup } from "~/composables/use-signup";

const { signupProfesseur, baseData } = useSignup();

const techLevel = ref(7);
const specialites = ref<string[]>([]);
const newSpecialite = ref("");
const niveauExperience = ref("");
const motivationPrincipale = ref("");
const error = ref("");
const loading = ref(false);

// Rediriger si pas de données de base
onMounted(() => {
  if (!baseData.value) {
    navigateTo("/sign-up");
  }
});

function addSpecialite() {
  if (newSpecialite.value.trim() && !specialites.value.includes(newSpecialite.value.trim())) {
    specialites.value.push(newSpecialite.value.trim());
    newSpecialite.value = "";
  }
}

function removeSpecialite(index: number) {
  specialites.value.splice(index, 1);
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

  if (!niveauExperience.value || !motivationPrincipale.value) {
    error.value = "Veuillez remplir tous les champs requis";
    return;
  }

  loading.value = true;

  try {
    await signupProfesseur({
      niveau_experience: niveauExperience.value,
      specialites: specialites.value,
      motivation_principale: motivationPrincipale.value,
      niveau_technologique: techLevel.value,
    });

    // Rediriger vers la page de vérification email après inscription réussie
    await navigateTo(`/verify-email?email=${encodeURIComponent(baseData.value?.email || "")}`);
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
  navigateTo("/sign-up");
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
              Tell Us About Your Experience
            </h1>
            <p class="mt-2 text-base text-gray-600 dark:text-gray-400">
              This will help us understand your teaching profile.
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
            <!-- Niveau d'expérience -->
            <div class="w-full">
              <label class="block text-base font-medium text-gray-900 dark:text-white mb-2">
                Niveau d'expérience
              </label>
              <select
                v-model="niveauExperience"
                class="select select-bordered w-full"
                required
              >
                <option value="" disabled>
                  Sélectionnez votre niveau d'expérience
                </option>
                <option value="Débutant">
                  Débutant (moins de 2 ans)
                </option>
                <option value="Intermédiaire">
                  Intermédiaire (2-5 ans)
                </option>
                <option value="Avancé">
                  Avancé (5-10 ans)
                </option>
                <option value="Expert">
                  Expert (plus de 10 ans)
                </option>
              </select>
            </div>

            <!-- Niveau Technologique -->
            <div class="w-full">
              <div class="flex justify-between items-center mb-2">
                <span class="text-base font-medium text-gray-900 dark:text-white">Niveau Technologique</span>
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

            <!-- Spécialités -->
            <div class="w-full">
              <label class="block text-base font-medium text-gray-900 dark:text-white mb-2">
                Spécialités
              </label>
              <div class="join w-full">
                <input
                  v-model="newSpecialite"
                  type="text"
                  class="input input-bordered join-item flex-1"
                  placeholder="Enter a specialty and press Enter"
                  @keyup.enter.prevent="addSpecialite"
                >
                <button
                  type="button"
                  class="btn btn-primary join-item"
                  @click="addSpecialite"
                >
                  <Icon name="tabler:plus" size="20" />
                </button>
              </div>
              <div v-if="specialites.length > 0" class="flex gap-2 flex-wrap mt-3">
                <div
                  v-for="(specialite, index) in specialites"
                  :key="index"
                  class="badge badge-primary badge-lg gap-2"
                >
                  {{ specialite }}
                  <button
                    type="button"
                    class="btn btn-ghost btn-xs btn-circle"
                    @click="removeSpecialite(index)"
                  >
                    <Icon name="tabler:x" size="16" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Motivation principale -->
            <div class="w-full">
              <label class="block text-base font-medium text-gray-900 dark:text-white mb-2">
                Motivation principale
              </label>
              <textarea
                v-model="motivationPrincipale"
                class="textarea textarea-bordered w-full h-28"
                placeholder="What motivates you to teach? What do you hope to achieve with your students?"
                required
              />
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
