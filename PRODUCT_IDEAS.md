# Briefly product direction

## In the current MVP

- **Morning operations triage:** ask the Bedrock model to retrieve urgent and upcoming tasks across the synthetic book, then organize them into an advisor work queue. The model chooses the tools; the app does not change task status.
- **Meeting preparation:** summarize a selected client's synthetic notes and open tasks into an agenda and questions for the advisor.
- **Policy and procedure lookup:** optionally retrieve passages from an approved Bedrock Knowledge Base. The model should cite the returned source; advisors verify the source before relying on it.
- **Approval-gated follow-up proposals:** draft an action into the review gate. Approval in the demo records a local session entry only; it does not send messages or update a CRM.

## Useful next workflows for a wealth or fintech operations team

1. **Post-meeting follow-through:** use Amazon Transcribe on an approved recording, then Bedrock to draft a meeting summary, owners, due dates, and suggested CRM updates. Show source timestamps and require advisor approval before writing to a system of record.
2. **Service-case triage:** read a permission-filtered queue of transfer, beneficiary, distribution, and account-service cases; group duplicate issues, flag missing information, and draft next-step checklists. Keep money movement and account changes outside model authority.
3. **Document intake review:** use Amazon Textract for extraction and Bedrock for a checklist against approved KYC or account-opening requirements. Highlight uncertain fields and missing documents for an operations analyst; do not make eligibility or adverse decisions.
4. **Exception explanations:** summarize custodial feed exceptions, failed data imports, or overdue service-level items into a queue with affected source records and suggested owners. Deterministic code should calculate dates, balances, and thresholds; the model should explain and prioritize them.
5. **Compliance answer assistant:** index approved procedures in a Bedrock Knowledge Base, return relevant passages with links, and log which sources supported a draft. Guardrails can add content controls, but do not replace source checks, permissions, or advisor review.
6. **Durable review history:** replace the in-memory demo audit log with a protected datastore, least-privilege read/write roles, defined retention, and monitoring. Record proposal, reviewer, decision, and timestamp without silently executing the proposed action.

## Design boundaries for a production pilot

- Connect only to firm-approved data sources and enforce user/client permissions before any record reaches a model prompt or retrieval request.
- Use deterministic services for calculations, eligibility rules, dates, and transaction state. Use the model to summarize, classify, retrieve, and draft.
- Keep user confirmation for messages and material record changes. Never let the model move funds, place trades, alter beneficiaries, or decide access or eligibility.
- Choose the Bedrock region or inference profile to match the firm's data-residency requirements; some inference profiles route across AWS Regions.
- Keep synthetic data in the hackathon demo until compliance and security approve the specific production data flow.
