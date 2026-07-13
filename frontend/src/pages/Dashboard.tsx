import { useEffect, useState } from "react";
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { HealthScore, Nudge, Portfolio } from "../api/types";
import { useApp } from "../App";
import { assetTagClass, compactInr, inr, PALETTE, pct, upDown } from "../lib/format";

const gradeColor = (grade: string) =>
  grade?.startsWith("A") ? "var(--green)" : grade === "B" ? "#8ad4ff" : grade === "C" ? "var(--amber)" : "var(--red)";

export default function Dashboard() {
  const { investorId, profileVersion } = useApp();
  const [p, setP] = useState<Portfolio | null>(null);
  const [health, setHealth] = useState<HealthScore | null>(null);
  const [nudges, setNudges] = useState<Nudge[]>([]);

  useEffect(() => {
    setP(null);
    api.portfolio(investorId).then(setP).catch(() => {});
    api.healthScore(investorId).then(setHealth).catch(() => {});
    api.nudges(investorId).then(setNudges).catch(() => {});
  }, [investorId, profileVersion]);

  if (!p) return <div className="loading">Aggregating your holdings across brokers & depositories…</div>;

  const s = p.summary;
  const pieData = Object.values(
    p.holdings.reduce<Record<string, { name: string; value: number }>>((acc, h) => {
      acc[h.asset_class] ??= { name: h.asset_class, value: 0 };
      acc[h.asset_class].value += h.current_value;
      return acc;
    }, {})
  );

  return (
    <>
      {/* KPI row */}
      <div className="grid cols-4">
        <div className="card stat">
          <div className="label">Total Value</div>
          <div className="value">{inr(s.total_current_value)}</div>
          <div className={`delta ${upDown(s.day_change)}`}>
            {pct(s.day_change_pct)} today ({inr(s.day_change)})
          </div>
        </div>
        <div className="card stat">
          <div className="label">Invested</div>
          <div className="value">{inr(s.total_invested)}</div>
          <div className="delta muted">Cost basis</div>
        </div>
        <div className="card stat">
          <div className="label">Total P&L</div>
          <div className={`value ${upDown(s.total_pnl)}`}>{inr(s.total_pnl)}</div>
          <div className={`delta ${upDown(s.total_pnl)}`}>{pct(s.total_pnl_pct)} overall</div>
        </div>
        <Link to="/health" className="card stat" style={{ textDecoration: "none", color: "inherit" }}>
          <div className="label">Health Score</div>
          <div className="value" style={{ color: health ? gradeColor(health.grade) : undefined }}>
            {health ? health.grade : "…"}
            {health && <span className="muted" style={{ fontSize: 15 }}> · {health.score}/100</span>}
          </div>
          <div className="delta muted">{s.holdings_count} holdings · {s.accounts.length} accounts →</div>
        </Link>
      </div>

      {/* Smart nudges */}
      {nudges.length > 0 && (
        <>
          <div className="section-title">Smart Nudges</div>
          <div className="grid cols-3">
            {nudges.slice(0, 3).map((n, i) => (
              <div className="card" key={i} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <span className="chip" style={{ alignSelf: "flex-start", textTransform: "capitalize" }}>{n.kind}</span>
                <b style={{ fontSize: 14 }}>{n.title}</b>
                <div className="muted" style={{ fontSize: 12, lineHeight: 1.5, flex: 1 }}>{n.detail}</div>
                {n.cta && (
                  <Link to={n.kind === "education" ? "/risk" : "/explore"} style={{ color: "var(--brand)", fontSize: 12, fontWeight: 700 }}>
                    {n.cta} →
                  </Link>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {/* Allocation + accounts */}
      <div className="grid cols-2" style={{ marginTop: 18 }}>
        <div className="card">
          <h3>Asset Allocation</h3>
          <div className="sub">Consolidated across all your accounts</div>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                innerRadius={62}
                outerRadius={100}
                paddingAngle={2}
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={PALETTE[i % PALETTE.length]} stroke="none" />
                ))}
              </Pie>
              <Tooltip
                formatter={(v: number) => inr(v)}
                contentStyle={{ background: "#161f38", border: "1px solid #26314f", borderRadius: 10 }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Linked Accounts</h3>
          <div className="sub">Simulated via Account Aggregator / NSDL-CDSL consent</div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Broker</th>
                  <th>Depository</th>
                  <th className="num">Holdings</th>
                  <th className="num">Value</th>
                </tr>
              </thead>
              <tbody>
                {s.accounts.map((a) => (
                  <tr key={a.broker}>
                    <td><b>{a.broker}</b></td>
                    <td><span className="chip">{a.depository}</span></td>
                    <td className="num">{a.holdings_count}</td>
                    <td className="num">{compactInr(a.current_value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Holdings */}
      <div className="section-title">All Holdings</div>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Instrument</th>
                <th>Class</th>
                <th>Broker</th>
                <th className="num">Qty</th>
                <th className="num">Avg</th>
                <th className="num">LTP</th>
                <th className="num">Value</th>
                <th className="num">P&L</th>
              </tr>
            </thead>
            <tbody>
              {p.holdings.map((h) => (
                <tr key={`${h.broker}-${h.symbol}`}>
                  <td>
                    <b>{h.symbol}</b>
                    <div className="muted" style={{ fontSize: 11 }}>{h.name}</div>
                  </td>
                  <td><span className={`tag ${assetTagClass(h.asset_class)}`}>{h.asset_class}</span></td>
                  <td>{h.broker}</td>
                  <td className="num">{h.quantity}</td>
                  <td className="num">{inr(h.avg_cost)}</td>
                  <td className="num">{inr(h.ltp)}</td>
                  <td className="num">{inr(h.current_value)}</td>
                  <td className={`num ${upDown(h.pnl)}`}>
                    {inr(h.pnl)}
                    <div style={{ fontSize: 11 }}>{pct(h.pnl_pct)}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
