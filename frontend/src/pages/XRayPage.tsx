import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api/client";
import type { XRay } from "../api/types";
import { useApp } from "../App";
import { compactInr } from "../lib/format";

export default function XRayPage() {
  const { investorId } = useApp();
  const [x, setX] = useState<XRay | null>(null);

  useEffect(() => {
    setX(null);
    api.xray(investorId).then(setX).catch(() => {});
  }, [investorId]);

  if (!x) return <div className="loading">Looking through your funds to their underlying holdings…</div>;

  const chartData = x.exposures
    .filter((e) => e.true_pct >= 1)
    .slice(0, 8)
    .map((e) => ({ name: e.name, Direct: e.apparent_pct, "Hidden (via funds)": +(e.true_pct - e.apparent_pct).toFixed(2) }));

  return (
    <>
      <div className="card" style={{ background: "linear-gradient(135deg, #1a2547, #201a45)", marginBottom: 18 }}>
        <div className="sub" style={{ textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--brand)" }}>
          Portfolio X-Ray · Look-Through Analysis
        </div>
        <div style={{ fontSize: 20, fontWeight: 800, lineHeight: 1.4, marginTop: 6 }}>{x.headline}</div>
        <div className="muted" style={{ fontSize: 13, marginTop: 8 }}>
          Your mutual funds & ETFs hold underlying stocks. We decompose them to reveal your
          <b style={{ color: "var(--text)" }}> true </b> concentration — the risk a surface view hides.
        </div>
      </div>

      {/* Top hidden exposures */}
      <div className="grid cols-3">
        {x.top_hidden.slice(0, 3).map((e) => (
          <div className="card stat" key={e.symbol}>
            <div className="label">{e.name}</div>
            <div className="value">
              {e.apparent_pct.toFixed(0)}% <span className="muted" style={{ fontSize: 16 }}>→</span>{" "}
              <span className={e.flag ? "warn" : "up"}>{e.true_pct.toFixed(0)}%</span>
            </div>
            <div className="delta muted">
              +{compactInr(e.hidden_value)} hidden{e.via_funds.length ? ` via ${e.via_funds[0].split(" ")[0]}…` : ""}
            </div>
          </div>
        ))}
      </div>

      {/* Apparent vs true stacked bar */}
      <div className="section-title">Direct vs. Look-Through Exposure</div>
      <div className="card">
        <div className="sub">Blue = held directly · Purple = hidden inside your funds. Total bar = your TRUE exposure.</div>
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 40 }}>
            <XAxis type="number" tick={{ fill: "#9aa8c7", fontSize: 12 }} unit="%" />
            <YAxis type="category" dataKey="name" width={130} tick={{ fill: "#9aa8c7", fontSize: 11 }} />
            <Tooltip
              formatter={(v: number) => `${v.toFixed(1)}%`}
              contentStyle={{ background: "#161f38", border: "1px solid #26314f", borderRadius: 10 }}
              cursor={{ fill: "rgba(91,140,255,0.08)" }}
            />
            <Legend />
            <Bar dataKey="Direct" stackId="a" fill="#5b8cff" radius={[0, 0, 0, 0]} />
            <Bar dataKey="Hidden (via funds)" stackId="a" fill="#7c5cff" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      <div className="section-title">What This Reveals</div>
      <div className="card">
        {x.insights.map((ins, i) => (
          <div className="insight" key={i}>
            <span className="dot">◆</span> {ins}
          </div>
        ))}
      </div>

      {/* Full table */}
      <div className="section-title">Full Look-Through Breakdown</div>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Underlying</th>
                <th>Sector</th>
                <th className="num">Direct</th>
                <th className="num">True</th>
                <th className="num">Hidden</th>
                <th>Via funds</th>
              </tr>
            </thead>
            <tbody>
              {x.exposures.filter((e) => e.true_pct >= 0.5).map((e) => (
                <tr key={e.symbol}>
                  <td><b>{e.name}</b></td>
                  <td className="muted">{e.sector}</td>
                  <td className="num">{e.apparent_pct.toFixed(1)}%</td>
                  <td className={`num ${e.flag ? "warn" : ""}`}><b>{e.true_pct.toFixed(1)}%</b></td>
                  <td className="num up">{e.hidden_value > 0 ? `+${e.hidden_value > 0 ? (e.true_pct - e.apparent_pct).toFixed(1) : 0}pp` : "—"}</td>
                  <td className="muted" style={{ fontSize: 11 }}>{e.via_funds.join(", ") || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
