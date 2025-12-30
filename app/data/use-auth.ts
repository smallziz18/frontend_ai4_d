import { useApi } from "~/composables/use-api";

export type User = {
  id: string;
  username: string;
  email: string;
};

export function useAuth() {
  const api = useApi();
  const isProd = import.meta.env.PROD;
  const user = useState<User | null>("user", () => null);
  const cookieSecurity = {
    secure: isProd,
    sameSite: "lax" as const,
    path: "/",
  };
  const accessToken = useCookie("access_token", {
    maxAge: 60 * 60 * 24 * 7, // 7 jours
    ...cookieSecurity,
  });
  const refreshToken = useCookie("refresh_token", {
    maxAge: 60 * 60 * 24 * 30, // 30 jours
    ...cookieSecurity,
  });
  const userCookie = useCookie("user_data", {
    maxAge: 60 * 60 * 24 * 7,
    ...cookieSecurity,
  });

  const setUser = (value: User | null) => {
    user.value = value;
    userCookie.value = value ? JSON.stringify(value) : null;
  };

  const isAuthenticated = () => {
    return !!accessToken.value;
  };

  const login = async (email: string, password: string) => {
    try {
      const data = await api.auth.login(email, password);

      if (data) {
        accessToken.value = data.access_token;
        refreshToken.value = data.refresh_token;
        setUser(data.user);
      }

      return user.value;
    }
    catch (error: any) {
      // Si l'erreur est liée à un compte non vérifié, on lance une erreur spécifique
      const errorMessage = error.data?.detail || error.message || "Échec de connexion";
      throw new Error(errorMessage);
    }
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    }
    catch (e) {
      console.error("Erreur lors de la déconnexion:", e);
    }
    finally {
      accessToken.value = null;
      refreshToken.value = null;
      setUser(null);
    }
  };

  const loadUserFromCookie = () => {
    if (user.value)
      return;
    if (userCookie.value) {
      try {
        const parsed = typeof userCookie.value === "string" ? JSON.parse(userCookie.value) : userCookie.value;
        setUser(parsed as User);
      }
      catch (e) {
        console.error("Erreur lors du chargement de l'utilisateur:", e);
        setUser(null);
      }
    }
  };

  return {
    user: readonly(user),
    isAuthenticated,
    login,
    logout,
    loadUserFromCookie,
    setUser,
    accessToken,
    refreshToken,
  };
}
