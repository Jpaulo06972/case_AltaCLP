// AltaCLP Intelligence — App Router
// Design: Industrial Precision (Brutalismo Industrial Refinado)

import { Route, Switch } from "wouter";
import Layout from "./Layout";
import Home from "./Home";
import Alertas from "./Alertas";
import Comissionamento from "./Comissionamento";
import Codigo from "./Codigo";
import ROI from "./ROI";
import Cotacao from "./Cotacao";

const Toaster = (props: any) => null;
const TooltipProvider = ({ children }: any) => <>{children}</>;
const NotFound = () => <div>404 Não encontrado</div>;
const ErrorBoundary = ({ children }: any) => <>{children}</>;
const ThemeProvider = ({ children }: any) => <>{children}</>;
const toast = { info: (msg: string) => console.log(msg) } as any;

// Placeholder page for not-yet-implemented routes
function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex items-center justify-center h-full min-h-screen">
      <div className="text-center">
        <div className="text-4xl font-bold mb-2" style={{ color: "oklch(0.22 0.008 260)", fontFamily: "'JetBrains Mono', monospace" }}>
          {title}
        </div>
        <div className="text-sm" style={{ color: "oklch(0.4 0.01 260)", fontFamily: "'Space Grotesk', sans-serif" }}>
          Módulo em desenvolvimento — disponível na Fase 2
        </div>
      </div>
    </div>
  );
}

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Home} />
        <Route path="/alertas" component={Alertas} />
        <Route path="/comissionamento" component={Comissionamento} />
        <Route path="/codigo" component={Codigo} />
        <Route path="/cotacao" component={Cotacao} />
        <Route path="/roi" component={ROI} />
        <Route path="/maquinas">
          {() => {
            toast.info("Módulo de Máquinas em Campo — disponível na Fase 2");
            return <PlaceholderPage title="Máquinas em Campo" />;
          }}
        </Route>
        <Route path="/incidentes">
          {() => {
            toast.info("Módulo de Incidentes — disponível na Fase 2");
            return <PlaceholderPage title="Incidentes" />;
          }}
        </Route>
        <Route path="/configuracoes">
          {() => {
            toast.info("Configurações — disponível na Fase 2");
            return <PlaceholderPage title="Configurações" />;
          }}
        </Route>
        <Route path="/404" component={NotFound} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <TooltipProvider>
          <Toaster
            toastOptions={{
              style: {
                background: "oklch(0.16 0.008 260)",
                border: "1px solid oklch(0.22 0.008 260)",
                color: "oklch(0.85 0.005 260)",
                fontFamily: "'Space Grotesk', sans-serif",
                fontSize: "13px",
              },
            }}
          />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
