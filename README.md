# Briefly — Wealth Management AI Copilot

A Streamlit meeting-prep MVP for a wealth-advisor hackathon. It uses native `boto3` and Amazon Bedrock Converse with `anthropic.claude-3-sonnet-20240229-v1:0`; there is no LangChain or LlamaIndex. All included client data is synthetic and contains no contact details or account identifiers.

## Run locally

```bash
cd briefly
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
aws configure             # or use an IAM role / existing AWS profile
streamlit run app.py
```

Set `AWS_REGION` to a region where the model is available (default: `us-west-2`). The AWS identity needs Bedrock Runtime permissions and access to the model. AWS credentials are picked up through the standard boto3 credential chain. Never put credentials in source control.

## Included features

- Ten synthetic profiles with meeting notes and pending/urgent tasks.
- Client dashboard and responsive horizontal task timeline.
- Muse chat interface with four locally executed tools: illustrative portfolio drift estimate, CRM note keyword search, compliance proposal draft, and aggregate book metrics.
- Bedrock Converse tool-use loop with credential and service error handling.
- Advisor review expander for proposed actions. Approval or rejection only records a local session audit entry; it does not send email, change a CRM, or execute trades.

## Important demo boundaries

This prototype is not production software and is not investment, tax, or legal advice. Portfolio drift is an illustrative calculation using profile-level targets, not custodian holdings. The generated data and audit log are in-memory demonstration features. Production use would require approved data sources, durable access-controlled audit storage, identity and authorization controls, security review, and firm compliance approval.
