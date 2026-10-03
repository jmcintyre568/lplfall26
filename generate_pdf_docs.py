"""Generate a publication-quality 3-page technical specification PDF for Briefly."""

from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Canvas that adds running headers, rules, and dynamic 'Page X of Y' footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (on all pages)
        self.drawString(40, 755, "BRIEFLY · WEALTH ADVISOR AI COPILOT")
        self.drawRightString(letter[0] - 40, 755, "SYSTEM ARCHITECTURE & TECHNICAL SPECIFICATION")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(40, 748, letter[0] - 40, 748)

        # Footer
        self.line(40, 42, letter[0] - 40, 42)
        self.setFont("Helvetica", 7.5)
        self.drawString(40, 32, "Confidential · LPL Hackathon Fall 2026 · Native AWS Bedrock Architecture")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 32, page_text)
        self.restoreState()


def build_pdf(filename: str = "Briefly_Technical_Documentation.pdf"):
    # 40pt margins give 532pt printable width and 690pt height
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()

    PRIMARY = colors.HexColor("#0f172a")  # Deep Navy
    ACCENT = colors.HexColor("#1d4ed8")   # Royal Blue
    TEXT_DARK = colors.HexColor("#1e293b")
    MUTED = colors.HexColor("#64748b")
    LIGHT_BG = colors.HexColor("#f8fafc")
    BORDER_COLOR = colors.HexColor("#cbd5e1")

    # Typography styles
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=ACCENT,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="MetaText",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=MUTED,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="SubSectionHeading",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=ACCENT,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="BodyDark",
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=TEXT_DARK,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="CalloutText",
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#1e3a8a"),
    ))

    styles.add(ParagraphStyle(
        name="CodeBlock",
        fontName="Courier",
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#0f172a"),
    ))

    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
    ))

    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=7,
        leading=9.5,
        textColor=TEXT_DARK,
    ))

    story = []

    # =========================================================================
    # PAGE 1: TITLE, METADATA, EXECUTIVE SUMMARY & ARCHITECTURE OVERVIEW
    # =========================================================================
    story.append(Paragraph("System Architecture, Deterministic Engines & Technical Specification", styles["DocTitle"]))
    story.append(Paragraph("A Native Amazon Bedrock Platform for Wealth Advisory & Independent RIA Operations", styles["DocSubtitle"]))

    meta_data = [
        [
            Paragraph("<b>Target Cloud:</b> Amazon Web Services (AWS)", styles["MetaText"]),
            Paragraph("<b>Active Region:</b> us-east-1 (N. Virginia)", styles["MetaText"]),
        ],
        [
            Paragraph("<b>Bedrock Model:</b> Amazon Nova Pro (<code>us.amazon.nova-pro-v1:0</code>)", styles["MetaText"]),
            Paragraph("<b>SDK Protocol:</b> Native <code>boto3</code> Converse API (Zero LangChain)", styles["MetaText"]),
        ],
        [
            Paragraph(f"<b>System Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles["MetaText"]),
            Paragraph("<b>Identity & Security:</b> IAM Role / STS Caller Identity", styles["MetaText"]),
        ]
    ]
    meta_table = Table(meta_data, colWidths=[266, 266])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    summary_html = (
        "<b>Executive Summary:</b> Briefly is an enterprise AI copilot designed for wealth advisors. "
        "Unlike generic LLM wrappers that fabricate calculations, Briefly enforces a strict architectural boundary: "
        "<b>deterministic calculations</b> (RMDs, portfolio drift, tax-loss harvesting, wash-sale detection) are executed "
        "strictly in verifiable local Python code, while <b>Amazon Bedrock</b> operates as a supervisor agent via its "
        "native Converse API. Bedrock Guardrails filter out non-compliant advice, and an advisor approval gate ensures "
        "no email, trade, or CRM alteration occurs without explicit human authorization."
    )
    summary_table = Table([[Paragraph(summary_html, styles["CalloutText"])]], colWidths=[532])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#bfdbfe")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. System Architecture & Component Isolation", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
    story.append(Paragraph(
        "Briefly relies exclusively on native AWS SDK primitives. The architecture comprises five isolated layers:",
        styles["BodyDark"]
    ))

    arch_layers = [
        ["Layer", "AWS Service / Component", "Function & Operational Security Boundary"],
        [
            "1. Presentation",
            "Streamlit Dashboard",
            "Advisor workspace with client switcher, metrics snapshot, task tracks, meeting brief export, and high-contrast LPL Assistant chat."
        ],
        [
            "2. Agentic Supervisor",
            "Amazon Bedrock Converse API\n(us.amazon.nova-pro-v1:0)",
            "Model-driven autonomous reasoning loop. Decides when to invoke financial tools, inspects arguments, and synthesizes grounded natural language briefs."
        ],
        [
            "3. Safety & Policy",
            "Amazon Bedrock Guardrails &\nBedrock Knowledge Bases",
            "Inspects prompts and outputs against fiduciary constraints (PII redaction, investment advice disclaimers). Retrieves firm compliance documents from S3."
        ],
        [
            "4. Calculation Core",
            "Deterministic Planning Engine\n(planning.py)",
            "IRS Pub. 590-B Uniform Lifetime RMD tables, lot-level portfolio rebalancing math, wash-sale detection, and SEC Reg BI meeting documentation screens."
        ],
        [
            "5. Governance",
            "Durable SQLite Audit Trail\n(audit.py)",
            "Immutable session log capturing proposed advisor actions, reviewer identity, UTC timestamp, and approval/rejection decisions."
        ]
    ]

    t_arch = Table([[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row] for r, row in enumerate(arch_layers)], colWidths=[90, 160, 282])
    t_arch.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 4.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_arch)

    # =========================================================================
    # PAGE 2: DETERMINISTIC PLANNING ENGINE SPECIFICATIONS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("2. Deterministic Financial Planning Specification (planning.py)", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
    story.append(Paragraph(
        "A foundational principle of Briefly is that <b>large language models must never compute client financial balances or tax liabilities</b>. "
        "The module <code>planning.py</code> implements pure mathematical business logic across four critical advisor workflows:",
        styles["BodyDark"]
    ))

    # 2.1 RMD
    story.append(Paragraph("2.1 Required Minimum Distribution (RMD) Planner — SECURE 2.0 Compliance", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "Under the SECURE 2.0 Act, required beginning ages have transitioned based on birth cohort. "
        "Briefly automatically categorizes pre-tax retirement accounts (Traditional IRA, SEP, SIMPLE, Rollover, 401k) "
        "and divides the prior year-end balance by the IRS Uniform Lifetime Table (Publication 590-B) factor:",
        styles["BodyDark"]
    ))

    rmd_data = [
        ["Birth Year Cohort", "SECURE 2.0 Start Age", "Distribution Deadline", "Statutory Rule & Penalty Avoidance"],
        ["Born 1950 or earlier", "Age 72", "December 31 of current year", "Original SECURE Act 1.0 schedule."],
        ["Born 1951 – 1959", "Age 73", "April 1 following year (1st yr), Dec 31 thereafter", "SECURE 2.0 primary transition band."],
        ["Born 1960 or later", "Age 75", "April 1 following year (1st yr), Dec 31 thereafter", "SECURE 2.0 extended horizon for younger retirees."]
    ]
    t_rmd = Table([[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row] for r, row in enumerate(rmd_data)], colWidths=[110, 110, 140, 172])
    t_rmd.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_rmd)
    story.append(Spacer(1, 6))

    # 2.2 Portfolio Drift
    story.append(Paragraph("2.2 Lot-Level Allocation Drift & Concentration Limits", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "Holdings are aggregated across taxable, Traditional IRA, and Roth IRA sub-accounts. "
        "Asset classes (Equity, Fixed Income, Cash) are measured against firm model profiles. "
        "When any asset class diverges by more than <b>±5.0 percentage points</b>, an alert is triggered. "
        "Single-stock positions exceeding <b>10.0%</b> are isolated for concentration risk review.",
        styles["BodyDark"]
    ))

    drift_data = [
        ["Risk Profile", "Target Equity", "Target Fixed Income", "Target Cash", "Rebalance Action Trigger"],
        ["Aggressive", "80.0%", "15.0%", "5.0%", "Equity allocation <75% or >85%"],
        ["Moderate", "60.0%", "35.0%", "5.0%", "Equity allocation <55% or >65%"],
        ["Conservative", "30.0%", "60.0%", "10.0%", "Equity allocation <25% or >35%"]
    ]
    t_drift = Table([[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row] for r, row in enumerate(drift_data)], colWidths=[105, 100, 110, 100, 117])
    t_drift.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_drift)
    story.append(Spacer(1, 6))

    # 2.3 Tax Loss
    story.append(Paragraph("2.3 Tax-Loss Harvesting & Wash-Sale Screening (IRC § 1091)", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "Only taxable lots are evaluated for tax-loss opportunities. The screener applies a minimum $500 loss threshold, "
        "classifies short-term vs. long-term holding periods, and scans cross-account purchases within a <b>30-day window</b> "
        "to prevent IRS Section 1091 wash-sale disallowance. Non-substantially-identical replacement proxies (e.g. S&P 500 to Total Stock Market) are recommended.",
        styles["BodyDark"]
    ))
    story.append(Spacer(1, 6))

    # 2.4 Reg BI
    story.append(Paragraph("2.4 SEC Regulation Best Interest (Reg BI) Meeting Documentation Screen", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "Prior to committing meeting notes to a CRM or compliance file, Briefly runs a 10-point audit checklist against raw transcripts:",
        styles["BodyDark"]
    ))

    regbi_items = [
        ["Reg BI Audit Element", "Evaluation Focus", "Standard Required Evidence"],
        ["1. Client Goals", "Stated retirement or wealth milestones", "Target retirement date, capital growth objective"],
        ["2. Risk Profile", "Risk capacity & tolerance to drawdown", "Confirmation of volatility willingness"],
        ["3. Time Horizon", "Liquidity horizon and life milestones", "Estimated withdrawal timeframe in years"],
        ["4. Cash Flow & Liquidity", "Immediate or near-term capital needs", "Emergency reserve amounts or planned expenditures"],
        ["5. Tax Considerations", "Tax status and distribution strategy", "Marginal tax bracket, Roth vs. Traditional timing"],
        ["6. Fee Disclosures", "Advisory, custodial, and expense ratios", "Explicit presentation of product costs"],
        ["7. Alternatives Analyzed", "Comparison of competing investment options", "Documentation of why alternative was rejected"],
        ["8. Conflict Disclosures", "Affiliated compensation or incentives", "Form ADV Part 2A / Form CRS delivery"],
        ["9. Client Consent", "Explicit advisor agreement", "Verbal or written client concurrence"],
        ["10. Actionable Next Steps", "Assigned owners, tasks, and follow-ups", "Clear due dates for execution"]
    ]
    t_regbi = Table([[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row] for r, row in enumerate(regbi_items)], colWidths=[120, 192, 220])
    t_regbi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 3.2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_regbi)

    # =========================================================================
    # PAGE 3: BEDROCK CONVERSE LOOP, ACTION TOOLS & FIDUCIARY GOVERNANCE
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Amazon Bedrock Orchestration & Converse Loop", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
    story.append(Paragraph(
        "Briefly executes on Amazon Bedrock's native <code>Converse</code> API with Amazon Nova Pro (<code>us.amazon.nova-pro-v1:0</code>). "
        "This architecture delivers predictable token utilization, exact JSON schema validation, and zero framework overhead.",
        styles["BodyDark"]
    ))

    code_sample = (
        "// Bedrock Converse Native Tool Loop (agent.py)\n"
        "request = {\n"
        "    'modelId': 'us.amazon.nova-pro-v1:0',\n"
        "    'system': [{'text': SYSTEM_PROMPT}],\n"
        "    'messages': messages,\n"
        "    'toolConfig': self.tool_config,\n"
        "    'inferenceConfig': {'maxTokens': 1200, 'temperature': 0.2}\n"
        "}\n"
        "response = bedrock_runtime.converse(**request)"
    )
    t_code = Table([[Paragraph(f"<pre>{code_sample}</pre>", styles["CodeBlock"])]], colWidths=[532])
    t_code.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_code)
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.1 Implemented Action Tools", styles["SubSectionHeading"]))
    tool_list = [
        ["Tool Identifier", "Input Schema", "Operational Description"],
        ["get_portfolio_drift", "client_json: object", "Computes allocation divergence vs. target model. Returns percentage point delta."],
        ["query_crm_notes", "client_id: str, query: str", "Natural language keyword retrieval across prior advisor CRM interaction logs."],
        ["draft_compliance_log", "action: str, details: str", "Intercepts external action requests (email, trades). Formats payload for approval gate."],
        ["query_book_metrics", "query_type: enum", "Aggregates book-level metrics (AUM, client count, urgent tasks, pending deadlines)."],
        ["search_advisor_library", "query: str", "Vector RAG search over Bedrock Knowledge Base connected to S3 compliance manuals."]
    ]
    t_tools = Table([[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row] for r, row in enumerate(tool_list)], colWidths=[120, 130, 282])
    t_tools.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_tools)
    story.append(Spacer(1, 10))

    # 4. Governance & Audit Trail
    story.append(Paragraph("4. Fiduciary Governance, Audit Trail & Security Boundary", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
    story.append(Paragraph(
        "In wealth management, autonomous agent execution presents unacceptable regulatory risk. "
        "Briefly enforces an air-gap between model synthesis and production actions:",
        styles["BodyDark"]
    ))

    story.append(Paragraph("4.1 Human-in-the-Loop Fiduciary Gate", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "Whenever the supervisor model determines that an outbound email, CRM update, or trade should be performed, "
        "it emits a <code>BRIEFLY_PROPOSAL</code> envelope. Execution is immediately halted. The proposal surfaces "
        "in the Streamlit UI with <b>Approve & Log</b> and <b>Reject</b> buttons. No external API is triggered without human approval.",
        styles["BodyDark"]
    ))

    story.append(Paragraph("4.2 Durable SQLite Audit Trail (audit.py)", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "All advisor approvals and rejections are immutably logged to an SQLite database with UTC timestamps, "
        "reviewer credentials, proposed action text, and client ID. The log can be exported directly to CSV for compliance review:",
        styles["BodyDark"]
    ))

    audit_schema = [
        ["Field", "Type", "Description & Compliance Value"],
        ["id", "INTEGER PRIMARY KEY", "Autoincrementing record sequence number."],
        ["reviewed_at", "TEXT (ISO 8601)", "UTC timestamp of the human advisor's final decision."],
        ["client_id", "TEXT", "Stable synthetic client identifier (e.g. C-1001)."],
        ["action", "TEXT", "Categorical action requested (e.g. send_email, update_crm)."],
        ["details", "TEXT", "Verbatim proposed action payload drafted by Bedrock."],
        ["decision", "TEXT", "Explicit advisor ruling: 'approved' or 'rejected'."],
        ["reviewer", "TEXT", "Authenticated user identity (IAM role / advisor ID)."]
    ]
    t_audit = Table([[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row] for r, row in enumerate(audit_schema)], colWidths=[90, 130, 312])
    t_audit.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 3.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(t_audit)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Generated PDF documentation: {filename}")


if __name__ == "__main__":
    build_pdf()
