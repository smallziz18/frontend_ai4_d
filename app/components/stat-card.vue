<script setup lang="ts">
defineProps<{
  title: string;
  icon?: string;
  value?: string | number;
  description?: string;
  color?: "primary" | "secondary" | "accent" | "success" | "warning" | "error";
}>();
</script>

<template>
  <div class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
    <div class="card-body">
      <div class="flex items-start justify-between">
        <h3 class="card-title text-lg">
          {{ title }}
        </h3>
        <Icon
          v-if="icon"
          :name="icon"
          size="32"
          :class="{
            'text-primary': color === 'primary',
            'text-secondary': color === 'secondary',
            'text-accent': color === 'accent',
            'text-success': color === 'success',
            'text-warning': color === 'warning',
            'text-error': color === 'error',
          }"
        />
      </div>
      <div v-if="value" class="text-3xl font-bold mt-2">
        {{ value }}
      </div>
      <p v-if="description" class="text-sm opacity-70 mt-2">
        {{ description }}
      </p>
      <slot />
    </div>
  </div>
</template>
