import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { gitopsExtApi } from "@/services/api";
import {
  FolderGit2,
  Download,
  AlertTriangle,
  CheckCircle,
  FileCode,
  UploadCloud,
  Terminal,
  Cpu,
} from "lucide-react";

export default function WorkspaceTecnico() {
  const { data: projetosData, isLoading } = useQuery({
    queryKey: ["gitops-projetos-tecnico"],
    queryFn: () => gitopsExtApi.projetos().then((r) => r.data),
  });

  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [gitStatus, setGitStatus] = useState<"idle" | "pulling" | "synced" | "modified">("idle");
  const [code, setCode] = useState<string>("");
  const [originalCode, setOriginalCode] = useState<string>("");
  const [committing, setCommitting] = useState(false);

  const projetos = projetosData?.projetos || [];

  const handlePull = () => {
    setGitStatus("pulling");
    setTimeout(() => {
      const simulatedCode = `PROGRAM PLC_PRG
VAR
    bEnable_TempControl : BOOL := TRUE;
    rTemperature_PV : REAL := 25.0;
    rSetpoint : REAL := 78.5;
    bAlarm_HighTemp : BOOL := FALSE;
END_VAR

// Controle de temperatura da máquina
IF bEnable_TempControl THEN
    IF rTemperature_PV > rSetpoint THEN
        bAlarm_HighTemp := TRUE;
        // Ativar resfriamento
    ELSE
        bAlarm_HighTemp := FALSE;
    END_IF
END_IF`;
      setCode(simulatedCode);
      setOriginalCode(simulatedCode);
      setGitStatus("synced");
    }, 1500);
  };

  useEffect(() => {
    if (gitStatus === "synced" || gitStatus === "modified") {
      if (code !== originalCode) {
        setGitStatus("modified");
      } else {
        setGitStatus("synced");
      }
    }
  }, [code, originalCode, gitStatus]);

  const handleCommit = () => {
    setCommitting(true);
    setTimeout(() => {
      setOriginalCode(code);
      setGitStatus("synced");
      setCommitting(false);
    }, 1500);
  };

  const handleInstalar = () => {
    alert("Código instalado no CLP do cliente com sucesso!");
    setSelectedProject(null);
    setGitStatus("idle");
  };

  if (isLoading) {
    return <div className="p-8 text-apple-tertiary">Carregando projetos...</div>;
  }

  return (
    <div className="space-y-6 max-w-[1400px] animate-fade-in">
      <div>
        <h2 className="text-[24px] font-bold text-apple-label tracking-tight flex items-center gap-2">
          <Terminal size={24} className="text-apple-blue" />
          Workspace Local (Auditoria Git)
        </h2>
        <p className="text-[14px] text-apple-tertiary mt-1">
          Ambiente simulado para o técnico fazer Pull do código e editar. A auditoria bloqueia a instalação se houver modificações não commitadas.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Sidebar Projetos */}
        <div className="md:col-span-1 space-y-3">
          <h3 className="text-[13px] font-semibold text-apple-tertiary uppercase tracking-wider mb-2">Projetos Disponíveis</h3>
          {projetos.map((proj: any) => (
            <div
              key={proj.id_projeto}
              onClick={() => {
                setSelectedProject(proj);
                setGitStatus("idle");
                setCode("");
                setOriginalCode("");
              }}
              className={`apple-card p-4 cursor-pointer transition-all border ${selectedProject?.id_projeto === proj.id_projeto ? 'border-apple-blue bg-apple-blue/5' : 'border-transparent hover:border-apple-separator/30'}`}
            >
              <div className="flex items-center gap-3">
                <FolderGit2 size={18} className={selectedProject?.id_projeto === proj.id_projeto ? 'text-apple-blue' : 'text-apple-tertiary'} />
                <div>
                  <h4 className="text-[14px] font-semibold text-apple-label truncate">{proj.id_projeto}</h4>
                  <p className="text-[12px] text-apple-tertiary truncate">{proj.nome}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Workspace Principal */}
        <div className="md:col-span-3">
          {!selectedProject ? (
            <div className="apple-card h-[400px] flex flex-col items-center justify-center text-apple-tertiary">
              <FolderGit2 size={48} className="mb-4 opacity-50" />
              <p>Selecione um projeto para abrir o workspace.</p>
            </div>
          ) : (
            <div className="apple-card overflow-hidden flex flex-col min-h-[500px]">
              {/* Header do Workspace */}
              <div className="bg-apple-surface-0 border-b border-apple-separator/30 px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-[16px] font-semibold text-apple-label">{selectedProject.nome}</h3>
                  <p className="text-[13px] text-apple-tertiary font-mono">{selectedProject.repo}</p>
                </div>
                
                {gitStatus === "idle" && (
                  <button onClick={handlePull} className="apple-btn apple-btn-primary flex items-center gap-2">
                    <Download size={16} />
                    Fazer Git Pull
                  </button>
                )}
                {gitStatus === "pulling" && (
                  <button disabled className="apple-btn apple-btn-secondary flex items-center gap-2">
                    <Download size={16} className="animate-bounce" />
                    Baixando arquivos...
                  </button>
                )}
              </div>

              {/* Área de Edição */}
              {(gitStatus === "synced" || gitStatus === "modified") && (
                <div className="flex-1 flex flex-col">
                  {/* Status Bar */}
                  {gitStatus === "modified" ? (
                    <div className="bg-apple-red/10 border-b border-apple-red/20 p-4 animate-scale-in">
                      <div className="flex items-start gap-3">
                        <AlertTriangle size={24} className="text-apple-red shrink-0" />
                        <div>
                          <h4 className="text-[15px] font-bold text-apple-red">ERRO DE AUDITORIA: Modificações não commitadas detectadas!</h4>
                          <p className="text-[13px] text-apple-red/80 mt-1">
                            A pasta local foi alterada. Você não pode instalar este código na máquina do cliente sem registrar o hotfix no Git.
                          </p>
                          <button 
                            onClick={handleCommit}
                            disabled={committing}
                            className="mt-3 bg-apple-red hover:bg-red-600 text-white text-[13px] font-semibold px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
                          >
                            {committing ? <UploadCloud size={16} className="animate-pulse" /> : <UploadCloud size={16} />}
                            {committing ? "Salvando no Repositório..." : "Fazer Commit e Push"}
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-apple-green/10 border-b border-apple-green/20 p-3 flex items-center justify-between">
                      <div className="flex items-center gap-2 text-apple-green">
                        <CheckCircle size={16} />
                        <span className="text-[13px] font-medium">Pasta Sincronizada com o Repositório Git</span>
                      </div>
                      <button onClick={handleInstalar} className="apple-btn apple-btn-primary text-[12px] py-1.5 px-3 flex items-center gap-2">
                        <Cpu size={14} />
                        Instalar no CLP
                      </button>
                    </div>
                  )}

                  {/* Editor */}
                  <div className="flex-1 p-4 bg-[#1e1e1e]">
                    <div className="flex items-center gap-2 mb-2 text-gray-400 text-[12px] font-mono">
                      <FileCode size={14} /> PLC_PRG/Main.st
                      {gitStatus === "modified" && <span className="text-apple-yellow ml-2">(Modificado)</span>}
                    </div>
                    <textarea
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      spellCheck={false}
                      className="w-full h-[350px] bg-transparent text-gray-300 font-mono text-[13px] resize-none focus:outline-none focus:ring-0 p-2"
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
