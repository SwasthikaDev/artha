import { createContext, useContext, useEffect, useState } from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { api } from "./api/client";
import type { Investor, SystemStatus } from "./api/types";
import Dashboard from "./pages/Dashboard";
import AnalyticsPage from "./pages/AnalyticsPage";
import XRayPage from "./pages/XRayPage";
import HealthPage from "./pages/HealthPage";
import RiskProfiler from "./pages/RiskProfiler";
import AltAssets from "./pages/AltAssets";
import Advisor from "./pages/Advisor";

// ----- shared investor context ----------------------------------------- //
interface Ctx {
  investorId: string;
  setInvestorId: (id: string) => void;
  investors: Investor[];
  profileVersion: number;
  bumpProfile: () => void;
}
const AppCtx = createContext<Ctx>(null!);
export const useApp = () => useContext(AppCtx);

const NAV = [
  { to: "/", label: "Dashboard", ico: "◧", end: true },
  { to: "/analytics", label: "Analytics", ico: "◑" },
  { to: "/xray", label: "Portfolio X-Ray", ico: "◎" },
  { to: "/health", label: "Health Score", ico: "🛡" },
  { to: "/risk", label: "Risk Profile", ico: "◈" },
  { to: "/explore", label: "Alt-Assets", ico: "◆" },
  { to: "/advisor", label: "AI Advisor", ico: "✦" },
];

export default function App() {
  const [investorId, setInvestorId] = useState("INV001");
  const [investors, setInvestors] = useState<Investor[]>([]);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [profileVersion, setProfileVersion] = useState(0);

  useEffect(() => {
    api.investors().then(setInvestors).catch(() => {});
    api.status().then(setStatus).catch(() => {});
  }, []);

  const bumpProfile = () => setProfileVersion((v) => v + 1);

  return (
    <AppCtx.Provider value={{ investorId, setInvestorId, investors, profileVersion, bumpProfile }}>
      <div className="app">
        <aside className="sidebar">
          <div className="brand">
            <span className="logo">◈</span>
            <div>
              UnifyInvest
              <small>Multi-asset super app</small>
            </div>
          </div>
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
            >
              <span className="ico">{n.ico}</span>
              {n.label}
            </NavLink>
          ))}
          <div className="sidebar-foot">
            {status && (
              <>
                Market data: {status.market_data}
                <br />
                AI advisor: {status.ai_advisor}
                <br />
              </>
            )}
            SEBI GFF Hackathon · PS3
          </div>
        </aside>

        <main className="main">
          <div className="topbar">
            <TopbarTitle />
            <div className="investor-select">
              <span className="muted" style={{ fontSize: 12 }}>Investor</span>
              <select value={investorId} onChange={(e) => setInvestorId(e.target.value)}>
                {investors.map((i) => (
                  <option key={i.id} value={i.id}>
                    {i.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/xray" element={<XRayPage />} />
            <Route path="/health" element={<HealthPage />} />
            <Route path="/risk" element={<RiskProfiler />} />
            <Route path="/explore" element={<AltAssets />} />
            <Route path="/advisor" element={<Advisor />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </AppCtx.Provider>
  );
}

function TopbarTitle() {
  const path = window.location.pathname;
  const map: Record<string, [string, string]> = {
    "/": ["Unified Dashboard", "Your entire portfolio across every broker & depository, in one view"],
    "/analytics": ["Portfolio Analytics", "Allocation, concentration, and risk intelligence"],
    "/xray": ["Portfolio X-Ray", "Look through your funds to reveal your TRUE hidden concentration"],
    "/health": ["Portfolio Health", "Your A–F health grade and investor-protection alerts"],
    "/risk": ["Risk Profile", "Assess your risk appetite to personalize suitability"],
    "/explore": ["Alt-Asset Explorer", "Discover & learn REITs, InvITs, and bonds — matched to you"],
    "/advisor": ["AI Advisor", "Ask anything about your portfolio, in plain language"],
  };
  const [title, sub] = map[path] ?? map["/"];
  return (
    <div>
      <h1>{title}</h1>
      <p>{sub}</p>
    </div>
  );
}
