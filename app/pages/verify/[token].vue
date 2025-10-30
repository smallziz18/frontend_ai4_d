<script setup lang="ts">
const route = useRoute();
const token = route.params.token as string;
const verifying = ref(true);
const verified = ref(false);
const error = ref("");

onMounted(async () => {
  if (!token) {
    error.value = "Token de vérification manquant";
    verifying.value = false;
    return;
  }

  try {
    const { data, error: fetchError } = await useFetch(`http://127.0.0.1:8000/api/auth/v1/verify/${token}`, {
      method: "GET",
    });

    if (fetchError.value) {
      error.value = "Le lien de vérification est invalide ou expiré.";
    }
    else if (data.value) {
      verified.value = true;
      // Rediriger automatiquement vers login après 3 secondes
      setTimeout(() => {
        navigateTo("/login?verified=true");
      }, 3000);
    }
  }
  catch (e) {
    error.value = "Une erreur est survenue lors de la vérification.";
    console.error(e);
  }
  finally {
    verifying.value = false;
  }
});

function redirectToLogin() {
  navigateTo("/login?verified=true");
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body items-center text-center">
          <!-- Loading State -->
          <div v-if="verifying" class="py-8">
            <span class="loading loading-spinner loading-lg text-primary" />
            <p class="mt-4 text-lg font-semibold">
              Vérification en cours...
            </p>
            <p class="text-sm opacity-70 mt-2">
              Veuillez patienter
            </p>
          </div>

          <!-- Success State -->
          <div v-else-if="verified" class="py-4">
            <div class="mb-4">
              <div class="w-20 h-20 bg-success/10 rounded-full flex items-center justify-center mx-auto">
                <Icon
                  name="tabler:circle-check"
                  size="48"
                  class="text-success"
                />
              </div>
            </div>

            <h2 class="card-title text-2xl font-bold mb-2 text-success">
              Email vérifié avec succès !
            </h2>

            <p class="text-base opacity-80 mb-2">
              Votre compte a été activé. Vous pouvez maintenant vous connecter.
            </p>

            <p class="text-sm opacity-60 mb-6">
              Redirection automatique dans 3 secondes...
            </p>

            <button class="btn btn-primary btn-wide" @click="redirectToLogin">
              <Icon name="tabler:login" size="20" />
              Se connecter maintenant
            </button>
          </div>

          <!-- Error State -->
          <div v-else class="py-4">
            <div class="mb-4">
              <div class="w-20 h-20 bg-error/10 rounded-full flex items-center justify-center mx-auto">
                <Icon
                  name="tabler:circle-x"
                  size="48"
                  class="text-error"
                />
              </div>
            </div>

            <h2 class="card-title text-2xl font-bold mb-2 text-error">
              Échec de la vérification
            </h2>

            <p class="text-base opacity-80 mb-6">
              {{ error }}
            </p>

            <div class="space-y-3 w-full">
              <button class="btn btn-primary btn-wide" @click="redirectToLogin">
                <Icon name="tabler:arrow-left" size="20" />
                Retour à la connexion
              </button>

              <div class="divider">
                OU
              </div>

              <NuxtLink to="/verify-email" class="btn btn-outline btn-primary btn-wide">
                <Icon name="tabler:mail-forward" size="20" />
                Renvoyer l'email
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Help Section -->
      <div class="mt-6 text-center">
        <p class="text-sm opacity-70">
          Problème persistant ?
          <a href="#" class="link link-primary">Contactez le support</a>
        </p>
      </div>
    </div>
  </div>
</template>
