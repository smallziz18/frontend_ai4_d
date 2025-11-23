<script setup lang="ts">
defineProps<{
  name: string;
  icon?: string;
  earned?: boolean;
  description?: string;
  date?: string;
}>();
</script>

<template>
  <div
    class="card bg-base-100 border-2 transition-all"
    :class="{
      'border-warning shadow-lg': earned,
      'border-base-300 opacity-50': !earned,
    }"
  >
    <div class="card-body p-4">
      <div class="flex items-center gap-3">
        <div
          class="rounded-full p-3"
          :class="{
            'bg-warning text-warning-content': earned,
            'bg-base-200': !earned,
          }"
        >
          <Icon
            :name="icon || 'tabler:award'"
            size="32"
          />
        </div>
        <div class="flex-1">
          <h4 class="font-semibold">
            {{ name }}
          </h4>
          <p v-if="description" class="text-xs opacity-70">
            {{ description }}
          </p>
          <p v-if="earned && date" class="text-xs text-success mt-1">
            Obtenu le {{ date }}
          </p>
        </div>
        <Icon
          v-if="earned"
          name="tabler:check-circle"
          size="24"
          class="text-success"
        />
      </div>
    </div>
  </div>
</template>
