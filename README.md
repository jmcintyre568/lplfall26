# Briefly — Wealth Management AI Copilot

A Streamlit meeting-prep MVP for a wealth-advisor hackathon. It uses native `boto3` and Amazon Bedrock Converse with a model ID or inference profile selected in the sidebar or supplied as `BEDROCK_MODEL_ID`; there is no LangChain or LlamaIndex. All included client data is synthetic and contains no contact details or account identifiers.

## Run locally

```bash
cd briefly
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
aws configure sso --profile briefly
aws sso login --profile briefly
AWS_PROFILE=briefly AWS_REGION=us-west-2 streamlit run app.py
```

For IAM Identity Center, use the AWS access portal URL and SSO region supplied by your administrator when the CLI prompts you. Choose an account and permission set that have least-privilege access to Bedrock. The app uses temporary credentials from the standard boto3 profile chain; it never stores access keys. You can also use an existing IAM role or local AWS profile. Set `AWS_REGION` to a region where the selected model and configured Bedrock resources are available (default: `us-west-2`).

### Connect the Bedrock console model

1. In the Bedrock console, choose the AWS Region that your firm allows for this workload.
2. In **Model catalog**, choose an active text model that supports the Converse API and tool use. Open its model details and use the playground to confirm that it is enabled for your account.
3. Copy the model ID or the appropriate inference profile ID from the model details/programmatic access section and paste it in Briefly's **Bedrock model / inference profile ID** sidebar field. You can also set `BEDROCK_MODEL_ID` in the app's environment.
4. Configure local sign-in separately through an IAM Identity Center AWS CLI profile or an approved IAM role. The console playground selection does not pass credentials into the local Streamlit app.

The originally requested Claude 3 Sonnet model has reached end-of-life in `us-west-2` (July 30, 2026); select a currently active model instead. Cross-Region inference profiles can route prompts outside the source AWS Region, so choose a profile that fits your firm's data-residency requirements. The app's Converse tool loop is its agentic layer: Bedrock returns model-directed tool requests, the app executes only its allow-listed local/AWS retrieval tools, then sends results back for a grounded answer.

On macOS, if the AWS CLI is not installed, install AWS CLI v2 using [AWS's official installer instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). Then complete the SSO steps above in your own terminal. The SSO start URL and region identify your organization’s sign-in portal; do not paste AWS access keys or passwords into the app or chat.

Click **Check AWS connection** in the sidebar to check that the current profile can authenticate. This calls STS and does not display account identifiers. It does not verify Bedrock model access; model access is checked when you submit a chat prompt or generate a brief.

### Optional Bedrock integrations

Copy `.env.example` to a local `.env` only if you have a trusted environment loader; Streamlit does not load `.env` automatically. Prefer exporting the following variables in the shell or your deployment environment. Never commit secrets.

- **Guardrails:** set `BEDROCK_GUARDRAIL_ID` and `BEDROCK_GUARDRAIL_VERSION` to an existing published Guardrail. Briefly sends this configuration with each Converse call. Guardrails complement the advisor approval gate; AWS documents that Converse Guardrails do not evaluate tool definitions, tool-use arguments, or tool results.
- **Advisor Knowledge Base:** set `BEDROCK_KNOWLEDGE_BASE_ID` to an existing, ingested Bedrock Knowledge Base. The agent then gets an additional `search_advisor_library` tool that retrieves up to five relevant passages and source locations for policy and process questions. Use approved reference material and grant the AWS profile only the permissions it needs to retrieve from that Knowledge Base.

These integrations require their AWS resources to be created and configured in the selected region. No resources are created automatically by the app.

## Included features

- Ten synthetic profiles with meeting notes and pending/urgent tasks.
- Client dashboard and responsive horizontal task timeline.
- Agentic morning book triage that asks the model to call urgent and pending task tools, then prioritizes work across the book.
- Muse chat interface with four locally executed tools: illustrative portfolio drift estimate, CRM note keyword search, compliance proposal draft, and aggregate book metrics.
- One-click AI meeting brief with a downloadable text summary.
- Optional Bedrock Guardrails and Bedrock Knowledge Base retrieval, enabled by configuration.
- A sidebar AWS credential check that does not show account identifiers.
- Runtime model/inference profile selection so the app does not rely on a retired hard-coded model ID.
- Bedrock Converse tool-use loop with credential and service error handling.
- Advisor review expander for proposed actions. Approval or rejection only records a local session audit entry; it does not send email, change a CRM, or execute trades.

## Important demo boundaries

This prototype is not production software and is not investment, tax, or legal advice. Portfolio drift is an illustrative calculation using profile-level targets, not custodian holdings. The generated data and audit log are in-memory demonstration features. Production use would require approved data sources, durable access-controlled audit storage, identity and authorization controls, security review, and firm compliance approval.

See [PRODUCT_IDEAS.md](PRODUCT_IDEAS.md) for everyday wealth and fintech operations workflows and their implementation boundaries.
