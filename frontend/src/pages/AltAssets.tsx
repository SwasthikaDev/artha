import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { AltAsset } from "../api/types";
import { useApp } from "../App";
import { compactInr, suitClass } from "../lib/format";

const FILTERS = ["All", "REIT", "InvIT", "Bond"];

export default function AltAssets() {
  const { investorId, profileVersion } = useApp();
  const [assets, setAssets] = useState<AltAsset[]>([]);
  const [filter, setFilter] = useState("All");
  const [selected, setSelected] = useState<AltAsset | null>(null);
  const [hasProfile, setHasProfile] = useState(true);

  useEffect(() => {
    api.altAssets(investorId).then(setAssets).catch(() => {});
    api.getRiskProfile(investorId).then((r) => setHasProfile(!!r)).catch(() => {});
  }, [investorId, profileVersion]);

  const shown = useMemo(
    () => (filter === "All" ? assets : assets.filter((a) => a.asset_class === filter)),
    [assets, filter]
  );

  return (
    <>
      {!hasProfile && (
        <div className="flag" style={{ marginBottom: 18 }}>
          <span className="warn">◈</span>
          <span>
            Complete your <Link to="/risk" style={{ color: "var(--brand)", fontWeight: 700 }}>Risk Profile</Link>{" "}
            to see personalized suitability for each instrument.
          </span>
        </div>
      )}

      <div className="suggestions" style={{ marginBottom: 18 }}>
        {FILTERS.map((f) => (
          <div
            key={f}
            className="suggestion"
            style={filter === f ? { borderColor: "var(--brand)", color: "var(--text)" } : {}}
            onClick={() => setFilter(f)}
          >
            {f}
          </div>
        ))}
      </div>

      <div className="grid cols-3">
        {shown.map((a) => (
          <div className="card alt-card" key={a.id}>
            <div className="alt-head">
              <div>
                <div style={{ fontWeight: 800, fontSize: 15 }}>{a.name}</div>
                <div className="muted" style={{ fontSize: 12 }}>{a.category}</div>
              </div>
              {a.yield_pct != null && <div className="alt-yield">{a.yield_pct}%</div>}
            </div>

            <span className={`pill ${suitClass(a.suitability)}`} style={{ alignSelf: "flex-start" }}>
              {a.suitability === "Suitable" ? "✓" : a.suitability === "Caution" ? "!" : "✕"} {a.suitability}
            </span>

            <p className="muted" style={{ fontSize: 13, lineHeight: 1.5, margin: 0 }}>{a.summary}</p>

            <div className="alt-meta">
              <span>Risk <b>{a.risk_level}</b></span>
              {a.rating && <span>Rating <b>{a.rating}</b></span>}
              <span>Min <b>{compactInr(a.min_investment)}</b></span>
            </div>

            {a.suitability_reason && (
              <div className="muted" style={{ fontSize: 12, fontStyle: "italic" }}>
                {a.suitability_reason}
              </div>
            )}

            <button className="btn ghost" style={{ marginTop: "auto" }} onClick={() => setSelected(a)}>
              Learn more
            </button>
          </div>
        ))}
      </div>

      {selected && <EducationModal asset={selected} onClose={() => setSelected(null)} />}
    </>
  );
}

function EducationModal({ asset, onClose }: { asset: AltAsset; onClose: () => void }) {
  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed", inset: 0, background: "rgba(4,8,20,0.7)",
        display: "grid", placeItems: "center", padding: 20, zIndex: 50,
      }}
    >
      <div
        className="card"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: 620, width: "100%", maxHeight: "85vh", overflowY: "auto" }}
      >
        <div className="alt-head">
          <div>
            <h3 style={{ fontSize: 20 }}>{asset.name}</h3>
            <div className="muted" style={{ fontSize: 13 }}>{asset.category} · {asset.asset_class}</div>
          </div>
          <button className="btn ghost" onClick={onClose}>✕</button>
        </div>

        <div className="alt-meta" style={{ marginTop: 16 }}>
          {asset.yield_pct != null && <span>Yield <b className="up">{asset.yield_pct}%</b></span>}
          <span>Risk <b>{asset.risk_level}</b></span>
          {asset.rating && <span>Rating <b>{asset.rating}</b></span>}
          <span>Liquidity <b>{asset.liquidity}</b></span>
          {asset.tenure && <span>Tenure <b>{asset.tenure}</b></span>}
          <span>Min <b>{compactInr(asset.min_investment)}</b></span>
        </div>

        <div className="section-title" style={{ marginTop: 22 }}>What is this?</div>
        <p style={{ lineHeight: 1.65, fontSize: 14 }}>{asset.education}</p>

        {asset.highlights.length > 0 && (
          <>
            <div className="section-title">Highlights</div>
            {asset.highlights.map((h, i) => (
              <div className="insight" key={i}><span className="dot">✓</span> {h}</div>
            ))}
          </>
        )}

        <div className="section-title">Suitability for you</div>
        <div className={`flag`} style={{ background: "var(--panel-2)", borderColor: "var(--border)" }}>
          <span className={suitClass(asset.suitability) === "suit" ? "up" : suitClass(asset.suitability) === "caution" ? "warn" : "down"}>
            {asset.suitability}
          </span>
          <span>— {asset.suitability_reason}</span>
        </div>

        <button className="btn" style={{ marginTop: 18, width: "100%" }}>
          Invest (demo) — routes to partner RTA / exchange
        </button>
      </div>
    </div>
  );
}
