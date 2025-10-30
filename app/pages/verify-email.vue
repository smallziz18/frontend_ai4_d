<script setup lang="ts">
const route = useRoute();
const email = ref(route.query.email as string || "");
const resendLoading = ref(false);
const resendSuccess = ref(false);
const resendError = ref("");

async function resendVerificationEmail() {
  if (!email.value)
    return;

  resendLoading.value = true;
  resendError.value = "";
  resendSuccess.value = false;

  try {
    await useFetch(`http://127.0.0.1:8000/api/auth/v1/resend-verification`, {
      method: "POST",
      body: { email: email.value },
    });

    resendSuccess.value = true;
  }
  catch (e) {
    resendError.value = "Erreur lors de l'envoi de l'email. Veuillez réessayer.";
    console.error(e);
  }
  finally {
    resendLoading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body items-center text-center">
          <!-- Icon -->
          <div class="mb-4">
            <div class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
              <Icon
                name="tabler:mail-check"
                size="48"
                class="text-primary"
              />
            </div>
          </div>

          <!-- Title -->
          <h2 class="card-title text-2xl font-bold mb-2">
            Vérifiez votre email
          </h2>

          <!-- Description -->
          <div class="space-y-3 mb-6">
            <p class="text-base opacity-80">
              Nous avons envoyé un email de vérification à :
            </p>
            <p class="font-semibold text-primary">
              {{ email }}
            </p>
            <p class="text-sm opacity-70">
              Cliquez sur le lien dans l'email pour activer votre compte.
            </p>
          </div>

          <!-- Divider -->
          <div class="divider">
            Vous n'avez pas reçu l'email ?
          </div>

          <!-- Resend Button -->
          <div class="w-full space-y-3">
            <div v-if="resendSuccess" class="alert alert-success">
              <Icon name="tabler:check" size="20" />
              <span>Email renvoyé avec succès !</span>
            </div>

            <div v-if="resendError" class="alert alert-error">
              <Icon name="tabler:alert-circle" size="20" />
              <span>{{ resendError }}</span>
            </div>

            <button
              class="btn btn-outline btn-primary w-full"
              :disabled="resendLoading || resendSuccess"
              @click="resendVerificationEmail"
            >
              <Icon
                v-if="!resendLoading"
                name="tabler:mail-forward"
                size="20"
              />
              <span v-if="resendLoading" class="loading loading-spinner loading-sm" />
              {{ resendLoading ? "Envoi en cours..." : "Renvoyer l'email" }}
            </button>

            <div class="text-sm opacity-70">
              <p class="mb-2">
                Vérifiez aussi votre dossier spam.
              </p>
              <p>L'email peut prendre quelques minutes pour arriver.</p>
            </div>
          </div>

          <!-- Back to Login -->
          <div class="divider" />

          <NuxtLink to="/login" class="btn btn-ghost btn-sm">
            <Icon name="tabler:arrow-left" size="16" />
            Retour à la connexion
          </NuxtLink>
        </div>
      </div>

      <!-- Help Section -->
      <div class="mt-6 text-center">
        <p class="text-sm opacity-70">
          Besoin d'aide ?
          <a href="#" class="link link-primary">Contactez le support</a>
        </p>
      </div>
    </div>
  </div>
</template>
