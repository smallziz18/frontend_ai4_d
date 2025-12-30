<script setup lang="ts">
const { toasts, remove } = useToast();

function getAlertClass(color: string) {
  switch (color) {
    case "success":
      return "alert-success";
    case "warning":
      return "alert-warning";
    case "error":
      return "alert-error";
    default:
      return "alert-info";
  }
}

function getIcon(color: string) {
  switch (color) {
    case "success":
      return "tabler:check-circle";
    case "warning":
      return "tabler:alert-triangle";
    case "error":
      return "tabler:x-circle";
    default:
      return "tabler:info-circle";
  }
}
</script>

<template>
  <div class="toast toast-top toast-end z-50">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="alert"
      :class="getAlertClass(toast.color || 'info')"
    >
      <Icon :name="getIcon(toast.color || 'info')" size="20" />
      <div>
        <h3 class="font-bold">
          {{ toast.title }}
        </h3>
        <div v-if="toast.description" class="text-xs">
          {{ toast.description }}
        </div>
      </div>
      <button
        class="btn btn-sm btn-ghost btn-circle"
        @click="remove(toast.id)"
      >
        <Icon name="tabler:x" size="16" />
      </button>
    </div>
  </div>
</template>
