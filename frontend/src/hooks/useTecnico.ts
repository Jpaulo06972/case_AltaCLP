import { useAuth } from "@/contexts/AuthContext";

export function useTecnico() {
  const { user } = useAuth();
  const isTecnico = user?.perfil === "tecnico_campo";
  return { isTecnico, user };
}
