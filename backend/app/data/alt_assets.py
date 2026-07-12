"""Curated catalog of alternate investment instruments (REITs, InvITs, corporate bonds,
sovereign gold bonds) with education content — the awareness half of PS3.

Data is illustrative/representative for the prototype; figures are indicative.
"""
from app.models.schemas import AltAsset, AssetClass

ALT_ASSETS: list[AltAsset] = [
    AltAsset(
        id="embassy-reit",
        name="Embassy Office Parks REIT",
        asset_class=AssetClass.REIT,
        category="Commercial Office REIT",
        ticker="EMBASSY",
        yield_pct=6.8,
        rating="AAA",
        risk_level="Medium",
        min_investment=385.0,
        liquidity="High (exchange-traded)",
        tenure="Perpetual",
        summary="India's first listed REIT, owning premium commercial office parks leased to blue-chip tenants.",
        highlights=[
            "Regular quarterly distributions from rental income",
            "Exchange-traded — buy/sell like a stock",
            "Exposure to commercial real estate without buying property",
        ],
        education=(
            "A REIT (Real Estate Investment Trust) pools money from many investors to own "
            "income-producing real estate. SEBI requires REITs to distribute at least 90% of "
            "net distributable cash flow to unitholders, which is why they offer steady yields. "
            "You get real-estate exposure with stock-like liquidity and a low entry ticket."
        ),
    ),
    AltAsset(
        id="mindspace-reit",
        name="Mindspace Business Parks REIT",
        asset_class=AssetClass.REIT,
        category="Commercial Office REIT",
        ticker="MINDSPACE",
        yield_pct=7.1,
        rating="AAA",
        risk_level="Medium",
        min_investment=360.0,
        liquidity="High (exchange-traded)",
        tenure="Perpetual",
        summary="REIT with a portfolio of business parks across Mumbai, Hyderabad, Pune, and Chennai.",
        highlights=[
            "Geographically diversified office portfolio",
            "Tax-efficient distributions",
            "Institutional-grade assets accessible to retail",
        ],
        education=(
            "REIT distributions can be a mix of dividend, interest, and return of capital, each "
            "taxed differently. REITs suit investors seeking regular income and diversification "
            "beyond equities, with moderate risk tied to occupancy and rental trends."
        ),
    ),
    AltAsset(
        id="powergrid-invit",
        name="PowerGrid Infrastructure InvIT",
        asset_class=AssetClass.INVIT,
        category="Power Transmission InvIT",
        ticker="PGINVIT",
        yield_pct=9.2,
        rating="AAA",
        risk_level="Medium",
        min_investment=98.0,
        liquidity="Medium (exchange-traded)",
        tenure="Perpetual",
        summary="InvIT holding operational inter-state power transmission assets with long-term contracted cash flows.",
        highlights=[
            "High yield from regulated, contracted infrastructure cash flows",
            "Backed by PowerGrid, a Maharatna PSU",
            "Predictable, availability-based revenue",
        ],
        education=(
            "An InvIT (Infrastructure Investment Trust) owns operating infrastructure — power lines, "
            "roads, gas pipelines — that generate stable cash flows, and passes income to unitholders. "
            "Like REITs, SEBI mandates high distribution payouts. InvITs typically offer higher yields "
            "than REITs but carry sector-specific and interest-rate risks."
        ),
    ),
    AltAsset(
        id="irb-invit",
        name="IRB InvIT Fund",
        asset_class=AssetClass.INVIT,
        category="Roads / Highways InvIT",
        ticker="IRBINVIT",
        yield_pct=10.5,
        rating="AA+",
        risk_level="High",
        min_investment=55.0,
        liquidity="Medium (exchange-traded)",
        tenure="Finite (toll concession life)",
        summary="InvIT holding toll-road concessions; income driven by traffic and toll collections.",
        highlights=[
            "Among the highest yields in the listed InvIT space",
            "Cash flows linked to highway traffic",
            "Finite-life assets — yield includes return of capital",
        ],
        education=(
            "Toll-road InvITs earn from traffic-linked toll revenue, so cash flows are more variable "
            "than availability-based assets. Because concessions have a finite life, part of the high "
            "distribution is effectively return of your capital — compare the yield to the asset's "
            "remaining life before assuming it is pure income."
        ),
    ),
    AltAsset(
        id="ncd-lt-2029",
        name="L&T Finance NCD 2029",
        asset_class=AssetClass.BOND,
        category="Corporate Bond (NCD)",
        ticker="LTF29",
        yield_pct=8.4,
        rating="AAA",
        risk_level="Low",
        min_investment=1000.0,
        liquidity="Low-Medium (thin secondary market)",
        tenure="~5 years",
        summary="AAA-rated non-convertible debenture offering fixed coupons over a ~5-year tenure.",
        highlights=[
            "Fixed, predictable coupon income",
            "AAA credit rating — low default risk",
            "Higher yield than a comparable bank FD",
        ],
        education=(
            "A corporate bond / NCD is a loan you make to a company in return for fixed coupons and "
            "principal at maturity. Credit rating (AAA is safest) signals default risk; higher yields "
            "usually mean higher risk. Bond prices fall when interest rates rise. NCDs suit investors "
            "wanting steady income and lower volatility than equity."
        ),
    ),
    AltAsset(
        id="ncd-shriram-2028",
        name="Shriram Finance NCD 2028",
        asset_class=AssetClass.BOND,
        category="Corporate Bond (NCD)",
        ticker="SHRIRAM28",
        yield_pct=9.6,
        rating="AA+",
        risk_level="Medium",
        min_investment=1000.0,
        liquidity="Low (hold-to-maturity)",
        tenure="~4 years",
        summary="AA+ rated NCD from an NBFC offering an elevated coupon for the additional credit risk.",
        highlights=[
            "Attractive coupon vs AAA peers",
            "Diversifies fixed-income exposure",
            "Monthly / annual interest options",
        ],
        education=(
            "Stepping down from AAA to AA+ boosts yield but adds credit risk. NBFC bonds are sensitive "
            "to funding conditions and asset quality. A prudent approach is to size lower-rated bonds "
            "smaller and hold to maturity to avoid liquidity and price risk."
        ),
    ),
    AltAsset(
        id="sgb-2032",
        name="Sovereign Gold Bond 2032",
        asset_class=AssetClass.BOND,
        category="Sovereign Gold Bond",
        ticker="SGB2032",
        yield_pct=2.5,
        rating="Sovereign",
        risk_level="Low",
        min_investment=6250.0,
        liquidity="Medium (exchange-traded, 8-yr maturity)",
        tenure="8 years",
        summary="Government gold bond paying 2.5% interest plus gold-price-linked redemption; sovereign-backed.",
        highlights=[
            "2.5% annual interest ON TOP of gold price appreciation",
            "No making charges or storage risk vs physical gold",
            "Capital gains tax-free if held to maturity",
        ],
        education=(
            "Sovereign Gold Bonds are issued by RBI on behalf of the Government of India. They track "
            "gold prices and additionally pay 2.5% annual interest — an advantage over physical gold "
            "or gold ETFs. They suit investors seeking gold exposure as an inflation hedge and "
            "portfolio diversifier."
        ),
    ),
    AltAsset(
        id="nexus-reit",
        name="Nexus Select Trust REIT",
        asset_class=AssetClass.REIT,
        category="Retail / Mall REIT",
        ticker="NXST",
        yield_pct=7.5,
        rating="AAA",
        risk_level="Medium",
        min_investment=135.0,
        liquidity="High (exchange-traded)",
        tenure="Perpetual",
        summary="India's first retail-mall REIT, owning consumption-linked shopping centres across major cities.",
        highlights=[
            "Exposure to India's consumption growth",
            "Rental income plus revenue-share upside from tenants",
            "Low entry ticket",
        ],
        education=(
            "Retail REITs earn from mall rentals, often with a revenue-share component tied to tenant "
            "sales — so they participate in consumption growth. Footfall and discretionary spending "
            "drive performance, adding a mild cyclical tilt compared with office REITs."
        ),
    ),
]


def get_catalog() -> list[AltAsset]:
    return ALT_ASSETS


def get_asset(asset_id: str) -> AltAsset | None:
    return next((a for a in ALT_ASSETS if a.id == asset_id), None)
