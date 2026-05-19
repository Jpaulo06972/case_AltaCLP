import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

interface ProtectedRouteProps {
  children: JSX.Element;
  allowedRoles?: string[];
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="h-screen w-full flex items-center justify-center bg-apple-gray">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.perfil)) {
    if (user.perfil === "tecnico_campo") return <Navigate to="/maquinas" replace />;
    if (user.perfil === "vendas" || user.perfil === "vendedor") return <Navigate to="/cotacao" replace />;
    if (user.perfil === "engenharia") return <Navigate to="/engenharia" replace />;
    if (user.perfil === "cfo") return <Navigate to="/" replace />;
    return <Navigate to="/" replace />;
  }

  return children;
}
