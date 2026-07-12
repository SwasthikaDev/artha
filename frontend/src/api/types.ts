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

export interface SystemStatus {
  market_data: string;
  ai_advisor: string;
}
