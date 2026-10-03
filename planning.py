"""Deterministic planning rules for Briefly: RMDs, holdings analysis, tax-loss screening, Reg BI checklist.

Everything here is plain, testable Python. The language model only explains or drafts around these results;
it never calculates them. All outputs are illustrative decision support, not tax, legal, or investment advice.
"""

from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

SAMPLE_HOLDINGS_PATH = Path(__file__).parent / "sample_holdings.csv"
REQUIRED_COLUMNS = ["client_id", "account_type", "ticker", "asset_class", "kind", "shares", "price", "cost_basis", "acquired"]

# --- RMDs -------------------------------------------------------------------------------------------------
# IRS Uniform Lifetime Table (Pub. 590-B, effective 2022). Age attained during the distribution year.
UNIFORM_LIFETIME = {
    72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4,
    82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5,
    92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4, 101: 6.0,
    102: 5.6, 103: 5.2, 104: 4.9, 105: 4.6, 106: 4.3, 107: 4.1, 108: 3.9, 109: 3.7, 110: 3.5, 111: 3.4,
    112: 3.3, 113: 3.1, 114: 3.0, 115: 2.9,
}
PRETAX_ACCOUNTS = ("traditional ira", "401(k)", "403(b)", "sep ira", "simple ira", "rollover ira")


def rmd_start_age(birth_year: int) -> int:
    """SECURE 2.0: 73 for those born 1951-1959, 75 for 1960 or later (72 for 1950 or earlier)."""
    if birth_year <= 1950:
        return 72
    return 73 if birth_year <= 1959 else 75


def rmd_status(client: dict[str, Any], pretax_balance: float | None = None, year: int | None = None) -> dict[str, Any]:
    """Return the client's RMD position for ``year`` using the Uniform Lifetime Table.

    ``pretax_balance`` should be the prior December 31 balance of all pre-tax retirement accounts. The caller
    supplies an estimate (current value) when the true year-end figure is unavailable; the result labels it.
    """
    year = year or date.today().year
    birth_year = int(client.get("birth_year") or (year - int(client.get("age", 0))))
    age = year - birth_year
    start_age = rmd_start_age(birth_year)
    first_year = birth_year + start_age
    result: dict[str, Any] = {
        "client_id": client.get("id"), "name": client.get("name"), "year": year, "age_this_year": age,
        "start_age": start_age, "first_rmd_year": first_year, "pretax_balance": pretax_balance,
        "factor": None, "amount": None, "deadline": None, "state": None, "message": "",
    }
    if year < first_year:
        result.update(state="not_yet", message=f"No RMD yet. First RMD year is {first_year} (age {start_age}), {first_year - year} year(s) away.")
        return result
    factor = UNIFORM_LIFETIME.get(min(age, 115))
    result["factor"] = factor
    if pretax_balance is not None and factor:
        result["amount"] = round(pretax_balance / factor, 2)
    if year == first_year:
        result.update(state="first_year", deadline=f"April 1, {year + 1} (or December 31, {year})")
        result["message"] = (f"First RMD year. Deadline can be delayed to April 1, {year + 1}, but then two RMDs "
                             f"are due in {year + 1}, which can push income into a higher bracket.")
    else:
        result.update(state="required", deadline=f"December 31, {year}")
        result["message"] = f"RMD required by December 31, {year}."
    return result


def pretax_balance_from_holdings(client_id: str, rows: list[dict[str, Any]]) -> float | None:
    mine = [r for r in rows if r["client_id"] == client_id and r["account_type"].lower() in PRETAX_ACCOUNTS]
    return round(sum(r["market_value"] for r in mine), 2) if mine else None


# --- Holdings ---------------------------------------------------------------------------------------------
TARGETS = {
    "Aggressive": {"Equity": 80.0, "Fixed Income": 15.0, "Cash": 5.0},
    "Moderate": {"Equity": 60.0, "Fixed Income": 35.0, "Cash": 5.0},
    "Conservative": {"Equity": 30.0, "Fixed Income": 60.0, "Cash": 10.0},
}
DRIFT_THRESHOLD_PTS = 5.0
CONCENTRATION_LIMIT_PCT = 10.0
WASH_WINDOW_DAYS = 30
SUBSTITUTES = {
    "VTI": "a different broad US equity fund tracking another index", "VOO": "a large-cap fund tracking a different index",
    "QQQ": "a growth-oriented fund with a different index", "VXUS": "another international equity fund",
    "MUB": "a different national municipal fund", "BND": "a different intermediate bond fund",
    "AAPL": "a technology sector fund", "MSFT": "a technology sector fund", "NVDA": "a semiconductor or technology fund",
    "AMZN": "a consumer discretionary sector fund", "TSLA": "a consumer discretionary sector fund",
    "XOM": "an energy sector fund", "JPM": "a financial sector fund",
}


def parse_holdings(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse lot-level holdings CSV text. Returns (rows, errors); invalid rows are skipped with a message."""
    reader = csv.DictReader(io.StringIO(text.strip()))
    fields = [f.strip().lower() for f in (reader.fieldnames or [])]
    missing = [c for c in REQUIRED_COLUMNS if c not in fields]
    if missing:
        return [], [f"Missing required column(s): {', '.join(missing)}"]
    rows, errors = [], []
    for number, raw in enumerate(reader, start=2):
        row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
        try:
            shares, price, basis = float(row["shares"]), float(row["price"]), float(row["cost_basis"])
            acquired = datetime.strptime(row["acquired"], "%Y-%m-%d").date()
            if shares < 0 or price < 0 or basis < 0:
                raise ValueError("negative number")
            asset_class = row["asset_class"].title().replace("Fixed income", "Fixed Income")
            rows.append({
                "client_id": row["client_id"], "account_type": row["account_type"], "ticker": row["ticker"].upper(),
                "description": row.get("description", ""), "asset_class": asset_class, "kind": row["kind"].title(),
                "shares": shares, "price": price, "market_value": round(shares * price, 2), "cost_basis": basis,
                "acquired": acquired,
            })
        except (ValueError, KeyError) as exc:
            errors.append(f"Row {number}: {exc}")
    return rows, errors


def load_sample_holdings() -> list[dict[str, Any]]:
    rows, _ = parse_holdings(SAMPLE_HOLDINGS_PATH.read_text(encoding="utf-8"))
    return rows


def harvest_candidates(lots: list[dict[str, Any]], today: date | None = None, min_loss: float = 500.0) -> list[dict[str, Any]]:
    """Taxable lots with unrealized losses of at least ``min_loss``, flagged for wash-sale exposure."""
    today = today or date.today()
    candidates = []
    for lot in lots:
        if lot["account_type"].lower() != "taxable":
            continue
        gain = lot["market_value"] - lot["cost_basis"]
        if gain > -min_loss:
            continue
        held_days = (today - lot["acquired"]).days
        recent_buys = [o for o in lots if o is not lot and o["ticker"] == lot["ticker"] and 0 <= (today - o["acquired"]).days <= WASH_WINDOW_DAYS]
        candidates.append({
            "ticker": lot["ticker"], "acquired": lot["acquired"], "shares": lot["shares"],
            "market_value": lot["market_value"], "cost_basis": lot["cost_basis"], "loss": round(gain, 2),
            "term": "Long-term" if held_days > 365 else "Short-term",
            "wash_sale_risk": bool(recent_buys),
            "wash_note": (f"Another {lot['ticker']} lot was bought within {WASH_WINDOW_DAYS} days (any account)." if recent_buys else ""),
            "substitute_idea": SUBSTITUTES.get(lot["ticker"], "a similar but not substantially identical holding"),
        })
    return sorted(candidates, key=lambda c: c["loss"])


def analyze_holdings(client: dict[str, Any], rows: list[dict[str, Any]], today: date | None = None) -> dict[str, Any]:
    """Allocation vs. model target, concentration, rebalancing dollars, and tax-loss candidates for one client."""
    lots = [r for r in rows if r["client_id"] == client.get("id")]
    if not lots:
        return {"available": False}
    total = sum(r["market_value"] for r in lots)
    targets = TARGETS.get(client.get("risk_profile", "Moderate"), TARGETS["Moderate"])
    by_class: dict[str, float] = {}
    for r in lots:
        by_class[r["asset_class"]] = by_class.get(r["asset_class"], 0.0) + r["market_value"]
    allocation = []
    for klass in ("Equity", "Fixed Income", "Cash"):
        actual = by_class.get(klass, 0.0) / total * 100
        target = targets[klass]
        allocation.append({
            "asset_class": klass, "actual_pct": round(actual, 1), "target_pct": target,
            "drift_pts": round(actual - target, 1), "dollars_to_target": round((target - actual) / 100 * total, 0),
            "needs_review": abs(actual - target) >= DRIFT_THRESHOLD_PTS,
        })
    by_ticker: dict[str, dict[str, Any]] = {}
    for r in lots:
        entry = by_ticker.setdefault(r["ticker"], {"ticker": r["ticker"], "kind": r["kind"], "value": 0.0})
        entry["value"] += r["market_value"]
    concentration = sorted(
        [{"ticker": t["ticker"], "pct": round(t["value"] / total * 100, 1), "value": round(t["value"], 0)}
         for t in by_ticker.values() if t["kind"] == "Stock" and t["value"] / total * 100 > CONCENTRATION_LIMIT_PCT],
        key=lambda t: -t["pct"])
    by_account: dict[str, float] = {}
    for r in lots:
        by_account[r["account_type"]] = by_account.get(r["account_type"], 0.0) + r["market_value"]
    harvest = harvest_candidates(lots, today)
    unrealized = sum(r["market_value"] - r["cost_basis"] for r in lots)
    return {
        "available": True, "total_value": round(total, 2), "allocation": allocation, "concentration": concentration,
        "by_account": {k: round(v, 2) for k, v in by_account.items()}, "harvest": harvest,
        "harvestable_loss": round(sum(c["loss"] for c in harvest), 2), "unrealized_gain_loss": round(unrealized, 2),
        "largest_position_pct": round(max(t["value"] for t in by_ticker.values()) / total * 100, 1),
    }


# --- Reg BI documentation screen -------------------------------------------------------------------------
CHECKLIST = [
    ("Client goals / objectives", ["goal", "objective", "retire", "save for", "fund "]),
    ("Risk tolerance discussed", ["risk tolerance", "risk", "volatility", "downturn", "comfortable with"]),
    ("Time horizon", ["horizon", "years", "timeline", "retire in", "by age"]),
    ("Liquidity / income needs", ["liquidity", "cash need", "emergency", "withdraw", "income need", "distribution"]),
    ("Tax situation", ["tax", "bracket", "capital gain", "roth", "rmd"]),
    ("Costs and fees disclosed", ["fee", "cost", "expense ratio", "commission", "advisory fee"]),
    ("Alternatives considered", ["alternative", "instead", "compare", "other option", "versus", "rather than"]),
    ("Conflicts / compensation disclosed", ["conflict", "compensation", "incentive", "proprietary"]),
    ("Client agreement / consent", ["agree", "approve", "consent", "confirmed", "go ahead", "decided"]),
    ("Follow-up scheduled", ["follow up", "follow-up", "next meeting", "schedule", "call back", "send you"]),
]


def reg_bi_checklist(transcript: str) -> list[dict[str, Any]]:
    """Keyword screen of a meeting transcript against documentation elements advisors typically need to record.

    This is a documentation prompt for the advisor, not a determination of Reg BI compliance.
    """
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", transcript) if s.strip()]
    results = []
    for item, keywords in CHECKLIST:
        evidence = next((s for s in sentences if any(k in s.lower() for k in keywords)), "")
        results.append({"item": item, "found": bool(evidence), "evidence": evidence[:200]})
    return results
