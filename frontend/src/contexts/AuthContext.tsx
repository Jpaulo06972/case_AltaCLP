/**
 * AltaCLP Intelligence — Auth Context
 * Manages authentication state, login/logout, and user profile
 */

import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { authApi } from "@/services/api";

interface User {
  id: string;
  nome: string;
  email: string;
  perfil: "ceo" | "cfo" | "engenharia" | "tecnico_campo" | "vendas" | "vendedor";
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, senha: string) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("altaclp_token")
  );
  const [isLoading, setIsLoading] = useState(true);

  // On mount, try to restore session from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem("altaclp_user");
    if (storedUser && token) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem("altaclp_user");
      }
    }
    setIsLoading(false);
  }, [token]);

  const login = async (email: string, senha: string) => {
    const res = await authApi.login(email, senha);
    const { access_token, perfil, nome, user_id } = res.data;

    let userId = user_id || "";
    if (!userId) {
      try {
        localStorage.setItem("altaclp_token", access_token);
        const me = await authApi.me();
        userId = String(me.data.id);
      } catch {
        userId = "";
      }
    }

    const userData: User = {
      id: userId,
      nome,
      email,
      perfil,
    };

    localStorage.setItem("altaclp_token", access_token);
    localStorage.setItem("altaclp_user", JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const logout = () => {
    localStorage.removeItem("altaclp_token");
    localStorage.removeItem("altaclp_user");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
