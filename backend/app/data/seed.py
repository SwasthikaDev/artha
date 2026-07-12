"""Seed data — simulates the Account Aggregator / NSDL-CDSL unified feed.

Two investor personas with holdings deliberately fragmented across multiple brokers
and both depositories, so the aggregation + analytics story is visible. Prices are
realistic INR values; the market-data adapter overlays live prices when available.
"""
from app.models.schemas import AssetClass, Depository, Holding

# --------------------------------------------------------------------------- #
# Investor personas
# --------------------------------------------------------------------------- #
INVESTORS = {
    "INV001": {
        "name": "Aarav Sharma",
        "tagline": "Equity-heavy retail investor, 3 broker accounts",
    },
    "INV002": {
        "name": "Priya Nair",
        "tagline": "Balanced investor exploring alternate assets",
    },
}

DEFAULT_INVESTOR = "INV001"


# --------------------------------------------------------------------------- #
# Holdings — deliberately fragmented across brokers + NSDL/CDSL
# --------------------------------------------------------------------------- #
# fields: symbol, name, asset_class, sector, broker, depository, qty, avg_cost, ltp
_RAW: dict[str, list[tuple]] = {
    "INV001": [
        # Zerodha (CDSL) — concentrated equity book
        ("RELIANCE", "Reliance Industries", AssetClass.EQUITY, "Energy", "Zerodha", Depository.CDSL, 40, 2450, 2980),
        ("TCS", "Tata Consultancy Services", AssetClass.EQUITY, "IT", "Zerodha", Depository.CDSL, 25, 3600, 4120),
        ("INFY", "Infosys", AssetClass.EQUITY, "IT", "Zerodha", Depository.CDSL, 60, 1450, 1890),
        ("HDFCBANK", "HDFC Bank", AssetClass.EQUITY, "Financials", "Zerodha", Depository.CDSL, 45, 1520, 1685),
        ("WIPRO", "Wipro", AssetClass.EQUITY, "IT", "Zerodha", Depository.CDSL, 100, 410, 545),
        # Groww (CDSL) — mutual funds + a couple of stocks
        ("PPFAS", "Parag Parikh Flexi Cap Fund", AssetClass.MUTUAL_FUND, "Diversified", "Groww", Depository.CDSL, 850, 62, 78),
        ("UTINIFTY", "UTI Nifty 50 Index Fund", AssetClass.MUTUAL_FUND, "Diversified", "Groww", Depository.CDSL, 1200, 120, 148),
        ("HCLTECH", "HCL Technologies", AssetClass.EQUITY, "IT", "Groww", Depository.CDSL, 40, 1100, 1620),
        ("TATAMOTORS", "Tata Motors", AssetClass.EQUITY, "Auto", "Groww", Depository.CDSL, 80, 620, 985),
        # ICICI Direct (NSDL) — older holdings
        ("ITC", "ITC", AssetClass.EQUITY, "FMCG", "ICICI Direct", Depository.NSDL, 200, 320, 465),
        ("SBIN", "State Bank of India", AssetClass.EQUITY, "Financials", "ICICI Direct", Depository.NSDL, 90, 520, 820),
        ("GOLDBEES", "Nippon India Gold ETF", AssetClass.ETF, "Commodity", "ICICI Direct", Depository.NSDL, 150, 52, 68),
    ],
    "INV002": [
        # HDFC Securities (NSDL) — balanced core
        ("HDFCBANK", "HDFC Bank", AssetClass.EQUITY, "Financials", "HDFC Securities", Depository.NSDL, 30, 1480, 1685),
        ("NIFTYBEES", "Nippon India Nifty 50 ETF", AssetClass.ETF, "Diversified", "HDFC Securities", Depository.NSDL, 200, 210, 258),
        ("BHARTIARTL", "Bharti Airtel", AssetClass.EQUITY, "Telecom", "HDFC Securities", Depository.NSDL, 50, 950, 1560),
        # Kotak (NSDL) — fixed income tilt
        ("SGB2032", "Sovereign Gold Bond 2032", AssetClass.BOND, "Sovereign", "Kotak Securities", Depository.NSDL, 20, 5100, 6250),
        ("EMBASSY", "Embassy Office Parks REIT", AssetClass.REIT, "Real Estate", "Kotak Securities", Depository.NSDL, 60, 350, 385),
        # Groww (CDSL) — funds
        ("HDFCBAL", "HDFC Balanced Advantage Fund", AssetClass.MUTUAL_FUND, "Hybrid", "Groww", Depository.CDSL, 900, 32, 41),
    ],
}


def get_holdings(investor_id: str) -> list[Holding]:
    rows = _RAW.get(investor_id, _RAW[DEFAULT_INVESTOR])
    holdings: list[Holding] = []
    for sym, name, ac, sector, broker, dep, qty, avg, ltp in rows:
        holdings.append(
            Holding(
                symbol=sym, name=name, asset_class=ac, sector=sector,
                broker=broker, depository=dep, quantity=qty, avg_cost=avg, ltp=ltp,
            )
        )
    return holdings
