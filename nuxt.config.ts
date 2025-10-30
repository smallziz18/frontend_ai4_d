// https://nuxt.com/docs/api/configuration/nuxt-config

import env from "./lib/env";

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },

  runtimeConfig: {
    public: {
      apiBase: env.FAST_API_URL || "http://127.0.0.1:8000",
    },
  },

  modules: [
    "@nuxt/eslint",
    "@nuxtjs/tailwindcss",
    "@nuxt/icon",
    "@nuxtjs/color-mode",
    "@pinia/nuxt",
  ],

  eslint: {
    config: {
      standalone: false,
    },
  },

  colorMode: {
    dataValue: "theme",
  },
});
