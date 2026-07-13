// Mirrors the backend Pydantic schemas.

export interface Investor {
  id: string;
  name: string;
  tagline: string;
}

export interface HoldingView {
  symbol: string;
  name: string;
  asset_class: string;
  sector: string;
  broker: string;
  depository: string;
  quantity: number;
  avg_cost: number;
  ltp: number;
  invested: number;
  current_value: number;
  pnl: number;
  pnl_pct: number;
}

export interface AccountSummary {
  broker: string;
  depository: string;
  holdings_count: number;
  current_value: number;
}

export interface PortfolioSummary {
  investor_id: string;
  investor_name: string;
  total_invested: number;
  total_current_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  day_change: number;
  day_change_pct: number;
  holdings_count: number;
  accounts: AccountSummary[];
}

export interface Portfolio {
  investor_id: string;
  investor_name: string;
  summary: PortfolioSummary;
  holdings: HoldingView[];
}

export interface AllocationSlice {
  label: string;
  value: number;
  pct: number;
}

export interface ConcentrationItem {
  label: string;
  pct: number;
  flag: boolean;
}

export interface RiskMetrics {
  hhi: number;
  hhi_rating: string;
  diversification_score: number;
  equity_pct: number;
  est_volatility: number;
  top_holding_pct: number;
  concentration_flags: string[];
}

export interface Analytics {
  allocation_by_asset_class: AllocationSlice[];
  allocation_by_sector: AllocationSlice[];
  allocation_by_broker: AllocationSlice[];
  top_holdings: ConcentrationItem[];
  risk_metrics: RiskMetrics;
  insights: string[];
}

export interface RiskQuestionOption {
  label: string;
  points: number;
}

export interface RiskQuestion {
  id: string;
  question: string;
  options: RiskQuestionOption[];
}

export interface RiskProfileResult {
  score: number;
  category: string;
  description: string;
  recommended_equity_band: string;
  suitable_asset_classes: string[];
}

export interface AltAsset {
  id: string;
  name: string;
  asset_class: string;
  category: string;
  ticker?: string | null;
  yield_pct?: number | null;
  rating?: string | null;
  risk_level: string;
  min_investment: number;
  liquidity: string;
  tenure?: string | null;
  summary: string;
  highlights: string[];
  education: string;
  suitability: "Suitable" | "Caution" | "Unsuitable";
  suitability_reason: string;
}

export interface AdvisorResponse {
  reply: string;
  grounded_on: string[];
  source: string;
}

export interface XRayExposure {
  symbol: string;
  name: string;
  sector: string;
  apparent_value: number;
  apparent_pct: number;
  true_value: number;
  true_pct: number;
  hidden_value: number;
  via_funds: string[];
  flag: boolean;
}

export interface XRaySectorExposure {
  sector: string;
  apparent_pct: number;
  true_pct: number;
  delta_pct: number;
}

export interface XRay {
  exposures: XRayExposure[];
  sector_exposures: XRaySectorExposure[];
  top_hidden: XRayExposure[];
  headline: string;
  insights: string[];
}

export interface HealthComponent {
  label: string;
  score: number;
  weight: number;
  detail: string;
}

export interface ProtectionAlert {
  severity: "high" | "medium" | "low";
  title: string;
  detail: string;
  holding?: string | null;
}

export interface HealthScore {
  score: number;
  grade: string;
  summary: string;
  components: HealthComponent[];
  protection_alerts: ProtectionAlert[];
}

export interface QuizOption {
  label: string;
  correct: boolean;
}

export interface QuizQuestion {
  asset_id: string;
  question: string;
  options: QuizOption[];
  explanation: string;
}

export interface Nudge {
  kind: "gap" | "concentration" | "opportunity" | "education";
  title: string;
  detail: string;
  cta: string;
  asset_id?: string | null;
}

export interface SystemStatus {
  market_data: string;
  ai_advisor: string;
}
