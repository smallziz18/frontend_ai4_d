// Composable pour gérer le thème (dark/light)
export function useTheme() {
  // State du thème (sauvegardé dans localStorage)
  const theme = useState<"light" | "dark">("theme", () => {
    // Vérifier le localStorage au chargement
    if (import.meta.client) {
      const saved = localStorage.getItem("theme");
      if (saved === "light" || saved === "dark") {
        return saved;
      }
      // Par défaut, utiliser la préférence système
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    return "dark"; // Défaut server-side
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
      // Sauvegarder dans localStorage
      localStorage.setItem("theme", newTheme);
    }
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
