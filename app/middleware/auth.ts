export default defineNuxtRouteMiddleware(async () => {
  const accessToken = useCookie("access_token");

  // Vérifier si l'utilisateur est authentifié
  if (!accessToken.value) {
    // Rediriger vers la page de login si non authentifié
    return navigateTo("/login");
  }

  // Note: La vérification du profil se fera dans les pages elles-mêmes
  // pour éviter des appels API inutiles dans le middleware
});
