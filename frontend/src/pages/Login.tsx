/**
 * AltaCLP Intelligence — Login Page
 * Apple ID-style centered login modal
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Activity, Eye, EyeOff, Loader2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, senha);
      navigate("/", { replace: true });
    } catch (err: any) {
      setError(
        err.response?.data?.mensagem ||
          "Credenciais inválidas. Tente novamente."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f5f5f7] via-[#e8e8ed] to-[#d2d2d7] flex items-center justify-center p-6">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-apple-blue/5 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] rounded-full bg-apple-purple/5 blur-3xl" />
      </div>

      {/* Login card */}
      <div className="relative apple-card w-full max-w-[420px] p-10 animate-scale-in">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-apple-blue to-apple-indigo flex items-center justify-center mb-4 shadow-lg shadow-apple-blue/20">
            <Activity size={32} className="text-white" />
          </div>
          <h1 className="text-[22px] font-bold text-apple-label tracking-tight">
            AltaCLP Intelligence
          </h1>
          <p className="text-[14px] text-apple-tertiary mt-1">
            Faça login para continuar
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-apple-red/8 border border-apple-red/15 text-apple-red text-[13px] font-medium px-4 py-3 rounded-xl animate-fade-in">
              {error}
            </div>
          )}

          <div>
            <label className="block text-[13px] font-medium text-apple-secondary mb-1.5">
              E-mail
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="marcos.tedesco@altaclp.com.br"
              required
              className="w-full px-4 py-3 bg-apple-surface-1 border border-apple-separator rounded-xl text-[15px] text-apple-label placeholder:text-apple-quaternary focus:outline-none focus:ring-2 focus:ring-apple-blue/40 focus:border-apple-blue transition-all duration-200"
            />
          </div>

          <div>
            <label className="block text-[13px] font-medium text-apple-secondary mb-1.5">
              Senha
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                placeholder="••••••"
                required
                className="w-full px-4 py-3 bg-apple-surface-1 border border-apple-separator rounded-xl text-[15px] text-apple-label placeholder:text-apple-quaternary focus:outline-none focus:ring-2 focus:ring-apple-blue/40 focus:border-apple-blue transition-all duration-200 pr-12"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-apple-tertiary hover:text-apple-secondary transition-colors"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="apple-btn apple-btn-primary w-full py-3.5 text-[15px] mt-2 disabled:opacity-60"
          >
            {loading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              "Entrar"
            )}
          </button>
        </form>

        {/* Demo accounts hint */}
        <div className="mt-6 pt-5 border-t border-apple-separator">
          <p className="text-[11px] text-apple-tertiary text-center mb-2 font-medium">
            Contas de demonstração
          </p>
          <div className="grid grid-cols-2 gap-1.5">
            {[
              { email: "marcos.tedesco@altaclp.com.br", label: "CEO" },
              { email: "roberto.cfo@altaclp.com.br", label: "CFO" },
              { email: "claudia.eng@altaclp.com.br", label: "Engenharia" },
              { email: "anderson.campo@altaclp.com.br", label: "Campo" },
            ].map((demo) => (
              <button
                key={demo.email}
                onClick={() => {
                  setEmail(demo.email);
                  setSenha("demo123");
                }}
                className="text-[11px] text-apple-blue font-medium px-2.5 py-1.5 rounded-lg hover:bg-apple-blue/8 transition-colors text-center"
              >
                {demo.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
