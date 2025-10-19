<script setup lang="ts">
import { ref } from "vue";

const userType = ref<"student" | "professor">("student");

function handleNext() {
  if (userType.value === "student") {
    navigateTo("/sign-up/etudiants");
  }
  else {
    navigateTo("/sign-up/professors");
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
              <form class="mt-8 space-y-4" @submit.prevent="handleNext">
                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <fieldset class="flex flex-col">
                    <legend class="fieldset-legend">
                      What is your name?
                    </legend>
                    <input
                      type="text"
                      class="input"
                    >
                  </fieldset>
                  <fieldset class="flex flex-col">
                    <legend class="fieldset-legend">
                      What is your last name?
                    </legend>
                    <input
                      type="text"
                      class="input"
                    >
                  </fieldset>
                </div>
                <fieldset class="flex flex-col">
                  <legend class="fieldset-legend">
                    Username
                  </legend>
                  <input
                    type="text"
                    class="input validator flex w-full min-w-0"
                    required
                    placeholder="Username"
                    pattern="[A-Za-z][A-Za-z0-9\-]*"
                    minlength="3"
                    maxlength="30"
                    title="Only letters, numbers or dash"
                  >
                  <p class="validator-hint">
                    Must be 3 to 30 characters containing only letters, numbers or dash
                  </p>
                </fieldset>
                <fieldset class="flex flex-col">
                  <legend class="fieldset-legend">
                    Email address
                  </legend>
                  <input
                    class="input validator flex w-full"
                    type="email"
                    required
                    placeholder="mail@site.com"
                  >
                  <div class="validator-hint">
                    Enter valid email address
                  </div>
                </fieldset>
                <fieldset class="flex flex-col">
                  <legend class="fieldset-legend">
                    Password
                  </legend>
                  <input
                    type="password"
                    class="input validator flex w-full"
                    required
                    placeholder="Password"
                    minlength="8"
                    pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
                    title="Must be more than 8 characters, including number, lowercase letter, uppercase letter"
                  >
                  <p class="validator-hint">
                    Must be more than 8 characters, including at least one number, one lowercase letter, one uppercase letter
                  </p>
                </fieldset>
                <fieldset class="flex flex-col">
                  <legend class="fieldset-legend">
                    Confirm Password
                  </legend>
                  <input
                    type="password"
                    class="input validator flex w-full"
                    required
                    placeholder="Confirm Password"
                  >
                </fieldset>
                <div class="form-control">
                  <label class="label cursor-pointer justify-start gap-4">
                    <span class="label-text text-sm font-medium text-gray-700 dark:text-gray-300">I am a...</span>
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
                  class="flex w-full justify-center rounded-lg bg-primary py-3 px-4 text-sm font-semibold text-white shadow-sm hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 dark:ring-offset-background-dark"
                >
                  Next
                </button>
                <p class="text-center text-sm text-gray-600 dark:text-gray-400">
                  Already have an account? <a class="font-medium text-primary hover:underline" href="#">Login</a>
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</template>
