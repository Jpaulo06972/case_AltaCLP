/**
 * AltaCLP Intelligence — Application Router
 */

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/contexts/AuthContext";
import { AppDataProvider } from "@/contexts/AppDataContext";
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
import BibliotecaEquipamentos from "@/pages/BibliotecaEquipamentos";

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
        <AppDataProvider>
          <ToastProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route element={<DashboardLayout />}>
                  <Route path="/" element={<ProtectedRoute allowedRoles={["ceo", "cfo"]}><DashboardCEO /></ProtectedRoute>} />
                  <Route path="/engenharia" element={<ProtectedRoute allowedRoles={["engenharia", "ceo", "cfo"]}><DashboardEngenharia /></ProtectedRoute>} />
                  <Route path="/maquinas" element={<ProtectedRoute allowedRoles={["engenharia", "tecnico_campo", "ceo", "cfo"]}><Maquinas /></ProtectedRoute>} />
                  <Route path="/maquinas/:id" element={<ProtectedRoute allowedRoles={["engenharia", "tecnico_campo", "ceo", "cfo"]}><MaquinaDetalhe /></ProtectedRoute>} />
                  <Route path="/alertas" element={<ProtectedRoute allowedRoles={["engenharia", "tecnico_campo", "ceo", "cfo"]}><Alertas /></ProtectedRoute>} />
                  <Route path="/gitops" element={<ProtectedRoute allowedRoles={["engenharia", "ceo", "cfo"]}><GitOps /></ProtectedRoute>} />
                  <Route path="/comissionamento" element={<ProtectedRoute allowedRoles={["engenharia", "tecnico_campo", "vendedor", "ceo", "cfo"]}><Comissionamento /></ProtectedRoute>} />
                  <Route path="/cotacao" element={<ProtectedRoute allowedRoles={["vendas", "vendedor", "ceo", "cfo"]}><Cotacao /></ProtectedRoute>} />
                  <Route path="/biblioteca" element={<ProtectedRoute allowedRoles={["engenharia", "tecnico_campo", "ceo", "cfo"]}><BibliotecaEquipamentos /></ProtectedRoute>} />
                  <Route path="/roi" element={<ProtectedRoute allowedRoles={["ceo", "cfo"]}><ROI /></ProtectedRoute>} />
                </Route>
              </Routes>
            </BrowserRouter>
          </ToastProvider>
        </AppDataProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
