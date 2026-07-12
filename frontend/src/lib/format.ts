export const inr = (n: number, decimals = 0): string =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals,
  }).format(n);

export const compactInr = (n: number): string => {
  const abs = Math.abs(n);
  if (abs >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`;
  if (abs >= 1e5) return `₹${(n / 1e5).toFixed(2)} L`;
  if (abs >= 1e3) return `₹${(n / 1e3).toFixed(1)}K`;
  return `₹${n.toFixed(0)}`;
};

export const pct = (n: number): string => `${n >= 0 ? "+" : ""}${n.toFixed(2)}%`;

export const upDown = (n: number): string => (n >= 0 ? "up" : "down");

// Consistent categorical palette for charts.
export const PALETTE = [
  "#5b8cff", "#7c5cff", "#3ecf8e", "#ffb454", "#ff6b6b",
  "#8ad4ff", "#b39dff", "#7ee0c0", "#ffcf6b", "#ff9db0",
];

export const assetTagClass = (assetClass: string): string => {
  const m: Record<string, string> = {
    Equity: "equity", "Mutual Fund": "mf", ETF: "etf",
    Bond: "bond", REIT: "reit", InvIT: "invit", Gold: "gold",
  };
  return m[assetClass] ?? "equity";
};

export const suitClass = (s: string): string =>
  s === "Suitable" ? "suit" : s === "Caution" ? "caution" : "unsuit";
