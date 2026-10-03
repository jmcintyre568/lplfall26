#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "✦ Briefly: AWS IAM Identity Center (SSO) Login Setup"
echo "=========================================================="
echo ""
echo "Running 'aws configure sso' with the local CLI..."
echo "When prompted:"
echo "  1. SSO session name: briefly"
echo "  2. SSO start URL: (Paste the URL provided by the hackathon)"
echo "  3. SSO region: (Enter the region provided, e.g., us-east-1 or us-west-2)"
echo "  4. SSO registration scopes: [ENTER] (defaults to sso:account:access)"
echo "  5. Browser will open: Click 'Allow' / 'Confirm and continue'"
echo "  6. CLI default client Region: us-west-2"
echo "  7. CLI default output format: json"
echo "  8. CLI profile name: briefly"
echo "=========================================================="
echo ""

"$DIR/.venv/bin/aws" configure sso

echo ""
echo "Testing AWS connection..."
"$DIR/.venv/bin/aws" sts get-caller-identity --profile briefly

echo ""
echo "✅ Authenticated successfully! You can now run Briefly with:"
echo "   AWS_PROFILE=briefly AWS_REGION=us-west-2 .venv/bin/streamlit run app.py"
echo ""
