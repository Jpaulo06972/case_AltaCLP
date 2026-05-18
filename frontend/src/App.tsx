/**
 * AltaCLP Intelligence — Application Router
 */

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/contexts/AuthContext";
import { ToastProvider } from "@/components/Toast";
import DashboardLayout from "@/components/DashboardLayout";
import ProtectedRoute from "@/components/ProtectedRoute";
import Login from "@/pages/Login";
import DashboardCEO from "@/pages/DashboardCEO";
import DashboardEngenharia from "@/pages/DashboardEngenharia";
import Alertas from "@/pages/Alertas";
import Maquinas from "@/pages/Maquinas";
import MaquinaDetalhe from "@/pages/MaquinaDetalhe";
import GitOps from "@/pages/GitOps";
import Comissionamento from "@/pages/Comissionamento";
import Cotacao from "@/pages/Cotacao";
import ROI from "@/pages/ROI";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route element={<DashboardLayout />}>
                <Route path="/" element={<ProtectedRoute allowedRoles={["ceo", "cfo", "engenharia"]}><DashboardCEO /></ProtectedRoute>} />
                <Route path="/engenharia" element={<ProtectedRoute allowedRoles={["engenharia"]}><DashboardEngenharia /></ProtectedRoute>} />
                <Route path="/maquinas" element={<ProtectedRoute allowedRoles={["engenharia", "tecnico_campo"]}><Maquinas /></ProtectedRoute>} />
                <Route path="/maquinas/:id" element={<ProtectedRoute allowedRoles={["engenharia", "tecnico_campo"]}><MaquinaDetalhe /></ProtectedRoute>} />
                <Route path="/alertas" element={<ProtectedRoute allowedRoles={["engenharia", "tecnico_campo"]}><Alertas /></ProtectedRoute>} />
                <Route path="/gitops" element={<ProtectedRoute allowedRoles={["engenharia"]}><GitOps /></ProtectedRoute>} />
                <Route path="/comissionamento" element={<ProtectedRoute allowedRoles={["ceo", "cfo", "engenharia", "tecnico_campo"]}><Comissionamento /></ProtectedRoute>} />
                <Route path="/cotacao" element={<ProtectedRoute allowedRoles={["engenharia", "vendas"]}><Cotacao /></ProtectedRoute>} />
                <Route path="/roi" element={<ProtectedRoute allowedRoles={["ceo", "cfo"]}><ROI /></ProtectedRoute>} />
              </Route>
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
