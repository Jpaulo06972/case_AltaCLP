// AltaCLP Intelligence — Mock Data
// Based on real data extracted from client transcripts and internal documents

export const kpiData = {
  falseAlerts: {
    current: 64,
    previous: 60,
    trend: "up",
    costPerMonth: 31400,
    label: "Falsos Alertas",
    unit: "%",
  },
  commissioning: {
    backlog: 26,
    withDelay: 13,
    withFine: 4,
    avgDays: 6,
    label: "Backlog Comissionamento",
  },
  codeSync: {
    divergent: 8,
    total: 50,
    incidentsThisYear: 4,
    totalLoss: 250000,
    label: "Máquinas com Drift de Código",
  },
  nps: {
    current: 68,
    previous: 82,
    drop: -14,
    label: "NPS",
  },
  revenueAtRisk: {
    anaclara: 780000,
    label: "Receita em Risco (Anaclara)",
  },
};

export type AlertStatus = "critical" | "warning" | "ok" | "offline";

export interface Machine {
  id: string;
  name: string;
  client: string;
  location: string;
  status: AlertStatus;
  lastAlert: string;
  alertCount30d: number;
  falseAlertRate: number;
  codeSync: "ok" | "divergent" | "unknown";
  lastVisit: string;
  sensors: {
    temperature: number;
    pressure: number;
    vibration: number;
  };
}

export const machines: Machine[] = [
  {
    id: "M-VH-118",
    name: "Extrusora Linha 3",
    client: "Vinhal Alimentos",
    location: "Ribeirão Preto/SP",
    status: "critical",
    lastAlert: "há 2h",
    alertCount30d: 18,
    falseAlertRate: 72,
    codeSync: "divergent",
    lastVisit: "09/05/2026",
    sensors: { temperature: 91, pressure: 4.2, vibration: 8.7 },
  },
  {
    id: "M-BL-042",
    name: "Caldeira Principal",
    client: "Belmare Cosméticos",
    location: "Diadema/SP",
    status: "warning",
    lastAlert: "há 4h",
    alertCount30d: 11,
    falseAlertRate: 64,
    codeSync: "divergent",
    lastVisit: "02/05/2026",
    sensors: { temperature: 78, pressure: 6.1, vibration: 3.2 },
  },
  {
    id: "M-AN-201",
    name: "Misturador Batch A",
    client: "Anaclara Alimentos",
    location: "Boituva/SP",
    status: "warning",
    lastAlert: "há 1d",
    alertCount30d: 7,
    falseAlertRate: 57,
    codeSync: "ok",
    lastVisit: "14/05/2026",
    sensors: { temperature: 65, pressure: 2.8, vibration: 1.9 },
  },
  {
    id: "M-AN-202",
    name: "Misturador Batch B",
    client: "Anaclara Alimentos",
    location: "Boituva/SP",
    status: "ok",
    lastAlert: "há 3d",
    alertCount30d: 3,
    falseAlertRate: 33,
    codeSync: "ok",
    lastVisit: "14/05/2026",
    sensors: { temperature: 62, pressure: 2.7, vibration: 1.6 },
  },
  {
    id: "M-PG-077",
    name: "Prensa Hidráulica",
    client: "Pampulha Papel",
    location: "Ponta Grossa/PR",
    status: "warning",
    lastAlert: "há 6h",
    alertCount30d: 9,
    falseAlertRate: 78,
    codeSync: "unknown",
    lastVisit: "28/04/2026",
    sensors: { temperature: 55, pressure: 12.4, vibration: 5.1 },
  },
  {
    id: "M-CB-015",
    name: "Reator Químico R1",
    client: "Cubatão Sódio",
    location: "Cubatão/SP",
    status: "ok",
    lastAlert: "há 5d",
    alertCount30d: 2,
    falseAlertRate: 50,
    codeSync: "ok",
    lastVisit: "10/05/2026",
    sensors: { temperature: 145, pressure: 8.9, vibration: 2.3 },
  },
  {
    id: "M-AS-033",
    name: "Linha de Envase",
    client: "Aspáragos Alimentos",
    location: "Campinas/SP",
    status: "ok",
    lastAlert: "há 2d",
    alertCount30d: 4,
    falseAlertRate: 75,
    codeSync: "ok",
    lastVisit: "08/05/2026",
    sensors: { temperature: 42, pressure: 1.4, vibration: 0.8 },
  },
  {
    id: "M-MN-091",
    name: "Britador Primário",
    client: "Mineração Norte",
    location: "Parauapebas/PA",
    status: "offline",
    lastAlert: "há 12h",
    alertCount30d: 0,
    falseAlertRate: 0,
    codeSync: "unknown",
    lastVisit: "01/05/2026",
    sensors: { temperature: 0, pressure: 0, vibration: 0 },
  },
];

export interface CommissioningItem {
  id: string;
  machine: string;
  client: string;
  location: string;
  status: "delayed" | "fine" | "scheduled" | "at_risk";
  daysWaiting: number;
  contractualDeadline: string;
  engineer: string;
  estimatedDays: number;
  revenue: number;
}

export const commissioningBacklog: CommissioningItem[] = [
  {
    id: "COM-2026-041",
    machine: "Misturador Batch C",
    client: "Anaclara Alimentos",
    location: "Boituva/SP",
    status: "fine",
    daysWaiting: 48,
    contractualDeadline: "30/05/2026",
    engineer: "Cláudia Santarém",
    estimatedDays: 6,
    revenue: 195000,
  },
  {
    id: "COM-2026-042",
    machine: "Misturador Batch D",
    client: "Anaclara Alimentos",
    location: "Boituva/SP",
    status: "fine",
    daysWaiting: 45,
    contractualDeadline: "30/05/2026",
    engineer: "Anderson Vasconcellos",
    estimatedDays: 6,
    revenue: 195000,
  },
  {
    id: "COM-2026-043",
    machine: "Linha de Embalagem",
    client: "Anaclara Alimentos",
    location: "Boituva/SP",
    status: "at_risk",
    daysWaiting: 42,
    contractualDeadline: "15/06/2026",
    engineer: "Júnior Almeida",
    estimatedDays: 8,
    revenue: 195000,
  },
  {
    id: "COM-2026-044",
    machine: "Sistema de Dosagem",
    client: "Anaclara Alimentos",
    location: "Boituva/SP",
    status: "at_risk",
    daysWaiting: 40,
    contractualDeadline: "15/06/2026",
    engineer: "Cláudia Santarém",
    estimatedDays: 7,
    revenue: 195000,
  },
  {
    id: "COM-2026-038",
    machine: "Compressor Atlas",
    client: "Belmare Cosméticos",
    location: "Diadema/SP",
    status: "delayed",
    daysWaiting: 62,
    contractualDeadline: "01/05/2026",
    engineer: "Anderson Vasconcellos",
    estimatedDays: 5,
    revenue: 87000,
  },
  {
    id: "COM-2026-039",
    machine: "Reator R2",
    client: "Cubatão Sódio",
    location: "Cubatão/SP",
    status: "delayed",
    daysWaiting: 55,
    contractualDeadline: "05/05/2026",
    engineer: "Cláudia Santarém",
    estimatedDays: 12,
    revenue: 142000,
  },
  {
    id: "COM-2026-040",
    machine: "Transportador de Correia",
    client: "Mineração Norte",
    location: "Parauapebas/PA",
    status: "scheduled",
    daysWaiting: 28,
    contractualDeadline: "10/06/2026",
    engineer: "Júnior Almeida",
    estimatedDays: 4,
    revenue: 68000,
  },
];

export interface Incident {
  id: string;
  date: string;
  machine: string;
  client: string;
  type: "code_drift" | "false_alert" | "downtime" | "nps";
  severity: "critical" | "high" | "medium";
  description: string;
  loss: number;
  resolved: boolean;
  rootCause: string;
}

export const incidents: Incident[] = [
  {
    id: "INC-2026-018",
    date: "12/03/2026",
    machine: "Linha de Produção 2",
    client: "Belmare Cosméticos",
    type: "code_drift",
    severity: "critical",
    description: "Hotfix de timer (45min→30min) não sincronizado com Git. Deploy sobrescreveu fix. Linha parada 36h.",
    loss: 140000,
    resolved: true,
    rootCause: "Técnico Anderson não deu push após hotfix em campo (VLAN restrita)",
  },
  {
    id: "INC-2026-024",
    date: "08/04/2026",
    machine: "Misturador M-AS-033",
    client: "Aspáragos Alimentos",
    type: "code_drift",
    severity: "high",
    description: "Setpoint de temperatura incorreto após atualização. Produção fora de spec por 2h.",
    loss: 80000,
    resolved: true,
    rootCause: "Versão do Git não refletia ajuste de campo do técnico Joelson",
  },
  {
    id: "INC-2026-031",
    date: "29/04/2026",
    machine: "Prensa PG-077",
    client: "Pampulha Papel",
    type: "code_drift",
    severity: "high",
    description: "Setpoint de pressão errado, supervisório mascarou. 2h de produção fora de spec.",
    loss: 30000,
    resolved: true,
    rootCause: "Divergência entre código em campo e repositório Git central",
  },
  {
    id: "INC-2026-035",
    date: "05/05/2026",
    machine: "Extrusora M-VH-118",
    client: "Vinhal Alimentos",
    type: "false_alert",
    severity: "medium",
    description: "4 visitas técnicas falsas em 12 semanas. Sensor de temperatura com threshold genérico.",
    loss: 12600,
    resolved: false,
    rootCause: "Threshold fixo de 85°C não considera contexto de máquina de alimentos",
  },
  {
    id: "INC-2026-036",
    date: "14/05/2026",
    machine: "Caldeira BL-042",
    client: "Belmare Cosméticos",
    type: "code_drift",
    severity: "critical",
    description: "Divergência detectada entre código em campo e Git. Próximo deploy em risco.",
    loss: 0,
    resolved: false,
    rootCause: "Hotfix não documentado — Anderson Vasconcellos (7º fim de semana consecutivo)",
  },
];

export const alertTrendData = [
  { month: "Nov/25", total: 142, false: 82, real: 60 },
  { month: "Dez/25", total: 138, false: 79, real: 59 },
  { month: "Jan/26", total: 155, false: 94, real: 61 },
  { month: "Fev/26", total: 161, false: 101, real: 60 },
  { month: "Mar/26", total: 148, false: 93, real: 55 },
  { month: "Abr/26", total: 172, false: 110, real: 62 },
  { month: "Mai/26", total: 89, false: 57, real: 32 },
];

export const savingsProjection = [
  { phase: "Fase 1 (Sem 1-4)", accumulated: 0, monthly: 0, label: "Baseline" },
  { phase: "Fase 1 Ativa", accumulated: 780000, monthly: 25000, label: "Anaclara + Thresholds" },
  { phase: "Fase 2 (Sem 5-8)", accumulated: 880000, monthly: 35000, label: "+ GitOps + App Campo" },
  { phase: "Fase 3 (Sem 9-12)", accumulated: 1050000, monthly: 55000, label: "+ IA Preditiva" },
  { phase: "12 meses", accumulated: 1320000, monthly: 55000, label: "Regime Pleno" },
];

export const teamData = [
  { name: "Cláudia Santarém", role: "Coord. Engenharia", workload: 95, status: "critical" as AlertStatus },
  { name: "Anderson Vasconcellos", role: "Eng. Aplicação Sr.", workload: 88, status: "warning" as AlertStatus },
  { name: "Júnior Almeida", role: "Eng. Aplicação", workload: 82, status: "warning" as AlertStatus },
  { name: "Fernanda Rocha", role: "Eng. Aplicação Jr.", workload: 70, status: "ok" as AlertStatus },
];
