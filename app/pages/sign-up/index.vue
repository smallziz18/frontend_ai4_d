<script setup lang="ts">
import { useSignup } from "~~/composables/use-signup";
import { ref } from "vue";

const { setBaseData } = useSignup();
const router = useRouter();

const userType = ref<"student" | "professor">("student");
const nom = ref("");
const prenom = ref("");
const username = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const error = ref("");
const showPassword = ref(false);
const showConfirmPassword = ref(false);

async function handleNext() {
  error.value = "";

  // Validation
  if (!nom.value || !prenom.value || !username.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = "Tous les champs sont requis";
    return;
  }

  if (password.value !== confirmPassword.value) {
    error.value = "Les mots de passe ne correspondent pas";
    return;
  }

  if (password.value.length < 8) {
    error.value = "Le mot de passe doit contenir au moins 8 caractères";
    return;
  }

  // Validation supplémentaire : vérifier complexité du mot de passe
  const hasUpperCase = /[A-Z]/.test(password.value);
  const hasLowerCase = /[a-z]/.test(password.value);
  const hasNumber = /\d/.test(password.value);

  if (!hasUpperCase || !hasLowerCase || !hasNumber) {
    error.value = "Le mot de passe doit contenir au moins une majuscule, une minuscule et un chiffre";
    return;
  }

  // Stocker les données de base
  setBaseData({
    nom: nom.value,
    prenom: prenom.value,
    username: username.value,
    email: email.value,
    motDePasseHash: password.value,
  });

  // Navigation vers la page appropriée
  try {
    if (userType.value === "student") {
      await router.push("/sign-up/etudiants");
    }
    else {
      await router.push("/sign-up/professors");
    }
  }
  catch (e) {
    console.error("Erreur de navigation:", e);
    error.value = "Erreur lors de la navigation";
  }
}
</script>

<template>
  <body class="bg-background-light dark:bg-background-dark font-display">
    <div class="relative flex min-h-screen w-full flex-col group/design-root overflow-x-hidden">
      <div class="layout-container flex h-full grow flex-col">
        <div class="flex flex-1">
          <div class="hidden lg:flex flex-1 items-center justify-center bg-teal-50 dark:bg-teal-900/20 p-8">
            <div class="w-full max-w-md">
              <img
                class="w-full h-auto rounded-xl object-cover"
                data-alt="A group of people working on laptops at a table."
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCx6VasBtSoftFyo3-1JK3x7rXwozNlykH-JJhXITocUqOQpwFNfDajLpI8OnWtvK1Kj18oyW7aKwtu2FcwGj3XG0qPizCsoTpeEMzpvRlrM-UdIf6WmzHNWaCUglVLzBm8bPM_RrX9KkGdutGYN9uKbkxEN2R0tTxe0aCZLHg45Xn5aCOoPaHz6e7_SIY4YLETGkJMHqZEiyJfD_ZdIHY48A7CPWVBuIR8GtVFgKD9WkTLlSJXfQ-nvBOj1ZWE4FuwgEBCjVbxMA"
              >
            </div>
          </div>
          <div class="flex flex-1 flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24">
            <div class="mx-auto w-full max-w-lg">
              <div class="flex flex-col gap-6">
                <div>
                  <p class="text-3xl font-bold text-gray-900 dark:text-white">
                    Create Your Account
                  </p>
                  <p class="mt-2 text-base text-gray-600 dark:text-gray-300">
                    Let's get started with your learning journey.
                  </p>
                </div>
                <div class="flex flex-col gap-2">
                  <p class="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Step 1 of 2
                  </p>
                  <div class="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                    <div class="h-2 w-1/2 rounded-full bg-primary" />
                  </div>
                </div>
              </div>

              <div v-if="error" class="mt-4 p-3 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-sm">
                {{ error }}
              </div>

              <form class="mt-8 space-y-4" @submit.prevent="handleNext">
                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div class="form-control">
                    <label class="label">
                      <span class="label-text">Nom</span>
                    </label>
                    <input
                      v-model="nom"
                      type="text"
                      class="input input-bordered w-full"
                      placeholder="Votre nom"
                      required
                    >
                  </div>
                  <div class="form-control">
                    <label class="label">
                      <span class="label-text">Prénom</span>
                    </label>
                    <input
                      v-model="prenom"
                      type="text"
                      class="input input-bordered w-full"
                      placeholder="Votre prénom"
                      required
                    >
                  </div>
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Username</span>
                  </label>
                  <input
                    v-model="username"
                    type="text"
                    class="input input-bordered w-full"
                    required
                    placeholder="Username"
                    pattern="[A-Za-z][A-Za-z0-9\-]*"
                    minlength="3"
                    maxlength="30"
                    title="Only letters, numbers or dash"
                  >
                  <label class="label">
                    <span class="label-text-alt">Must be 3 to 30 characters containing only letters, numbers or dash</span>
                  </label>
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Email address</span>
                  </label>
                  <input
                    v-model="email"
                    class="input input-bordered w-full"
                    type="email"
                    required
                    placeholder="mail@site.com"
                  >
                  <label class="label">
                    <span class="label-text-alt">Enter valid email address</span>
                  </label>
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Password</span>
                  </label>
                  <div class="relative">
                    <input
                      v-model="password"
                      :type="showPassword ? 'text' : 'password'"
                      class="input input-bordered w-full pr-10"
                      required
                      placeholder="Password"
                      minlength="8"
                    >
                    <button
                      type="button"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                      @click="showPassword = !showPassword"
                    >
                      <Icon
                        v-if="showPassword"
                        name="tabler:eye-off"
                        size="20"
                      />
                      <Icon
                        v-else
                        name="tabler:eye"
                        size="20"
                      />
                    </button>
                  </div>
                  <label class="label">
                    <span class="label-text-alt">Must be more than 8 characters, including at least one number, one lowercase letter, one uppercase letter</span>
                  </label>
                </div>

                <div class="form-control">
                  <label class="label">
                    <span class="label-text">Confirm Password</span>
                  </label>
                  <div class="relative">
                    <input
                      v-model="confirmPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      class="input input-bordered w-full pr-10"
                      :class="{ 'input-error': confirmPassword && password !== confirmPassword }"
                      required
                      placeholder="Confirm Password"
                    >
                    <button
                      type="button"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                      @click="showConfirmPassword = !showConfirmPassword"
                    >
                      <Icon
                        v-if="showConfirmPassword"
                        name="tabler:eye-off"
                        size="20"
                      />
                      <Icon
                        v-else
                        name="tabler:eye"
                        size="20"
                      />
                    </button>
                  </div>
                  <label v-if="confirmPassword && password !== confirmPassword" class="label">
                    <span class="label-text-alt text-error">Les mots de passe ne correspondent pas</span>
                  </label>
                  <label v-else-if="confirmPassword && password === confirmPassword" class="label">
                    <span class="label-text-alt text-success">✓ Les mots de passe correspondent</span>
                  </label>
                </div>

                <div class="form-control">
                  <label class="label cursor-pointer justify-start gap-4">
                    <span class="label-text text-sm font-medium">I am a...</span>
                    <input
                      v-model="userType"
                      type="checkbox"
                      class="toggle toggle-primary"
                      true-value="professor"
                      false-value="student"
                    >
                    <span class="label-text text-sm font-medium" :class="userType === 'professor' ? 'text-primary' : 'text-gray-500'">
                      {{ userType === 'student' ? 'Student' : 'Professor' }}
                    </span>
                  </label>
                </div>

                <button
                  type="submit"
                  class="btn btn-primary w-full"
                >
                  Next
                </button>

                <p class="text-center text-sm text-gray-600 dark:text-gray-400">
                  Already have an account? <NuxtLink to="/login" class="font-medium text-primary hover:underline">
                    Login
                  </NuxtLink>
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</template>
