export type User = {
  id: string;
  username: string;
  email: string;
};

type LoginResponse = {
  message: string;
  access_token: string;
  refresh_token: string;
  user: User;
};

export function useAuth() {
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
    const { data, error } = await useFetch<LoginResponse>("http://127.0.0.1:8000/api/auth/v1/login", {
      method: "POST",
      body: { email, password },
    });

    if (error.value) {
      // Si l'erreur est liée à un compte non vérifié, on lance une erreur spécifique
      const errorMessage = error.value.data?.detail || "Échec de connexion";
      throw new Error(errorMessage);
    }

    if (data.value) {
      accessToken.value = data.value.access_token;
      refreshToken.value = data.value.refresh_token;
      userCookie.value = JSON.stringify(data.value.user);
      user.value = data.value.user;
    }

    return user.value;
  };

  const logout = async () => {
    try {
      await useFetch("http://127.0.0.1:8000/api/auth/v1/logout", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      });
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
