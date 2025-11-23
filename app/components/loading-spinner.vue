<script setup lang="ts">
defineProps<{
  message?: string;
  size?: "sm" | "md" | "lg";
}>();
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 p-8">
    <span
      class="loading loading-spinner text-primary"
      :class="{
        'loading-sm': size === 'sm',
        'loading-md': size === 'md',
        'loading-lg': !size || size === 'lg',
      }"
    />
    <p v-if="message" class="text-center text-gray-600 dark:text-gray-400">
      {{ message }}
    </p>
  </div>
</template>
