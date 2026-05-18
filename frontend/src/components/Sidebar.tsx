/**
 * AltaCLP Intelligence — Sidebar (macOS Sonoma Style)
 * Glassmorphism sidebar with SF Symbol-like icons
 */

import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Activity,
  Bell,
  GitCompareArrows,
  Wrench,
  Zap,
  TrendingUp,
  Cpu,
  LogOut,
  ChevronDown,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";

const navigation = [
  { label: "Visão Geral", path: "/", icon: LayoutDashboard, roles: ["ceo", "cfo", "engenharia"] },
  { label: "Máquinas", path: "/maquinas", icon: Cpu, roles: ["engenharia", "tecnico_campo"] },
  { label: "Alertas", path: "/alertas", icon: Bell, roles: ["engenharia", "tecnico_campo"] },
  { label: "Auditoria GitOps", path: "/gitops", icon: GitCompareArrows, roles: ["engenharia"] },
  { label: "Comissionamento", path: "/comissionamento", icon: Wrench, roles: ["ceo", "cfo", "engenharia", "tecnico_campo"] },
  { label: "Cotação IA", path: "/cotacao", icon: Zap, roles: ["engenharia", "vendas"] },
  { label: "ROI & Economia", path: "/roi", icon: TrendingUp, roles: ["ceo", "cfo"] },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const profileLabels: Record<string, string> = {
    ceo: "CEO",
    cfo: "CFO",
    engenharia: "Engenharia",
    tecnico_campo: "Técnico de Campo",
  };

  return (
    <aside className="glass-sidebar w-[260px] h-screen flex flex-col border-r border-black/5 fixed left-0 top-0 z-40">
      {/* Logo / App Name */}
      <div className="px-5 pt-6 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-apple-blue flex items-center justify-center">
            <Activity size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-[15px] font-bold text-apple-label tracking-tight">
              AltaCLP
            </h1>
            <p className="text-[11px] text-apple-tertiary font-medium">
              Intelligence Platform
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-0.5 overflow-y-auto">
        <p className="text-[11px] font-semibold text-apple-tertiary uppercase tracking-wider px-3 pb-1 pt-2">
          Menu
        </p>
        {navigation
          .filter((item) => user && item.roles.includes(user.perfil))
          .map((item) => {
          const isActive =
            item.path === "/"
              ? location.pathname === "/"
              : location.pathname.startsWith(item.path);

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-200 ${
                isActive
                  ? "bg-apple-blue text-white shadow-sm"
                  : "text-apple-secondary hover:bg-black/[0.04]"
              }`}
            >
              <item.icon
                size={18}
                strokeWidth={isActive ? 2 : 1.5}
                className={isActive ? "text-white" : "text-apple-tertiary"}
              />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      {/* User section */}
      <div className="px-3 pb-4 pt-2 border-t border-black/5">
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-black/[0.04] transition-colors"
          >
            {/* Avatar */}
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-apple-blue to-apple-purple flex items-center justify-center text-white text-xs font-bold">
              {user?.nome?.charAt(0) || "U"}
            </div>
            <div className="flex-1 text-left min-w-0">
              <p className="text-[13px] font-semibold text-apple-label truncate">
                {user?.nome || "Usuário"}
              </p>
              <p className="text-[11px] text-apple-tertiary">
                {profileLabels[user?.perfil || "ceo"]}
              </p>
            </div>
            <ChevronDown
              size={14}
              className={`text-apple-tertiary transition-transform ${
                showUserMenu ? "rotate-180" : ""
              }`}
            />
          </button>

          {/* Dropdown menu */}
          {showUserMenu && (
            <div className="absolute bottom-full left-0 right-0 mb-1 apple-card p-1 animate-scale-in">
              <button
                onClick={() => {
                  setShowUserMenu(false);
                  logout();
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] font-medium text-apple-red hover:bg-apple-red/10 transition-colors"
              >
                <LogOut size={16} />
                Sair da conta
              </button>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
