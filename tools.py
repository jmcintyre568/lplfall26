"""Local action tools exposed to the Briefly Bedrock orchestrator."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def get_portfolio_drift(client_json: dict[str, Any]) -> str:
    """Estimate allocation drift from a client's risk-profile target.

    Args:
        client_json: Client dictionary. May include ``holdings`` as a mapping
            of asset-class names to portfolio percentages (0-100). For this
            synthetic MVP, profiles have illustrative equity targets of 80%
            Aggressive, 60% Moderate, and 30% Conservative. If holdings are
            absent, a deterministic illustrative allocation is used.

    Returns:
        A readable drift summary, with an alert when the absolute equity
        allocation difference exceeds five percentage points. This is an
        educational estimate, not investment advice.
    """
    profile = str(client_json.get("risk_profile", "Moderate"))
    targets = {"Aggressive": 80.0, "Moderate": 60.0, "Conservative": 30.0}
    target = targets.get(profile, targets["Moderate"])
    holdings = client_json.get("holdings")
    if isinstance(holdings, dict) and holdings:
        equity = sum(float(value) for key, value in holdings.items() if "equity" in key.lower() or "stock" in key.lower())
        denominator = sum(float(value) for value in holdings.values())
        actual = equity / denominator * 100 if denominator > 0 else target
    else:
        # Synthetic estimate keeps the demo usable without fabricating detailed positions.
        actual = {"Aggressive": 87.0, "Moderate": 56.0, "Conservative": 36.0}.get(profile, target)
    drift = actual - target
    result = f"Illustrative equity allocation is {actual:.1f}% vs. a {target:.1f}% {profile.lower()} profile target (drift {drift:+.1f} percentage points)."
    if abs(drift) > 5.0:
        return f"⚠️ Portfolio drift alert: {result} Advisor review recommended."
    return f"Within the 5 percentage-point review threshold: {result}"


def query_crm_notes(client_id: str, query: str, clients_data: list[dict[str, Any]]) -> list[str]:
    """Search one client's synthetic CRM meeting notes using query keywords.

    Args:
        client_id: Stable synthetic client identifier such as ``C-1001``.
        query: Natural-language query; terms are matched case-insensitively.
        clients_data: Complete list of client dictionaries.

    Returns:
        Matching note strings, or a clear message when no match/client exists.
    """
    client = next((item for item in clients_data if item.get("id") == client_id), None)
    if client is None:
        return [f"No synthetic client found for ID {client_id}."]
    terms = [word.lower().strip(".,?!:;") for word in query.split() if len(word) > 2]
    notes = client.get("meeting_notes", [])
    matches = [note for note in notes if any(term in note.lower() for term in terms)] if terms else list(notes)
    return matches or ["No matching meeting notes found for that query."]


def draft_compliance_log(action: str, details: str) -> str:
    """Create a timestamped proposed-action record for advisor review.

    Args:
        action: Proposed action label, for example ``send_email`` or
            ``update_crm``. This function records intent only and never acts.
        details: Human-readable context for the proposed action.

    Returns:
        A JSON string with UTC timestamp, action, details, and pending-review
        status. An advisor must approve outside this function before execution.
    """
    return json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "details": details,
        "status": "pending_advisor_review",
    }, ensure_ascii=False)


def query_book_metrics(query_type: str, clients_data: list[dict[str, Any]]) -> Any:
    """Answer simple aggregate questions over the synthetic client book.

    Args:
        query_type: One of ``urgent_tasks``, ``pending_tasks``,
            ``client_count``, or ``assets_under_management``.
        clients_data: Complete list of client dictionaries.

    Returns:
        Matching client/task summaries, a count, or aggregate portfolio value.
    """
    normalized = query_type.lower().replace(" ", "_")
    if normalized in {"urgent_tasks", "pending_tasks"}:
        desired = "urgent" if normalized == "urgent_tasks" else "pending"
        return [{"client_id": client["id"], "name": client["name"], "task": task}
                for client in clients_data for task in client.get("pending_tasks", [])
                if task.get("status") == desired]
    if normalized == "client_count":
        return len(clients_data)
    if normalized == "assets_under_management":
        return round(sum(float(client.get("portfolio_value", 0)) for client in clients_data), 2)
    return {"error": f"Unsupported query_type: {query_type}"}
