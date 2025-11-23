<script setup lang="ts">
const { isDark, themeIcon, toggleTheme } = useTheme();
</script>

<template>
  <button
    class="btn btn-ghost btn-circle"
    :aria-label="isDark ? 'Passer en mode clair' : 'Passer en mode sombre'"
    @click="toggleTheme"
  >
    <Icon :name="themeIcon" size="24" />
  </button>
</template>
