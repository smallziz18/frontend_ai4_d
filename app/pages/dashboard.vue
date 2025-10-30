<script setup lang="ts">
import { useAuth } from "~/data/use-auth";

const { user, logout, loadUserFromCookie } = useAuth();

// Charger l'utilisateur depuis les cookies au montage
onMounted(() => {
  loadUserFromCookie();
});

async function handleLogout() {
  await logout();
  await navigateTo("/login");
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <div class="navbar bg-base-100 shadow-sm">
      <div class="flex-1">
        <div class="flex items-center gap-2 text-primary dark:text-secondary px-4">
          <Icon name="tabler:school" size="32" />
          <h2 class="text-xl font-bold">
            AI-Edu
          </h2>
        </div>
      </div>
      <div class="flex-none">
        <button
          class="btn btn-ghost btn-sm mx-2"
          @click="handleLogout"
        >
          <Icon name="tabler:logout" size="20" />
          Déconnexion
        </button>
      </div>
    </div>

    <div class="container mx-auto px-4 py-16">
      <div class="max-w-2xl mx-auto">
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <div class="flex items-center justify-center mb-6">
              <div class="avatar placeholder">
                <div class="bg-primary text-primary-content rounded-full w-24">
                  <span class="text-3xl">{{ user?.username?.charAt(0).toUpperCase() }}</span>
                </div>
              </div>
            </div>

            <h2 class="card-title text-3xl font-bold text-center justify-center mb-2">
              You are logged in! 🎉
            </h2>

            <p class="text-center text-lg mb-6">
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

            <div class="card-actions justify-center mt-6">
              <button class="btn btn-primary btn-wide">
                Commencer les cours
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
