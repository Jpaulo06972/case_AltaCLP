// AltaCLP Intelligence — Main Layout
// Design: Industrial Precision — Dark sidebar with amber accents

import { useState } from "react";
import { Link, useLocation } from "wouter";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Cpu,
  GitBranch,
  LayoutDashboard,
  Settings,
  Wrench,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  {
    group: "Visão Geral",
    items: [
      { path: "/", label: "Command Center", icon: LayoutDashboard },
    ],
  },
  {
    group: "Operações",
    items: [
      { path: "/alertas", label: "Alertas & Preditiva", icon: Activity },
      { path: "/comissionamento", label: "Comissionamento", icon: Wrench },
      { path: "/codigo", label: "Auditoria de Código", icon: GitBranch },
    ],
  },
  {
    group: "Comercial",
    items: [
      { path: "/cotacao", label: "Assistente de Cotação", icon: Zap },
      { path: "/roi", label: "ROI & Economia", icon: BarChart3 },
    ],
  },
  {
    group: "Sistema",
    items: [
      { path: "/maquinas", label: "Máquinas em Campo", icon: Cpu },
      { path: "/incidentes", label: "Incidentes", icon: AlertTriangle },
      { path: "/configuracoes", label: "Configurações", icon: Settings },
    ],
  },
];

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [location] = useLocation();

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: "oklch(0.1 0.008 260)" }}>
      {/* Sidebar */}
      <aside
        className={cn(
          "flex flex-col flex-shrink-0 transition-all duration-300 ease-out border-r",
          collapsed ? "w-16" : "w-60"
        )}
        style={{
          background: "oklch(0.11 0.008 260)",
          borderColor: "oklch(0.18 0.008 260)",
        }}
      >
        {/* Logo */}
        <div
          className="flex items-center h-14 px-4 border-b flex-shrink-0"
          style={{ borderColor: "oklch(0.18 0.008 260)" }}
        >
          <div className="flex items-center gap-3 min-w-0">
            <div
              className="w-8 h-8 rounded flex items-center justify-center flex-shrink-0"
              style={{ background: "oklch(0.75 0.18 80)" }}
            >
              <span className="text-xs font-bold" style={{ color: "oklch(0.1 0.008 260)", fontFamily: "'JetBrains Mono', monospace" }}>
                AC
              </span>
            </div>
            {!collapsed && (
              <div className="min-w-0">
                <div className="text-sm font-bold truncate" style={{ color: "oklch(0.95 0.003 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
                  AltaCLP
                </div>
                <div className="text-xs truncate" style={{ color: "oklch(0.55 0.012 260)" }}>
                  Intelligence
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-3 px-2">
          {navItems.map((group) => (
            <div key={group.group} className="mb-4">
              {!collapsed && (
                <div
                  className="text-xs font-semibold uppercase tracking-widest px-2 mb-1"
                  style={{ color: "oklch(0.4 0.01 260)", fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  {group.group}
                </div>
              )}
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = location === item.path;
                return (
                  <Link key={item.path} href={item.path}>
                    <div
                      className={cn(
                        "flex items-center gap-3 px-2 py-2 rounded transition-all duration-150 mb-0.5",
                        isActive
                          ? "text-[oklch(0.1_0.008_260)]"
                          : "hover:bg-[oklch(0.16_0.008_260)]"
                      )}
                      style={
                        isActive
                          ? { background: "oklch(0.75 0.18 80)", color: "oklch(0.1 0.008 260)" }
                          : { color: "oklch(0.7 0.008 260)" }
                      }
                      title={collapsed ? item.label : undefined}
                    >
                      <Icon size={16} className="flex-shrink-0" />
                      {!collapsed && (
                        <span className="text-sm font-medium truncate" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                          {item.label}
                        </span>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Collapse toggle */}
        <div
          className="flex items-center justify-end p-3 border-t"
          style={{ borderColor: "oklch(0.18 0.008 260)" }}
        >
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded transition-colors hover:bg-[oklch(0.16_0.008_260)]"
            style={{ color: "oklch(0.55 0.012 260)" }}
          >
            {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
