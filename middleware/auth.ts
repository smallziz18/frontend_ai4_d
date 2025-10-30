export default defineNuxtRouteMiddleware((_to, _from) => {
  const accessToken = useCookie("access_token");

  // Vérifier si l'utilisateur est authentifié
  if (!accessToken.value) {
    // Rediriger vers la page de login si non authentifié
    return navigateTo("/login");
  }
});
