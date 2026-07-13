import type {
  AdvisorResponse,
  Analytics,
  AltAsset,
  HealthScore,
  Investor,
  Nudge,
  Portfolio,
  QuizQuestion,
  RiskProfileResult,
  RiskQuestion,
  SystemStatus,
  XRay,
} from "./types";

const BASE = "/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return res.json();
}

export const api = {
  status: () => get<SystemStatus>("/status"),
  investors: () => get<Investor[]>("/investors"),
  portfolio: (id: string) => get<Portfolio>(`/portfolio/${id}`),
  analytics: (id: string) => get<Analytics>(`/analytics/${id}`),
  riskQuestions: () => get<RiskQuestion[]>("/risk/questions"),
  getRiskProfile: (id: string) => get<RiskProfileResult | null>(`/risk/profile/${id}`),
  submitRiskProfile: (id: string, answers: { question_id: string; option_index: number }[]) =>
    post<RiskProfileResult>(`/risk/profile/${id}`, { answers }),
  altAssets: (id: string) => get<AltAsset[]>(`/alt-assets/${id}`),
  advisor: (id: string, message: string, history: { role: string; content: string }[], lang = "en") =>
    post<AdvisorResponse>("/advisor", { investor_id: id, message, history, lang }),
  xray: (id: string) => get<XRay>(`/xray/${id}`),
  healthScore: (id: string) => get<HealthScore>(`/health-score/${id}`),
  nudges: (id: string) => get<Nudge[]>(`/nudges/${id}`),
  quiz: (assetId: string) => get<QuizQuestion>(`/quiz/${assetId}`),
};
