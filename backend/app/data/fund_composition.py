"""Fund look-through data — the underlying holdings of each mutual fund / ETF.

Powers the Portfolio X-Ray: decomposing funds into their underlying stocks reveals
the investor's TRUE concentration, which is hidden when funds are treated as opaque
single line-items. Weights are indicative top-holding compositions (%). Equity weights
need not sum to 100 — the remainder is treated as "Other / smaller holdings".
"""
from __future__ import annotations

# fund_symbol -> list of (underlying_symbol, name, sector, weight_pct_of_fund)
FUND_COMPOSITION: dict[str, list[tuple[str, str, str, float]]] = {
    # UTI Nifty 50 Index Fund — tracks the Nifty 50
    "UTINIFTY": [
        ("HDFCBANK", "HDFC Bank", "Financials", 11.3),
        ("RELIANCE", "Reliance Industries", "Energy", 9.8),
        ("ICICIBANK", "ICICI Bank", "Financials", 7.9),
        ("INFY", "Infosys", "IT", 6.1),
        ("TCS", "Tata Consultancy Services", "IT", 4.3),
        ("ITC", "ITC", "FMCG", 4.0),
        ("BHARTIARTL", "Bharti Airtel", "Telecom", 3.4),
        ("LT", "Larsen & Toubro", "Infrastructure", 3.3),
        ("SBIN", "State Bank of India", "Financials", 2.9),
        ("HCLTECH", "HCL Technologies", "IT", 1.6),
    ],
    # Nippon India Nifty 50 ETF — also tracks the Nifty 50
    "NIFTYBEES": [
        ("HDFCBANK", "HDFC Bank", "Financials", 11.3),
        ("RELIANCE", "Reliance Industries", "Energy", 9.8),
        ("ICICIBANK", "ICICI Bank", "Financials", 7.9),
        ("INFY", "Infosys", "IT", 6.1),
        ("TCS", "Tata Consultancy Services", "IT", 4.3),
        ("ITC", "ITC", "FMCG", 4.0),
        ("BHARTIARTL", "Bharti Airtel", "Telecom", 3.4),
        ("LT", "Larsen & Toubro", "Infrastructure", 3.3),
        ("SBIN", "State Bank of India", "Financials", 2.9),
    ],
    # Parag Parikh Flexi Cap — domestic + foreign equity tilt
    "PPFAS": [
        ("HDFCBANK", "HDFC Bank", "Financials", 7.6),
        ("BAJAJHLDNG", "Bajaj Holdings", "Financials", 6.9),
        ("ITC", "ITC", "FMCG", 5.8),
        ("POWERGRID", "Power Grid", "Utilities", 5.1),
        ("COALINDIA", "Coal India", "Energy", 4.7),
        ("ICICIBANK", "ICICI Bank", "Financials", 4.4),
        ("INFY", "Infosys", "IT", 3.9),
        ("HCLTECH", "HCL Technologies", "IT", 2.8),
        ("FOREIGN", "Foreign Equity (Alphabet, Meta, Amazon)", "Foreign Equity", 14.2),
    ],
    # HDFC Balanced Advantage — hybrid (equity + debt)
    "HDFCBAL": [
        ("ICICIBANK", "ICICI Bank", "Financials", 6.2),
        ("HDFCBANK", "HDFC Bank", "Financials", 5.4),
        ("RELIANCE", "Reliance Industries", "Energy", 4.8),
        ("INFY", "Infosys", "IT", 3.6),
        ("SBIN", "State Bank of India", "Financials", 3.1),
        ("NTPC", "NTPC", "Utilities", 2.7),
        ("DEBT", "Debt & Money Market", "Fixed Income", 34.0),
    ],
    # Nippon India Gold ETF — underlying is physical gold
    "GOLDBEES": [
        ("GOLD", "Physical Gold", "Commodity", 100.0),
    ],
}


def get_composition(symbol: str) -> list[tuple[str, str, str, float]] | None:
    return FUND_COMPOSITION.get(symbol)


def is_fund(symbol: str) -> bool:
    return symbol in FUND_COMPOSITION
