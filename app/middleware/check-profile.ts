/**
 * Middleware pour vérifier si l'utilisateur a déjà un profil
 * Utilisé uniquement sur la page /questionnaire pour éviter qu'un utilisateur
 * avec un profil existant ne refasse le questionnaire
 */
export default defineNuxtRouteMiddleware(async () => {
  const accessToken = useCookie("access_token");

  // Si pas connecté, laisser le middleware auth.ts gérer
  if (!accessToken.value) {
    return;
  }

  // Vérifier si l'utilisateur a déjà un profil
  const { hasProfile } = useProfile();

  try {
    const profileExists = await hasProfile();

    if (profileExists) {
      console.warn("⚠️ L'utilisateur a déjà un profil - Redirection vers dashboard");

      // Rediriger vers le dashboard avec un message
      return navigateTo({
        path: "/dashboard",
        query: { from: "questionnaire_blocked" },
      });
    }
  }
  catch (e) {
    console.error("Erreur lors de la vérification du profil:", e);
    // En cas d'erreur, laisser passer (mieux vaut permettre l'accès que bloquer à tort)
  }
});
