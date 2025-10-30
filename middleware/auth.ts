export default defineNuxtRouteMiddleware((to) => {
  const accessToken = useCookie("access_token");

  // Si l'utilisateur essaie d'accéder au dashboard sans être connecté
  if (to.path === "/dashboard" && !accessToken.value) {
    return navigateTo("/login");
  }

  // Si l'utilisateur est connecté et essaie d'accéder à la page de login
  if (to.path === "/login" && accessToken.value) {
    return navigateTo("/dashboard");
  }
});
