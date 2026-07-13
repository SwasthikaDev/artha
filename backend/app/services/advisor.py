"""AI Advisor Service — natural-language Q&A grounded on the investor's own portfolio.

Builds a compact grounding context from the live portfolio + analytics, then answers via
the Claude API when ANTHROPIC_API_KEY is set. Falls back to a deterministic rule-based
advisor (still grounded on real numbers) so the feature always works in a demo.
"""
from __future__ import annotations

import os

from app.models.schemas import AdvisorResponse, Analytics, Portfolio

_SYSTEM = (
    "You are Artha's investor assistant for Indian retail investors. You are given the "
    "user's actual consolidated portfolio and analytics. Answer ONLY using these facts plus "
    "general, educational investing knowledge. Be concise, plain-spoken, and India-context aware "
    "(REITs, InvITs, SGBs, NSDL/CDSL). Never invent holdings or numbers not in the context. "
    "You are an educational assistant, not a registered investment adviser — add a one-line "
    "reminder to consult a SEBI-registered adviser for personal advice when the user asks what to buy/sell."
)


def _ground(portfolio: Portfolio, analytics: Analytics) -> tuple[str, list[str]]:
    s = portfolio.summary
    facts: list[str] = []
    lines = [
        f"Investor: {portfolio.investor_name}",
        f"Total value: Rs {s.total_current_value:,.0f}  |  Invested: Rs {s.total_invested:,.0f}",
        f"Overall P&L: Rs {s.total_pnl:,.0f} ({s.total_pnl_pct:+.1f}%)  |  Holdings: {s.holdings_count} across {len(s.accounts)} accounts",
        f"Equity exposure: {analytics.risk_metrics.equity_pct:.0f}%  |  Est. volatility: {analytics.risk_metrics.est_volatility:.0f}%",
        f"Diversification score: {analytics.risk_metrics.diversification_score:.0f}/100 (HHI {analytics.risk_metrics.hhi:.0f}, {analytics.risk_metrics.hhi_rating})",
        "Asset-class allocation: " + ", ".join(f"{a.label} {a.pct:.0f}%" for a in analytics.allocation_by_asset_class),
        "Sector allocation: " + ", ".join(f"{a.label} {a.pct:.0f}%" for a in analytics.allocation_by_sector[:6]),
        "Top holdings: " + ", ".join(f"{t.label} {t.pct:.0f}%" for t in analytics.top_holdings[:6]),
    ]
    facts.extend(f.label for f in analytics.top_holdings[:3])
    if analytics.risk_metrics.concentration_flags:
        lines.append("Concentration flags: " + "; ".join(analytics.risk_metrics.concentration_flags))
    return "\n".join(lines), facts


def answer(message: str, portfolio: Portfolio, analytics: Analytics, history: list[dict], lang: str = "en") -> AdvisorResponse:
    context, facts = _ground(portfolio, analytics)
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        try:
            return _claude_answer(message, context, facts, history, key, lang)
        except Exception:
            pass  # fall through to rule-based
    return _rule_based(message, portfolio, analytics, context, facts, lang)


def _claude_answer(message, context, facts, history, key, lang="en") -> AdvisorResponse:
    import anthropic

    client = anthropic.Anthropic(api_key=key)
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    system = _SYSTEM
    if lang == "hi":
        system += " IMPORTANT: Respond entirely in Hindi (Devanagari script), keeping financial terms like REIT, InvIT, SGB, NSDL, CDSL in English where natural."
    msgs = []
    for turn in history[-6:]:
        role = turn.get("role")
        content = turn.get("content", "")
        if role in ("user", "assistant") and content:
            msgs.append({"role": role, "content": content})
    msgs.append(
        {"role": "user", "content": f"My portfolio context:\n{context}\n\nMy question: {message}"}
    )
    resp = client.messages.create(
        model=model, max_tokens=700, system=system, messages=msgs
    )
    text = "".join(block.text for block in resp.content if getattr(block, "type", "") == "text")
    return AdvisorResponse(reply=text.strip(), grounded_on=facts, source="claude")


def _rule_based(message, portfolio: Portfolio, analytics: Analytics, context: str, facts: list[str], lang: str = "en") -> AdvisorResponse:
    if lang == "hi":
        return _rule_based_hi(message, portfolio, analytics, facts)
    m = message.lower()
    rm = analytics.risk_metrics
    s = portfolio.summary
    parts: list[str] = []

    if any(w in m for w in ("concentrat", "over-", "over ", "risky", "risk", "exposure")):
        if rm.concentration_flags:
            parts.append("Here's what stands out in your concentration:")
            parts.extend(f"• {f}" for f in rm.concentration_flags)
        else:
            parts.append(
                f"Your portfolio looks reasonably spread — HHI is {rm.hhi:.0f} ({rm.hhi_rating}) "
                f"and diversification score is {rm.diversification_score:.0f}/100."
            )
    elif any(w in m for w in ("diversif", "spread", "balance")):
        top_ac = analytics.allocation_by_asset_class[0]
        parts.append(
            f"You're {rm.equity_pct:.0f}% in equity/ETFs, with {top_ac.label} the largest sleeve at "
            f"{top_ac.pct:.0f}%. Diversification score: {rm.diversification_score:.0f}/100."
        )
        if rm.equity_pct >= 70:
            parts.append("Adding REITs, InvITs, or bonds would lower your overall volatility.")
    elif any(w in m for w in ("reit", "invit", "bond", "alternat", "alt ", "gold", "fixed income")):
        parts.append(
            "Alternate assets can add income and diversification beyond equities: REITs (real estate, "
            "~6–7.5% yield), InvITs (infrastructure, ~9–10%), corporate bonds/NCDs (fixed coupons), "
            "and Sovereign Gold Bonds (gold + 2.5% interest). Check the Alt-Asset section — each is "
            "tagged for suitability against your risk profile."
        )
    elif any(w in m for w in ("profit", "loss", "p&l", "pnl", "return", "gain", "how am i doing", "performance")):
        parts.append(
            f"Your portfolio is worth Rs {s.total_current_value:,.0f}, invested Rs {s.total_invested:,.0f}. "
            f"Overall P&L is Rs {s.total_pnl:,.0f} ({s.total_pnl_pct:+.1f}%)."
        )
        winners = sorted(portfolio.holdings, key=lambda h: -h.pnl_pct)[:2]
        parts.append("Top performers: " + ", ".join(f"{w.name} ({w.pnl_pct:+.0f}%)" for w in winners) + ".")
    elif any(w in m for w in ("allocat", "holding", "what do i own", "portfolio")):
        parts.append(
            "Your allocation: " + ", ".join(f"{a.label} {a.pct:.0f}%" for a in analytics.allocation_by_asset_class) + "."
        )
        parts.append("Largest holdings: " + ", ".join(f"{t.label} ({t.pct:.0f}%)" for t in analytics.top_holdings[:4]) + ".")
    else:
        parts.append(
            f"Your portfolio is Rs {s.total_current_value:,.0f} across {s.holdings_count} holdings in "
            f"{len(s.accounts)} accounts, {rm.equity_pct:.0f}% in equity, diversification {rm.diversification_score:.0f}/100. "
            "Ask me about concentration, diversification, performance, or alternate assets like REITs and bonds."
        )

    if analytics.insights:
        parts.append("\nTip: " + analytics.insights[0])
    parts.append("\n(Educational only — consult a SEBI-registered adviser for personal advice.)")
    return AdvisorResponse(reply="\n".join(parts), grounded_on=facts, source="rule-based")


def _rule_based_hi(message, portfolio: Portfolio, analytics: Analytics, facts: list[str]) -> AdvisorResponse:
    """Hindi rule-based fallback grounded on the same real numbers."""
    m = message.lower()
    rm = analytics.risk_metrics
    s = portfolio.summary
    parts: list[str] = []

    if any(w in m for w in ("concentrat", "over", "risk", "जोखिम", "एकाग्र")):
        if rm.concentration_flags:
            parts.append("आपके पोर्टफोलियो में एकाग्रता (concentration) के मुख्य बिंदु:")
            parts.extend(f"• {f}" for f in rm.concentration_flags)
        else:
            parts.append(f"आपका पोर्टफोलियो ठीक-ठाक फैला हुआ है — विविधता स्कोर {rm.diversification_score:.0f}/100 है।")
    elif any(w in m for w in ("reit", "invit", "bond", "gold", "बॉन्ड", "सोना", "वैकल्पिक")):
        parts.append(
            "वैकल्पिक निवेश (alternate assets) इक्विटी से आगे आय और विविधता देते हैं: "
            "REITs (रियल एस्टेट, ~6–7.5% yield), InvITs (इंफ्रास्ट्रक्चर, ~9–10%), "
            "corporate bonds/NCDs (निश्चित ब्याज), और Sovereign Gold Bonds (सोना + 2.5% ब्याज)। "
            "Alt-Asset सेक्शन में हर विकल्प आपकी जोखिम-प्रोफ़ाइल के अनुसार टैग किया गया है।"
        )
    elif any(w in m for w in ("profit", "loss", "return", "perform", "मुनाफ़ा", "नुकसान", "प्रदर्शन")):
        parts.append(
            f"आपके पोर्टफोलियो का मूल्य ₹{s.total_current_value:,.0f} है, निवेश ₹{s.total_invested:,.0f}। "
            f"कुल लाभ/हानि ₹{s.total_pnl:,.0f} ({s.total_pnl_pct:+.1f}%) है।"
        )
    else:
        parts.append(
            f"आपका पोर्टफोलियो ₹{s.total_current_value:,.0f} का है, {s.holdings_count} होल्डिंग्स "
            f"{len(s.accounts)} खातों में, {rm.equity_pct:.0f}% इक्विटी में, विविधता {rm.diversification_score:.0f}/100। "
            "एकाग्रता, विविधता, प्रदर्शन या वैकल्पिक निवेश के बारे में पूछें।"
        )
    parts.append("\n(केवल शैक्षिक जानकारी — व्यक्तिगत सलाह हेतु SEBI-पंजीकृत सलाहकार से परामर्श करें।)")
    return AdvisorResponse(reply="\n".join(parts), grounded_on=facts, source="rule-based")
