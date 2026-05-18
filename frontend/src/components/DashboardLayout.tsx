/**
 * AltaCLP Intelligence — Dashboard Layout
 * macOS-style layout with glassmorphism sidebar + header
 */

import { Outlet, Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import Sidebar from "@/components/Sidebar";

const pageTitles: Record<string, string> = {
  "/": "Visão Geral",
  "/maquinas": "Máquinas",
  "/alertas": "Alertas",
  "/gitops": "Auditoria GitOps",
  "/comissionamento": "Comissionamento",
  "/cotacao": "Cotação Inteligente",
  "/roi": "ROI & Economia",
};

export default function DashboardLayout() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-apple-bg">
        <div className="w-8 h-8 border-3 border-apple-blue/30 border-t-apple-blue rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const currentTitle =
    pageTitles[location.pathname] ||
    Object.entries(pageTitles).find(([path]) =>
      path !== "/" && location.pathname.startsWith(path)
    )?.[1] ||
    "AltaCLP";

  return (
    <div className="min-h-screen bg-apple-bg">
      <Sidebar />

      {/* Main content area — offset by sidebar width */}
      <div className="ml-[260px]">
        {/* Top header bar */}
        <header className="glass sticky top-0 z-30 h-14 flex items-center justify-between px-8 border-b border-black/5">
          <h2 className="text-[17px] font-semibold text-apple-label tracking-tight">
            {currentTitle}
          </h2>
          <div className="flex items-center gap-3">
            <span className="text-[12px] text-apple-tertiary font-medium">
              {new Date().toLocaleDateString("pt-BR", {
                weekday: "long",
                day: "numeric",
                month: "long",
              })}
            </span>
          </div>
        </header>

        {/* Page content */}
        <main className="p-8 animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
