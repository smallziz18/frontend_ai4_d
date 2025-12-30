import { useAuth } from "~/data/use-auth";

export default defineNuxtRouteMiddleware(async () => {
  const { loadUserFromCookie } = useAuth();
  const accessToken = useCookie("access_token");

  // Vérifier si l'utilisateur est authentifié
  if (!accessToken.value) {
    // Rediriger vers la page de login si non authentifié
    return navigateTo("/login");
  }

  // Restaure le user en mémoire si les cookies sont présents
  loadUserFromCookie();
});
