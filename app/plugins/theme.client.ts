export default defineNuxtPlugin(() => {
  if (import.meta.server)
    return;
  const { theme, setTheme } = useTheme();
  // Appliquer immédiatement le thème stocké pour éviter le flash
  setTheme(theme.value);
});
