/**
 * AltaCLP Intelligence — AppDataContext
 * Single source of truth for all cross-screen relational data.
 * Hydrates from GET /api/v1/app-state on app load and invalidates
 * after every mutation via the exposed `refresh()` helper.
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import api from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Project {
  id: string;
  nome_contrato: string;
  status: string;
  valor_contrato: number;
  prazo: string | null;
  dias_atraso: number;
  risco: string | null;
  progresso: number;
  alert_count: number;
}

export interface Machine {
  id: string;
  codigo: string;
  nome: string;
  status: string;
  id_projeto: string | null;
  ultima_leitura: string | null;
}

export interface AlertItem {
  id: string;
  codigo_alerta: string;
  titulo: string;
  severidade: string;
  status: string;
  maquina_id: string;
  id_projeto: string | null;
  timestamp_criacao: string | null;
}

export interface GitLog {
  id: string;
  id_projeto: string | null;
  diff_resumo: string;
  em_sync: boolean;
  timestamp: string | null;
}

export interface CurrentUser {
  id: string;
  nome: string;
  perfil: string;
}

interface AppDataState {
  projects: Project[];
  machines: Machine[];
  alerts: AlertItem[];
  gitLogs: GitLog[];
  currentUser: CurrentUser | null;
  isLoading: boolean;
  error: string | null;
  lastFetchedAt: string | null;
}

interface AppDataContextType extends AppDataState {
  refresh: () => Promise<void>;
  /** Optimistically update a single project field in local state */
  updateProject: (id: string, patch: Partial<Project>) => void;
  /** Optimistically update a single alert */
  updateAlert: (id: string, patch: Partial<AlertItem>) => void;
}

// ─── Context ──────────────────────────────────────────────────────────────────

const AppDataContext = createContext<AppDataContextType | null>(null);

export function AppDataProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [state, setState] = useState<AppDataState>({
    projects: [],
    machines: [],
    alerts: [],
    gitLogs: [],
    currentUser: null,
    isLoading: false,
    error: null,
    lastFetchedAt: null,
  });

  const fetch = useCallback(async () => {
    if (!isAuthenticated) return;
    setState((s) => ({ ...s, isLoading: true, error: null }));
    try {
      const res = await api.get("/app-state");
      const d = res.data;
      setState({
        projects: d.projects ?? [],
        machines: d.machines ?? [],
        alerts: d.alerts ?? [],
        gitLogs: d.git_logs ?? [],
        currentUser: d.current_user ?? null,
        isLoading: false,
        error: null,
        lastFetchedAt: d.fetched_at ?? new Date().toISOString(),
      });
    } catch (err: any) {
      setState((s) => ({
        ...s,
        isLoading: false,
        error: err?.response?.data?.detail ?? "Falha ao carregar dados globais",
      }));
    }
  }, [isAuthenticated]);

  // Hydrate on auth, then every 60 seconds
  useEffect(() => {
    if (isAuthenticated) {
      fetch();
      const interval = setInterval(fetch, 60_000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated, fetch]);

  const updateProject = useCallback((id: string, patch: Partial<Project>) => {
    setState((s) => ({
      ...s,
      projects: s.projects.map((p) => (p.id === id ? { ...p, ...patch } : p)),
    }));
  }, []);

  const updateAlert = useCallback((id: string, patch: Partial<AlertItem>) => {
    setState((s) => ({
      ...s,
      alerts: s.alerts.map((a) => (a.id === id ? { ...a, ...patch } : a)),
    }));
  }, []);

  return (
    <AppDataContext.Provider
      value={{ ...state, refresh: fetch, updateProject, updateAlert }}
    >
      {children}
    </AppDataContext.Provider>
  );
}

export function useAppData() {
  const ctx = useContext(AppDataContext);
  if (!ctx) throw new Error("useAppData must be used inside AppDataProvider");
  return ctx;
}
