// Composable pour gérer le thème (dark/light)
export function useTheme() {
  const isProd = import.meta.env.PROD;
  const themeCookie = useCookie<"light" | "dark">("theme", {
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 365, // 1 an
    secure: isProd,
  });
  // State du thème (sauvegardé dans localStorage)
  const theme = useState<"light" | "dark">("theme", () => {
    if (import.meta.client) {
      const savedLocal = localStorage.getItem("theme");
      const savedCookie = themeCookie.value;
      const saved = (savedLocal as "light" | "dark") || savedCookie || undefined;
      if (saved === "light" || saved === "dark") {
        return saved;
      }
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    return themeCookie.value || "dark";
  });

  // Appliquer le thème au document
  const applyTheme = (newTheme: "light" | "dark") => {
    if (import.meta.client) {
      const html = document.documentElement;
      if (newTheme === "dark") {
        html.classList.add("dark");
        html.setAttribute("data-theme", "dark");
      }
      else {
        html.classList.remove("dark");
        html.setAttribute("data-theme", "light");
      }
      localStorage.setItem("theme", newTheme);
    }
    themeCookie.value = newTheme;
  };

  // Changer le thème
  const toggleTheme = () => {
    const newTheme = theme.value === "dark" ? "light" : "dark";
    theme.value = newTheme;
    applyTheme(newTheme);
  };

  // Définir un thème spécifique
  const setTheme = (newTheme: "light" | "dark") => {
    theme.value = newTheme;
    applyTheme(newTheme);
  };

  // Computed pour les icônes
  const isDark = computed(() => theme.value === "dark");
  const themeIcon = computed(() => isDark.value ? "tabler:sun" : "tabler:moon");

  // Initialiser le thème au montage (côté client uniquement)
  onMounted(() => {
    applyTheme(theme.value);
  });

  return {
    theme,
    isDark,
    themeIcon,
    toggleTheme,
    setTheme,
  };
}
