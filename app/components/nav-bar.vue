<script setup lang="ts">
const colormod = useColorMode();

const isDark = computed({
  get() {
    return colormod.value === "dark";
  },
  set(value) {
    colormod.value = value ? "dark" : "light";
  },
});
</script>

<template>
  <div class="navbar bg-base-300 shadow-sm">
    <div class="flex-1">
      <NuxtLink to="/" class="btn btn-soft btn-primary text-xl">
        AI4D School
      </NuxtLink>
    </div>
    <div class=" flex-1">
      <NuxtLink to="/login" class="btn btn-outline btn-primary mr-2">
        Log in
      </NuxtLink>
      <NuxtLink to="/sign-up" class="btn btn-outline btn-info mr-2">
        Sign up
      </NuxtLink>
    </div>
    <div class=" flex-none">
      <label class="flex cursor-pointer gap-2">
        <Icon name="tabler:sun" size="24" />
        <input
          v-model="isDark"
          type="checkbox"
          value="synthwave"
          class="toggle theme-controller"
        >
        <Icon
          :is-dark
          name="tabler:moon-filled"
          size="24"
        />
      </label>
    </div>
  </div>
</template>

<style scoped>

</style>
