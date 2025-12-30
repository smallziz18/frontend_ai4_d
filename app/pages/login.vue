<script setup lang="ts">
import { useProfile } from "~/composables/use-profile";
import { useAuth } from "~/data/use-auth";

definePageMeta({
  layout: "empty",
});

const { login } = useAuth();
const { hasProfile } = useProfile();
const route = useRoute();

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);
const successMessage = ref("");

// Vérifier si l'utilisateur vient de s'inscrire ou de vérifier son email
onMounted(() => {
  if (route.query.registered === "true") {
    successMessage.value = "Inscription réussie ! Vérifiez votre email pour activer votre compte.";
  }
  else if (route.query.verified === "true") {
    successMessage.value = "Email vérifié avec succès ! Vous pouvez maintenant vous connecter.";
  }
});

async function handleLogin() {
  error.value = "";
  successMessage.value = "";
  loading.value = true;

  try {
    await login(email.value, password.value);

    // Vérifier si l'utilisateur a déjà un profil (utilisateur existant)
    const profileExists = await hasProfile();

    if (profileExists) {
      // Utilisateur existant -> dashboard
      await navigateTo("/dashboard");
    }
    else {
      // Nouvel utilisateur -> questionnaire
      await navigateTo("/questionnaire");
    }
  }
  catch (e: any) {
    // Afficher le message d'erreur du backend (ex: compte non vérifié)
    error.value = e.message || "Identifiants incorrects";

    // Si le compte n'est pas vérifié, proposer de renvoyer l'email
    if (error.value.includes("vérifié") || error.value.includes("verified")) {
      error.value += " - Vérifiez votre email ou renvoyez un nouveau lien.";
    }
  }
  finally {
    loading.value = false;
  }
}
</script>

<template>
  <body class="bg-background-light dark:bg-background-dark font-display">
    <!-- Theme Toggle en haut à droite -->
    <div class="fixed top-4 right-4 z-50">
      <ThemeToggle />
    </div>

    <form class="relative flex min-h-screen w-full flex-col items-center justify-center bg-background-light dark:bg-background-dark group/design-root overflow-x-hidden" @submit.prevent="handleLogin">
      <div class="layout-container flex h-full grow flex-col w-full max-w-md px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col items-center justify-center py-12">
          <div class="flex flex-col items-center mb-8">
            <Icon name="tabler:book" size="48" />
            <p class="mt-2 text-xl font-bold text-slate-800 dark:text-slate-200">
              EduAI
            </p>
          </div>
          <div class="w-full">
            <div class="flex flex-wrap justify-center gap-3 p-4">
              <p class="text-slate-900 dark:text-slate-50 text-3xl sm:text-4xl font-black leading-tight tracking-[-0.033em] text-center">
                Welcome Back
              </p>
            </div>

            <div v-if="successMessage" class="mx-4 mb-4 p-3 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-sm">
              {{ successMessage }}
            </div>

            <div v-if="error" class="mx-4 mb-4 p-3 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-sm">
              {{ error }}
            </div>

            <div class="flex w-full flex-wrap items-end gap-4 px-4 py-3">
              <label class="flex flex-col min-w-40 flex-1">
                <p class="text-slate-800 dark:text-slate-200 text-base font-medium leading-normal pb-2">Email</p>
                <input
                  v-model="email"
                  type="email"
                  required
                  class="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-slate-900 dark:text-slate-50 focus:outline-0 focus:ring-2 focus:ring-primary/50 border-none bg-slate-200/50 dark:bg-slate-800/50 h-14 placeholder:text-slate-500 dark:placeholder:text-slate-400 p-4 text-base font-normal leading-normal"
                  placeholder="Enter your email"
                >
              </label>
            </div>
            <div class="flex w-full flex-wrap items-end gap-4 px-4 py-3">
              <label class="flex flex-col min-w-40 flex-1">
                <p class="text-slate-800 dark:text-slate-200 text-base font-medium leading-normal pb-2">Password</p>
                <div class="flex w-full flex-1 items-stretch rounded-lg">
                  <input
                    v-model="password"
                    type="password"
                    required
                    class="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-slate-900 dark:text-slate-50 focus:outline-0 focus:ring-2 focus:ring-primary/50 border-none bg-slate-200/50 dark:bg-slate-800/50 h-14 placeholder:text-slate-500 dark:placeholder:text-slate-400 p-4 text-base font-normal leading-normal"
                    placeholder="Enter your password"
                  >
                </div>
              </label>
            </div>
            <p class="text-primary text-sm font-medium leading-normal pb-3 pt-1 px-4 underline cursor-pointer text-right">
              Forgot Password?
            </p>
            <div class="flex px-4 py-3 justify-center mt-4">
              <button
                type="submit"
                :disabled="loading"
                class="flex min-w-[84px] w-full cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-5 bg-primary text-slate-50 text-base font-bold leading-normal tracking-[0.015em] hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="truncate">{{ loading ? 'Connexion...' : 'Log In' }}</span>
              </button>
            </div>
            <div class="flex justify-center items-center px-4 py-3">
              <p class="text-slate-600 dark:text-slate-400 text-sm font-normal">
                Don't have an account? <NuxtLink
                  to="/sign-up"
                  class="font-medium text-primary underline"
                >
                  Sign Up
                </NuxtLink>
              </p>
            </div>
          </div>
        </div>
      </div>
    </form>
  </body>
</template>
