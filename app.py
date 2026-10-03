"""Briefly: synthetic wealth-advisor meeting prep demo."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from agent import BrieflyOrchestrator

st.set_page_config(page_title="Briefly | Advisor Copilot", page_icon="✦", layout="wide")

ROOT = Path(__file__).parent
with (ROOT / "clients.json").open(encoding="utf-8") as file:
    CLIENTS = json.load(file)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp { background: #f5f7fa; color: #17253b; font-family: 'DM Sans', sans-serif; }
[data-testid="stSidebar"] { background: #101d32; }
[data-testid="stSidebar"] * { color: #edf3fb; }
[data-testid="stSidebar"] input { color: #17253b !important; }
h1,h2,h3 { font-family: 'Manrope', sans-serif; letter-spacing: -.035em; }
.eyebrow { color:#71819a; text-transform:uppercase; letter-spacing:.13em; font-size:.72rem; font-weight:700; }
.hero { display:flex; justify-content:space-between; align-items:center; padding: 1.1rem 0 1.5rem; }
.hero h1 { margin:0; color:#15253c; font-size:2.2rem; }
.hero p { color:#78869a; margin:.35rem 0 0; }
.tag { padding:.45rem .8rem; border:1px solid #dde5ef; border-radius:99px; color:#566a85; background:white; font-size:.8rem; }
.task-track { display:flex; gap:14px; overflow-x:auto; padding: 12px 2px 20px; }
.task-card { min-width:220px; flex:1; background:white; border:1px solid #e3e9f1; border-top:3px solid #8da0ba; border-radius:12px; padding:14px 16px; box-shadow:0 4px 16px #1e34500a; }
.task-card.urgent { border-top-color:#e35555; }
.task-date { color:#8492a5; font-size:.76rem; font-weight:700; }
.task-desc { color:#263851; font-weight:600; margin:8px 0 12px; line-height:1.4; }
.task-status { color:#60738e; font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; }
.task-card.urgent .task-status { color:#c64040; }
[data-testid="stMetric"] { background:white; border:1px solid #e4eaf1; border-radius:12px; padding:10px 14px; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color:#5b6b82 !important; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * { color:#17253b !important; }
.section-card { background:white; padding:20px 22px; border-radius:16px; border:1px solid #e4eaf1; }
.hero { flex-wrap:wrap; gap:.6rem; }
.task-track { flex-wrap:wrap; }
@media (max-width: 1000px) {
  /* Stack the main/chat layout and wrap columns when the window gets narrow */
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; row-gap: 1rem; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
  /* Keep nested column groups (metrics, notes) in a compact 2-up grid */
  [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  [data-testid="column"] [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: calc(50% - 1rem) !important; flex: 1 1 calc(50% - 1rem) !important; }
  .hero h1 { font-size: 1.7rem; }
}
@media (max-width: 560px) {
  [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  [data-testid="column"] [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
  .task-card { min-width: 100%; }
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "pending_proposal" not in st.session_state:
    st.session_state.pending_proposal = None
if "meeting_brief" not in st.session_state:
    st.session_state.meeting_brief = None
if "workday_brief" not in st.session_state:
    st.session_state.workday_brief = None
if "aws_status" not in st.session_state:
    st.session_state.aws_status = None
if "orchestrator" not in st.session_state or not hasattr(st.session_state.orchestrator, "model_id"):
    try:
        st.session_state.orchestrator = BrieflyOrchestrator()
        st.session_state.orchestrator_error = None
    except Exception as exc:  # Client construction can fail before a request is sent.
        st.session_state.orchestrator = None
        st.session_state.orchestrator_error = str(exc)


if st.session_state.orchestrator is not None:
    _orch = st.session_state.orchestrator
    st.session_state.setdefault("bedrock_model_id", _orch.model_id)
    st.session_state.setdefault("bedrock_guardrail_id", _orch.guardrail_id or "")
    st.session_state.setdefault("bedrock_guardrail_version", _orch.guardrail_version or "DRAFT")
    st.session_state.setdefault("bedrock_kb_id", _orch.knowledge_base_id or "")
    _orch.model_id = st.session_state.bedrock_model_id.strip()
    _orch.update_guardrail(st.session_state.bedrock_guardrail_id, st.session_state.bedrock_guardrail_version)
    _orch.update_knowledge_base(st.session_state.bedrock_kb_id)

main_col, side_col = st.columns([2.2, 1], gap="large")

with side_col:
    st.markdown("<div style='padding:4px 0 8px'><div style='font-size:1.4rem;font-weight:800;font-family:Manrope'>✦ LPL Assistant</div></div>", unsafe_allow_html=True)
    with st.container(height=220, border=True):
        if not st.session_state.messages:
            st.caption("No messages yet. Ask LPL Assistant below.")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    if st.session_state.pending_proposal:
        proposal = st.session_state.pending_proposal
        with st.expander("⚠️ Pending Advisor Review", expanded=True):
            st.markdown(f"**Proposed action:** {proposal.get('action', 'Review action')}  \n{proposal.get('details', '')}")
            st.caption(f"Drafted {proposal.get('timestamp', '')} · No external action has been taken.")
            approve, reject = st.columns(2)
            if approve.button("Approve & Log", type="primary", use_container_width=True, key="approve_proposal"):
                st.session_state.audit_log.append({**proposal, "decision": "approved", "reviewed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()})
                st.session_state.pending_proposal = None
                st.toast("Action approved and recorded in the local audit log.", icon="✅")
                st.rerun()
            if reject.button("Reject", use_container_width=True, key="reject_proposal"):
                st.session_state.audit_log.append({**proposal, "decision": "rejected", "reviewed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()})
                st.session_state.pending_proposal = None
                st.info("Proposal rejected and recorded.")
                st.rerun()
    prompt = st.chat_input("Ask LPL Assistant…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        if st.session_state.orchestrator is None:
            response_text = f"Bedrock client setup failed: {st.session_state.orchestrator_error}. Check your AWS configuration and restart the app."
        else:
            selected = st.session_state.get("selected_client", CLIENTS[0]["id"])
            current_client = next(client for client in CLIENTS if client["id"] == selected)
            response_text = st.session_state.orchestrator.route_query(prompt, current_client, CLIENTS)
        if response_text.startswith("BRIEFLY_PROPOSAL:"):
            payload = json.loads(response_text.removeprefix("BRIEFLY_PROPOSAL:"))
            st.session_state.pending_proposal = payload["proposal"]
            response_text = payload.get("summary") or "A proposed action is ready for your review."
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()
    with st.expander("⚙️ AWS & Bedrock settings", expanded=False):
        orchestrator = st.session_state.orchestrator
        if orchestrator is None:
            st.warning(f"AWS client setup issue: {st.session_state.orchestrator_error}")
        else:
            st.markdown("**AWS connection**")
            if st.button("Check AWS connection", use_container_width=True, key="check_aws"):
                with st.spinner("Checking AWS credentials…"):
                    st.session_state.aws_status = orchestrator.check_aws_access()
            if st.session_state.aws_status:
                connected, status_text = st.session_state.aws_status
                (st.success if connected else st.warning)(status_text)
            st.markdown("**Bedrock**")
            st.text_input(
                "Model / inference profile ID",
                key="bedrock_model_id",
                placeholder="Paste an active ID from the Bedrock model page",
                help="Use a model or inference profile that supports Converse and tool use in your chosen region.",
            )
            st.text_input("Guardrail ID (optional)", key="bedrock_guardrail_id", placeholder="e.g. g-1234567890")
            st.text_input("Guardrail version (optional)", key="bedrock_guardrail_version", placeholder="e.g. DRAFT or 1")
            st.text_input(
                "Knowledge Base ID (optional)",
                key="bedrock_kb_id",
                placeholder="e.g. kb-1234567890",
                help="Enables the search_advisor_library tool for policy lookups.",
            )
            st.caption("Guardrail: " + ("active" if orchestrator.guardrail_config else "not configured"))
            st.caption("Knowledge Base: " + ("connected" if orchestrator.knowledge_base_id else "not configured"))

with main_col:
    st.markdown("<div class='hero'><div><div class='eyebrow'>Advisor workspace · Meeting preparation</div><h1>Good morning, Advisor</h1></div><div class='tag'>● &nbsp; Demo environment · Synthetic data</div></div>", unsafe_allow_html=True)
    client_options = {f"{client['name']}  ·  {client['id']}": client for client in CLIENTS}
    selected_label = st.selectbox("Select a client", list(client_options), label_visibility="collapsed", key="client_picker")
    client = client_options[selected_label]
    st.session_state.selected_client = client["id"]

    st.markdown(f"<div style='margin:18px 0 10px'><span class='eyebrow'>Client snapshot</span><h2 style='margin:4px 0 0'>{client['name']}</h2></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio value", f"${client['portfolio_value']:,.0f}")
    c2.metric("Risk profile", client["risk_profile"])
    c3.metric("Age", str(client["age"]))
    c4.metric("Open tasks", str(len(client["pending_tasks"])), delta=f"{sum(t['status'] == 'urgent' for t in client['pending_tasks'])} urgent", delta_color="inverse")

    st.markdown("<div class='eyebrow' style='margin:14px 0 4px'>Agentic operations</div>", unsafe_allow_html=True)
    act1, act2, _act_gap = st.columns([1, 1, 2])
    run_queue = act1.button("✦ Priority queue", key="generate_workday_brief", use_container_width=True)
    run_brief = act2.button("✦ Meeting brief", type="primary", key="generate_meeting_brief", use_container_width=True)
    if run_queue:
        if st.session_state.orchestrator is None:
            st.session_state.workday_brief = f"Bedrock client setup failed: {st.session_state.orchestrator_error}"
        else:
            with st.spinner("Reviewing urgent and upcoming work across the book…"):
                st.session_state.workday_brief = st.session_state.orchestrator.route_query(
                    "Prepare today's advisor operations brief across the entire client book. Use query_book_metrics to retrieve both urgent_tasks and pending_tasks. Prioritize urgent items and tasks due soon, group by client and date, and list suggested preparation steps. Do not make investment recommendations and do not claim any task or external action was completed.",
                    client,
                    CLIENTS,
                )
    if run_brief:
        if st.session_state.orchestrator is None:
            st.session_state.meeting_brief = f"Bedrock client setup failed: {st.session_state.orchestrator_error}"
        else:
            with st.spinner("Preparing a concise brief with Bedrock…"):
                st.session_state.meeting_brief = st.session_state.orchestrator.route_query(
                    "Prepare a concise pre-meeting brief with: client context, discussion agenda based on existing notes and pending tasks, questions to confirm with the client, and items that require advisor judgment. Clearly identify that the supplied portfolio estimate is illustrative. Do not make investment recommendations or imply that any action has been taken.",
                    client,
                    CLIENTS,
                )
    if st.session_state.workday_brief:
        with st.expander("Today's priority queue", expanded=True):
            st.markdown(st.session_state.workday_brief)
            st.download_button(
                "Download today's queue",
                data=st.session_state.workday_brief,
                file_name="briefly-daily-priority-queue.txt",
                mime="text/plain",
                key="download_workday_brief",
            )
    if st.session_state.meeting_brief:
        with st.expander("Advisor-ready meeting brief", expanded=True):
            st.markdown(st.session_state.meeting_brief)
            st.download_button(
                "Download brief",
                data=st.session_state.meeting_brief,
                file_name=f"briefly-{client['id'].lower()}-meeting-brief.txt",
                mime="text/plain",
                key="download_meeting_brief",
            )

    st.markdown("<div style='margin:18px 0 6px'><span class='eyebrow'>Relationship timeline</span><h2 style='margin:4px 0'>Upcoming priorities</h2></div>", unsafe_allow_html=True)
    tasks_html = "".join(
        f"<div class='task-card {'urgent' if task['status'] == 'urgent' else ''}'><div class='task-date'>{task['date']}</div><div class='task-desc'>{task['description']}</div><div class='task-status'>● &nbsp;{task['status']}</div></div>"
        for task in sorted(client["pending_tasks"], key=lambda item: item["date"])
    ) or "<div class='task-card'>No upcoming tasks.</div>"
    st.markdown(f"<div class='task-track'>{tasks_html}</div>", unsafe_allow_html=True)

    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("<div class='eyebrow'>Conversation context</div><h3 style='margin:5px 0 12px'>Recent meeting notes</h3>", unsafe_allow_html=True)
        for note in client["meeting_notes"]:
            st.markdown(f"<div class='section-card' style='margin-bottom:10px;color:#51647e'>↳ &nbsp;{note}</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='eyebrow'>Human in the loop</div><h3 style='margin:5px 0 12px'>Compliance gate</h3>", unsafe_allow_html=True)
        st.markdown("<div class='section-card' style='color:#61738c;line-height:1.6'>Briefly can draft follow-ups and CRM actions. Every proposed action pauses here for advisor review; approval records a local audit entry.</div>", unsafe_allow_html=True)
        if st.session_state.audit_log:
            with st.expander(f"Audit log · {len(st.session_state.audit_log)}"):
                for entry in reversed(st.session_state.audit_log):
                    st.caption(f"{entry.get('decision','').title()} · {entry.get('action')} · {entry.get('reviewed_at','')}")
