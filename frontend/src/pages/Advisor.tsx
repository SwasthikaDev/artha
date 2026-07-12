import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { useApp } from "../App";

interface Msg {
  role: "user" | "assistant";
  content: string;
  grounded?: string[];
  source?: string;
}

const SUGGESTIONS = [
  "Am I over-concentrated in IT?",
  "How diversified is my portfolio?",
  "How am I performing overall?",
  "Should I look at REITs or bonds?",
];

export default function Advisor() {
  const { investorId } = useApp();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content:
          "Hi! I'm your UnifyInvest advisor. I can see your consolidated portfolio across all your accounts. Ask me about concentration, diversification, performance, or alternate assets.",
      },
    ]);
  }, [investorId]);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  const send = async (text: string) => {
    const q = text.trim();
    if (!q || busy) return;
    const history = messages
      .filter((m) => m.content)
      .map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { role: "user", content: q }]);
    setInput("");
    setBusy(true);
    try {
      const res = await api.advisor(investorId, q, history);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.reply, grounded: res.grounded_on, source: res.source },
      ]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Sorry — I couldn't reach the advisor service." }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card chat">
      <div className="chat-log" ref={logRef}>
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role === "user" ? "user" : "bot"}`}>
            {m.content}
            {m.grounded && m.grounded.length > 0 && (
              <div className="grounded">
                Grounded on: {m.grounded.join(", ")}
                {m.source && ` · ${m.source === "claude" ? "Claude AI" : "rule-based"}`}
              </div>
            )}
          </div>
        ))}
        {busy && <div className="msg bot muted">Analyzing your portfolio…</div>}
      </div>

      <div style={{ marginTop: 14 }}>
        <div className="suggestions">
          {SUGGESTIONS.map((s) => (
            <div key={s} className="suggestion" onClick={() => send(s)}>{s}</div>
          ))}
        </div>
        <div className="chat-input">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send(input)}
            placeholder="Ask about your portfolio…"
          />
          <button className="btn" onClick={() => send(input)} disabled={busy}>Send</button>
        </div>
      </div>
    </div>
  );
}
