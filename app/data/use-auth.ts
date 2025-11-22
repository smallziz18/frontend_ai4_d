export type User = {
  id: string;
  username: string;
  email: string;
};

export function useAuth() {
  const api = useApi();
  const user = useState<User | null>("user", () => null);
  const accessToken = useCookie("access_token", {
    maxAge: 60 * 60 * 24 * 7, // 7 jours
    secure: false,
    sameSite: "lax",
  });
  const refreshToken = useCookie("refresh_token", {
    maxAge: 60 * 60 * 24 * 30, // 30 jours
    secure: false,
    sameSite: "lax",
  });
  const userCookie = useCookie("user_data", {
    maxAge: 60 * 60 * 24 * 7,
    secure: false,
    sameSite: "lax",
  });

  const isAuthenticated = () => {
    return !!accessToken.value;
  };

  const login = async (email: string, password: string) => {
    try {
      const data = await api.auth.login(email, password);

      if (data) {
        accessToken.value = data.access_token;
        refreshToken.value = data.refresh_token;
        userCookie.value = JSON.stringify(data.user);
        user.value = data.user;
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
      userCookie.value = null;
      user.value = null;
    }
  };

  const loadUserFromCookie = () => {
    if (userCookie.value && !user.value) {
      try {
        user.value = JSON.parse(userCookie.value as string);
      }
      catch (e) {
        console.error("Erreur lors du chargement de l'utilisateur:", e);
      }
    }
  };

  return {
    user: readonly(user),
    isAuthenticated,
    login,
    logout,
    loadUserFromCookie,
  };
}
