<script setup lang="ts">
import { useProfile } from "~/composables/use-profile";
import { useAuth } from "~/data/use-auth";

definePageMeta({
  middleware: ["auth"],
});

const { user } = useAuth();
const { profile, profileLoading, fetchProfile } = useProfile();

const isEditing = ref(false);
const isSaving = ref(false);
const error = ref("");
const success = ref("");

// Formulaire d'édition
const editForm = ref({
  objectifs: "",
  motivation: "",
  energie: 5,
  competences: [] as string[],
});

const newCompetence = ref("");

// Charger le profil au montage
onMounted(async () => {
  try {
    await fetchProfile();
    if (profile.value) {
      editForm.value = {
        objectifs: profile.value.objectifs || "",
        motivation: profile.value.motivation || "",
        energie: profile.value.energie || 5,
        competences: [...(profile.value.competences || [])],
      };
    }
  }
  catch (e) {
    console.error("Erreur chargement profil:", e);
  }
});

// Ajouter une compétence
function addCompetence() {
  if (newCompetence.value.trim() && !editForm.value.competences.includes(newCompetence.value.trim())) {
    editForm.value.competences.push(newCompetence.value.trim());
    newCompetence.value = "";
  }
}

// Retirer une compétence
function removeCompetence(competence: string) {
  editForm.value.competences = editForm.value.competences.filter(c => c !== competence);
}

// Sauvegarder les modifications
async function saveProfile() {
  isSaving.value = true;
  error.value = "";
  success.value = "";

  try {
    const token = useCookie("access_token").value;
    await $fetch("/api/profile/v1/", {
      method: "PUT",
      baseURL: useRuntimeConfig().public.apiBase,
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: {
        objectifs: editForm.value.objectifs,
        motivation: editForm.value.motivation,
        energie: editForm.value.energie,
        competences: editForm.value.competences,
      },
    });

    success.value = "Profil mis à jour avec succès !";
    isEditing.value = false;
    await fetchProfile();

    setTimeout(() => {
      success.value = "";
    }, 3000);
  }
  catch (e: any) {
    error.value = "Erreur lors de la mise à jour du profil";
    console.error(e);
  }
  finally {
    isSaving.value = false;
  }
}

// Annuler l'édition
function cancelEdit() {
  if (profile.value) {
    editForm.value = {
      objectifs: profile.value.objectifs || "",
      motivation: profile.value.motivation || "",
      energie: profile.value.energie || 5,
      competences: [...(profile.value.competences || [])],
    };
  }
  isEditing.value = false;
  error.value = "";
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
    <div class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- Loading -->
      <div v-if="profileLoading" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <loading-spinner message="Chargement de votre profil..." />
        </div>
      </div>

      <!-- Content -->
      <div v-else-if="profile">
        <!-- Header -->
        <div class="card bg-base-100 shadow-xl mb-6">
          <div class="card-body">
            <div class="flex flex-col md:flex-row items-center md:items-start gap-6">
              <!-- Avatar -->
              <div class="avatar placeholder">
                <div class="bg-primary text-primary-content rounded-full w-24">
                  <span class="text-4xl">{{ user?.username?.charAt(0).toUpperCase() }}</span>
                </div>
              </div>

              <!-- Info -->
              <div class="flex-1 text-center md:text-left">
                <h1 class="text-3xl font-bold mb-2">
                  {{ user?.username }}
                </h1>
                <p class="text-sm opacity-70 mb-4">
                  {{ user?.email }}
                </p>
                <div class="flex flex-wrap gap-2 justify-center md:justify-start">
                  <div class="badge badge-lg badge-primary">
                    Niveau {{ profile.niveau }}
                  </div>
                  <div class="badge badge-lg badge-warning">
                    <Icon
                      name="tabler:star"
                      size="16"
                      class="mr-1"
                    />
                    {{ profile.xp }} XP
                  </div>
                  <div class="badge badge-lg badge-success">
                    <Icon
                      name="tabler:award"
                      size="16"
                      class="mr-1"
                    />
                    {{ profile.badges?.length || 0 }} badges
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div>
                <button
                  v-if="!isEditing"
                  class="btn btn-primary"
                  @click="isEditing = true"
                >
                  <Icon name="tabler:edit" size="20" />
                  Modifier
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Notifications -->
        <alert-message
          v-if="success"
          type="success"
          :message="success"
          :dismissible="true"
          class="mb-6"
          @dismiss="success = ''"
        />

        <alert-message
          v-if="error"
          type="error"
          :message="error"
          :dismissible="true"
          class="mb-6"
          @dismiss="error = ''"
        />

        <!-- Informations -->
        <div class="card bg-base-100 shadow-xl mb-6">
          <div class="card-body">
            <h2 class="card-title text-2xl mb-4">
              <Icon name="tabler:info-circle" size="28" />
              Informations
            </h2>

            <div class="space-y-4">
              <!-- Objectifs -->
              <div>
                <label class="label">
                  <span class="label-text font-semibold">Objectifs d'apprentissage</span>
                </label>
                <textarea
                  v-if="isEditing"
                  v-model="editForm.objectifs"
                  class="textarea textarea-bordered w-full"
                  rows="3"
                  placeholder="Décrivez vos objectifs..."
                />
                <p v-else class="text-sm p-3 bg-base-200 rounded-lg">
                  {{ profile.objectifs || "Non défini" }}
                </p>
              </div>

              <!-- Motivation -->
              <div>
                <label class="label">
                  <span class="label-text font-semibold">Motivation</span>
                </label>
                <textarea
                  v-if="isEditing"
                  v-model="editForm.motivation"
                  class="textarea textarea-bordered w-full"
                  rows="3"
                  placeholder="Qu'est-ce qui vous motive ?"
                />
                <p v-else class="text-sm p-3 bg-base-200 rounded-lg">
                  {{ profile.motivation || "Non définie" }}
                </p>
              </div>

              <!-- Niveau d'énergie -->
              <div>
                <label class="label">
                  <span class="label-text font-semibold">Niveau d'énergie</span>
                  <span class="label-text-alt">{{ editForm.energie }}/10</span>
                </label>
                <input
                  v-if="isEditing"
                  v-model.number="editForm.energie"
                  type="range"
                  min="1"
                  max="10"
                  class="range range-primary"
                >
                <div v-else>
                  <progress
                    class="progress progress-primary"
                    :value="profile.energie"
                    max="10"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Compétences -->
        <div class="card bg-base-100 shadow-xl mb-6">
          <div class="card-body">
            <h2 class="card-title text-2xl mb-4">
              <Icon name="tabler:code" size="28" />
              Compétences
            </h2>

            <!-- Add Competence (Edit Mode) -->
            <div v-if="isEditing" class="form-control mb-4">
              <div class="input-group">
                <input
                  v-model="newCompetence"
                  type="text"
                  placeholder="Ajouter une compétence..."
                  class="input input-bordered flex-1"
                  @keypress.enter="addCompetence"
                >
                <button
                  class="btn btn-primary"
                  @click="addCompetence"
                >
                  <Icon name="tabler:plus" size="20" />
                </button>
              </div>
            </div>

            <!-- Competences List -->
            <div class="flex flex-wrap gap-2">
              <div
                v-for="competence in isEditing ? editForm.competences : profile.competences"
                :key="competence"
                class="badge badge-lg gap-2"
                :class="isEditing ? 'badge-primary' : 'badge-outline'"
              >
                <Icon name="tabler:check" size="16" />
                {{ competence }}
                <button
                  v-if="isEditing"
                  class="btn btn-ghost btn-xs btn-circle"
                  @click="removeCompetence(competence)"
                >
                  <Icon name="tabler:x" size="14" />
                </button>
              </div>
            </div>

            <p v-if="editForm.competences.length === 0 && isEditing" class="text-sm opacity-70 mt-4">
              Ajoutez vos compétences techniques et soft skills
            </p>
          </div>
        </div>

        <!-- Actions (Edit Mode) -->
        <div v-if="isEditing" class="flex gap-4">
          <button
            class="btn btn-primary flex-1"
            :disabled="isSaving"
            @click="saveProfile"
          >
            <span v-if="!isSaving">
              <Icon name="tabler:check" size="20" />
              Sauvegarder
            </span>
            <span v-else class="loading loading-spinner" />
          </button>
          <button
            class="btn btn-ghost flex-1"
            :disabled="isSaving"
            @click="cancelEdit"
          >
            <Icon name="tabler:x" size="20" />
            Annuler
          </button>
        </div>

        <!-- Statistiques -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <stat-card
            title="Date d'inscription"
            icon="tabler:calendar"
            :value="new Date(profile.created_at).toLocaleDateString()"
            description="Membre depuis"
            color="primary"
          />
          <stat-card
            title="Dernière activité"
            icon="tabler:clock"
            :value="new Date(profile.updated_at).toLocaleDateString()"
            description="Mise à jour"
            color="secondary"
          />
          <stat-card
            title="Cours suivis"
            icon="tabler:book-open"
            value="2"
            description="En cours"
            color="warning"
          />
        </div>
      </div>
    </div>
  </div>
</template>
