<script setup lang="ts">
defineProps<{
  title: string;
  description: string;
  xp: number;
  badge?: string;
  objectives?: string[];
  completed?: boolean;
  progress?: number;
}>();
</script>

<template>
  <div
    class="card bg-base-100 border-2 transition-all hover:shadow-xl"
    :class="{
      'border-success': completed,
      'border-primary': !completed,
    }"
  >
    <div class="card-body">
      <div class="flex justify-between items-start">
        <h3 class="card-title text-xl">
          {{ title }}
        </h3>
        <div class="badge badge-primary gap-2">
          <Icon name="tabler:star" size="16" />
          {{ xp }} XP
        </div>
      </div>

      <p class="text-sm opacity-80 mt-2">
        {{ description }}
      </p>

      <div v-if="objectives && objectives.length > 0" class="mt-4">
        <h4 class="text-sm font-semibold mb-2">
          Objectifs :
        </h4>
        <ul class="space-y-2">
          <li
            v-for="(objective, idx) in objectives"
            :key="idx"
            class="flex items-start gap-2 text-sm"
          >
            <Icon
              :name="completed ? 'tabler:check' : 'tabler:circle'"
              size="20"
              :class="completed ? 'text-success' : 'text-base-content'"
            />
            <span>{{ objective }}</span>
          </li>
        </ul>
      </div>

      <div v-if="progress !== undefined && !completed" class="mt-4">
        <div class="flex justify-between text-xs mb-1">
          <span>Progression</span>
          <span>{{ progress }}%</span>
        </div>
        <progress
          class="progress progress-primary"
          :value="progress"
          max="100"
        />
      </div>

      <div v-if="badge" class="mt-4">
        <div class="badge badge-outline gap-2">
          <Icon name="tabler:award" size="16" />
          Récompense : {{ badge }}
        </div>
      </div>

      <div v-if="completed" class="mt-4">
        <div class="alert alert-success">
          <Icon name="tabler:check-circle" size="24" />
          <span>Quête terminée !</span>
        </div>
      </div>
    </div>
  </div>
</template>
