import { useEffect, useState } from "react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api/client";
import type { Analytics } from "../api/types";
import { useApp } from "../App";
import { inr, PALETTE } from "../lib/format";

export default function AnalyticsPage() {
  const { investorId } = useApp();
  const [a, setA] = useState<Analytics | null>(null);

  useEffect(() => {
    setA(null);
    api.analytics(investorId).then(setA).catch(() => {});
  }, [investorId]);

  if (!a) return <div className="loading">Computing allocation, concentration & risk metrics…</div>;

  const rm = a.risk_metrics;
  const sectorData = a.allocation_by_sector.map((s) => ({ name: s.label, pct: s.pct }));

  return (
    <>
      {/* Risk metric KPIs */}
      <div className="grid cols-4">
        <div className="card stat">
          <div className="label">Diversification</div>
          <div className="value">{rm.diversification_score.toFixed(0)}<span style={{ fontSize: 16 }}>/100</span></div>
          <div className="meter" style={{ marginTop: 10 }}>
            <span style={{ width: `${rm.diversification_score}%` }} />
          </div>
        </div>
        <div className="card stat">
          <div className="label">Concentration (HHI)</div>
          <div className="value">{rm.hhi.toFixed(0)}</div>
          <div className="delta muted">{rm.hhi_rating}</div>
        </div>
        <div className="card stat">
          <div className="label">Equity Exposure</div>
          <div className={`value ${rm.equity_pct >= 75 ? "warn" : ""}`}>{rm.equity_pct.toFixed(0)}%</div>
          <div className="delta muted">of portfolio</div>
        </div>
        <div className="card stat">
          <div className="label">Est. Volatility</div>
          <div className="value">{rm.est_volatility.toFixed(0)}%</div>
          <div className="delta muted">annualized</div>
        </div>
      </div>

      {/* Concentration flags */}
      {rm.concentration_flags.length > 0 && (
        <>
          <div className="section-title">Concentration Alerts</div>
          <div className="card">
            {rm.concentration_flags.map((f, i) => (
              <div className="flag" key={i}>
                <span className="warn">⚠</span> {f}
              </div>
            ))}
          </div>
        </>
      )}

      <div className="grid cols-2" style={{ marginTop: 18 }}>
        {/* Sector exposure */}
        <div className="card">
          <h3>Sector Exposure</h3>
          <div className="sub">Where your money is concentrated</div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={sectorData} layout="vertical" margin={{ left: 20 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="name" width={90} tick={{ fill: "#9aa8c7", fontSize: 12 }} />
              <Tooltip
                formatter={(v: number) => `${v.toFixed(1)}%`}
                contentStyle={{ background: "#161f38", border: "1px solid #26314f", borderRadius: 10 }}
                cursor={{ fill: "rgba(91,140,255,0.08)" }}
              />
              <Bar dataKey="pct" radius={[0, 6, 6, 0]}>
                {sectorData.map((_, i) => (
                  <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top holdings concentration */}
        <div className="card">
          <h3>Top Holdings</h3>
          <div className="sub">Single-holding concentration (flagged above 15%)</div>
          <div style={{ marginTop: 8 }}>
            {a.top_holdings.map((t) => (
              <div className="alloc-row" key={t.label}>
                <div className="lbl" style={{ width: 150, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {t.label}
                </div>
                <div className="bar">
                  <div className="meter">
                    <span style={{ width: `${Math.min(t.pct * 3, 100)}%`, background: t.flag ? "linear-gradient(90deg,#ffb454,#ff6b6b)" : undefined }} />
                  </div>
                </div>
                <div className={`pct ${t.flag ? "warn" : ""}`}>{t.pct.toFixed(1)}%</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="section-title">Portfolio Insights</div>
      <div className="card">
        {a.insights.map((ins, i) => (
          <div className="insight" key={i}>
            <span className="dot">•</span> {ins}
          </div>
        ))}
      </div>

      {/* Broker split */}
      <div className="section-title">Allocation by Broker</div>
      <div className="card">
        {a.allocation_by_broker.map((b) => (
          <div className="alloc-row" key={b.label}>
            <div className="lbl">{b.label}</div>
            <div className="bar"><div className="meter"><span style={{ width: `${b.pct}%` }} /></div></div>
            <div className="pct">{b.pct.toFixed(1)}%</div>
          </div>
        ))}
      </div>
    </>
  );
}
