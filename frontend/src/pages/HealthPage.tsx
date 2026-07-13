import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { HealthScore } from "../api/types";
import { useApp } from "../App";

const gradeColor = (grade: string) =>
  grade.startsWith("A") ? "var(--green)" : grade === "B" ? "#8ad4ff" : grade === "C" ? "var(--amber)" : "var(--red)";

const sevClass = (s: string) => (s === "high" ? "unsuit" : s === "medium" ? "caution" : "suit");

export default function HealthPage() {
  const { investorId, profileVersion } = useApp();
  const [h, setH] = useState<HealthScore | null>(null);

  useEffect(() => {
    setH(null);
    api.healthScore(investorId).then(setH).catch(() => {});
  }, [investorId, profileVersion]);

  if (!h) return <div className="loading">Grading your portfolio health…</div>;

  return (
    <>
      <div className="grid cols-2">
        {/* Grade hero */}
        <div className="card" style={{ display: "flex", alignItems: "center", gap: 26 }}>
          <div
            style={{
              width: 130, height: 130, borderRadius: "50%", flexShrink: 0,
              display: "grid", placeItems: "center",
              background: `conic-gradient(${gradeColor(h.grade)} ${h.score * 3.6}deg, var(--panel-2) 0deg)`,
            }}
          >
            <div
              style={{
                width: 104, height: 104, borderRadius: "50%", background: "var(--panel)",
                display: "grid", placeItems: "center", flexDirection: "column",
              }}
            >
              <div style={{ fontSize: 40, fontWeight: 800, color: gradeColor(h.grade), lineHeight: 1 }}>{h.grade}</div>
              <div className="muted" style={{ fontSize: 12 }}>{h.score}/100</div>
            </div>
          </div>
          <div>
            <h3 style={{ fontSize: 18 }}>Portfolio Health Score</h3>
            <p style={{ fontSize: 14, lineHeight: 1.6, marginTop: 8 }}>{h.summary}</p>
          </div>
        </div>

        {/* Components */}
        <div className="card">
          <h3>How it's scored</h3>
          <div className="sub">Four weighted lenses</div>
          {h.components.map((c) => (
            <div key={c.label} style={{ marginBottom: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 5 }}>
                <span><b>{c.label}</b> <span className="muted">· {(c.weight * 100).toFixed(0)}%</span></span>
                <span style={{ fontWeight: 700 }}>{c.score.toFixed(0)}</span>
              </div>
              <div className="meter"><span style={{ width: `${c.score}%` }} /></div>
              <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>{c.detail}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Protection alerts */}
      <div className="section-title">🛡 Investor Protection Alerts</div>
      {h.protection_alerts.length === 0 ? (
        <div className="card"><div className="insight"><span className="dot up">✓</span> No protection alerts — your portfolio looks well-guarded.</div></div>
      ) : (
        <div className="grid cols-1" style={{ gap: 12 }}>
          {h.protection_alerts.map((a, i) => (
            <div className="card" key={i} style={{ borderLeft: `4px solid ${a.severity === "high" ? "var(--red)" : a.severity === "medium" ? "var(--amber)" : "var(--brand)"}` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                <span className={`pill ${sevClass(a.severity)}`}>{a.severity.toUpperCase()}</span>
                <b style={{ fontSize: 15 }}>{a.title}</b>
              </div>
              <div style={{ fontSize: 13, lineHeight: 1.6 }} className="muted">{a.detail}</div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
