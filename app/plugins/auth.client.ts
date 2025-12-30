import { useAuth } from "~/data/use-auth";

export default defineNuxtPlugin(() => {
  if (import.meta.server)
    return;
  const { loadUserFromCookie } = useAuth();
  // Recharge l'utilisateur dès le boot client pour persister la session après reload
  loadUserFromCookie();
});
