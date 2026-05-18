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
    // Redirect to the default route for their role if they try to access forbidden route
    if (user.perfil === "tecnico_campo") return <Navigate to="/maquinas" replace />;
    if (user.perfil === "vendas") return <Navigate to="/cotacao" replace />;
    return <Navigate to="/" replace />;
  }

  return children;
}
