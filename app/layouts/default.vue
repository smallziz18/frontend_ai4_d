<script setup lang="ts">
const route = useRoute();

// Afficher la navbar uniquement sur la page d'accueil
const showNavBar = computed(() => route.path === "/");
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <NavBar v-if="showNavBar" />
    <main class="flex-1">
      <slot />
    </main>
    <Footer />
    <ToastContainer />
  </div>
</template>
