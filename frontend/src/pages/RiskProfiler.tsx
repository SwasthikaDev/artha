import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { RiskProfileResult, RiskQuestion } from "../api/types";
import { useApp } from "../App";

export default function RiskProfiler() {
  const { investorId, bumpProfile } = useApp();
  const nav = useNavigate();
  const [questions, setQuestions] = useState<RiskQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<RiskProfileResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.riskQuestions().then(setQuestions).catch(() => {});
    api.getRiskProfile(investorId).then((r) => r && setResult(r)).catch(() => {});
  }, [investorId]);

  const allAnswered = questions.length > 0 && questions.every((q) => q.id in answers);

  const submit = async () => {
    setSubmitting(true);
    try {
      const payload = questions.map((q) => ({ question_id: q.id, option_index: answers[q.id] }));
      const r = await api.submitRiskProfile(investorId, payload);
      setResult(r);
      bumpProfile();
    } finally {
      setSubmitting(false);
    }
  };

  const retake = () => {
    setResult(null);
    setAnswers({});
  };

  if (result) {
    return (
      <div className="grid cols-2">
        <div className="card">
          <h3>Your Risk Profile</h3>
          <div className="sub">Based on your questionnaire responses</div>
          <div className="score-ring" style={{ marginTop: 10 }}>
            <div className="score-num">{result.score}</div>
            <div>
              <div style={{ fontSize: 22, fontWeight: 800 }}>{result.category}</div>
              <div className="muted" style={{ fontSize: 13 }}>Recommended: {result.recommended_equity_band}</div>
            </div>
          </div>
          <div className="meter" style={{ marginTop: 18 }}>
            <span style={{ width: `${result.score}%` }} />
          </div>
          <p style={{ marginTop: 16, lineHeight: 1.6, fontSize: 14 }}>{result.description}</p>
        </div>

        <div className="card">
          <h3>Suitable Asset Classes</h3>
          <div className="sub">These now personalize your Alt-Asset suitability tags</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 12 }}>
            {result.suitable_asset_classes.map((c) => (
              <span key={c} className="pill suit">{c}</span>
            ))}
          </div>
          <div style={{ display: "flex", gap: 10, marginTop: 28 }}>
            <button className="btn" onClick={() => nav("/explore")}>
              Explore matched alt-assets →
            </button>
            <button className="btn ghost" onClick={retake}>Retake</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ maxWidth: 760 }}>
      <h3>Risk Profiling Questionnaire</h3>
      <div className="sub">
        Five quick questions. Your answers drive the suitability engine — every alt-asset
        gets tagged Suitable / Caution / Unsuitable for you.
      </div>

      {questions.map((q, qi) => (
        <div className="q-block" key={q.id}>
          <div className="q">{qi + 1}. {q.question}</div>
          <div className="options">
            {q.options.map((opt, oi) => (
              <div
                key={oi}
                className={`option ${answers[q.id] === oi ? "selected" : ""}`}
                onClick={() => setAnswers((a) => ({ ...a, [q.id]: oi }))}
              >
                {opt.label}
              </div>
            ))}
          </div>
        </div>
      ))}

      <button className="btn" disabled={!allAnswered || submitting} onClick={submit}>
        {submitting ? "Scoring…" : "Get my risk profile"}
      </button>
    </div>
  );
}
