<script setup lang="ts">
defineProps<{
  type?: "info" | "success" | "warning" | "error";
  message: string;
  dismissible?: boolean;
}>();

const emit = defineEmits<{
  dismiss: [];
}>();
</script>

<template>
  <div
    class="alert"
    :class="{
      'alert-info': type === 'info',
      'alert-success': type === 'success',
      'alert-warning': type === 'warning',
      'alert-error': type === 'error',
    }"
  >
    <Icon
      :name="
        type === 'success'
          ? 'tabler:check-circle'
          : type === 'warning'
            ? 'tabler:alert-triangle'
            : type === 'error'
              ? 'tabler:alert-circle'
              : 'tabler:info-circle'
      "
      size="24"
    />
    <span>{{ message }}</span>
    <button
      v-if="dismissible"
      class="btn btn-sm btn-ghost"
      @click="emit('dismiss')"
    >
      <Icon name="tabler:x" size="20" />
    </button>
  </div>
</template>
