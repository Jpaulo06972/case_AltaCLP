/**
 * AltaCLP Intelligence — Toast Notification System
 * macOS-style floating notifications
 */

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import { CheckCircle, AlertTriangle, AlertOctagon, Info, X } from "lucide-react";

interface Toast {
  id: string;
  message: string;
  type: "success" | "error" | "warning" | "info";
  exiting?: boolean;
}

interface ToastContextType {
  addToast: (message: string, type?: Toast["type"]) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}

const icons = {
  success: <CheckCircle size={16} className="text-apple-green flex-shrink-0" />,
  error: <AlertOctagon size={16} className="text-apple-red flex-shrink-0" />,
  warning: <AlertTriangle size={16} className="text-apple-orange flex-shrink-0" />,
  info: <Info size={16} className="text-apple-blue flex-shrink-0" />,
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: any, type: Toast["type"] = "info") => {
    const id = crypto.randomUUID();
    let msgString = message;
    if (msgString && typeof msgString === "object") {
      msgString = msgString.message || msgString.mensagem || JSON.stringify(msgString);
    } else if (msgString === undefined || msgString === null) {
      msgString = "";
    } else {
      msgString = String(msgString);
    }
    setToasts((prev) => [...prev, { id, message: msgString, type }]);

    // Auto-dismiss after 4s
    setTimeout(() => {
      setToasts((prev) =>
        prev.map((t) => (t.id === id ? { ...t, exiting: true } : t))
      );
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 250);
    }, 4000);
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) =>
      prev.map((t) => (t.id === id ? { ...t, exiting: true } : t))
    );
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 250);
  }, []);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`toast ${toast.exiting ? "toast-exit" : ""}`}
          >
            <div className="flex items-center gap-3">
              {icons[toast.type]}
              <span className="flex-1">{toast.message}</span>
              <button
                onClick={() => dismiss(toast.id)}
                className="opacity-60 hover:opacity-100 transition-opacity"
              >
                <X size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
