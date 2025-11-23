<script setup lang="ts">
// Le composant theme-toggle gère le thème
</script>

<template>
  <div class="navbar bg-base-300 shadow-sm">
    <div class="flex-1">
      <NuxtLink to="/" class="btn btn-soft btn-primary text-xl">
        AI4D School
      </NuxtLink>
    </div>
    <div class="flex-1">
      <NuxtLink to="/login" class="btn btn-outline btn-primary mr-2">
        Log in
      </NuxtLink>
      <NuxtLink to="/sign-up" class="btn btn-outline btn-info mr-2">
        Sign up
      </NuxtLink>
    </div>
    <div class="flex-none">
      <!-- Nouveau toggle de thème -->
      <ThemeToggle />
    </div>
  </div>
</template>
