#!/bin/bash
# Builds a combined CA bundle (Python's certifi roots + this Mac's system trust
# store) so Python-based tools trust the same certificates the OS/browser do.
# Needed because a corporate security tool's root CA can be trusted by macOS
# without being present in certifi's bundled cacert.pem, causing TLS failures
# for Python HTTPS clients (e.g. talking to Snowflake's S3-backed result stage)
# even though browser traffic to the same host works fine.
set -euo pipefail

OUT="$HOME/.conference_dashboard_ca_bundle.pem"
PYTHON_BIN="${1:-python3}"

CERTIFI_PATH=$("$PYTHON_BIN" -c "import certifi; print(certifi.where())")

{
  cat "$CERTIFI_PATH"
  security find-certificate -a -p /Library/Keychains/System.keychain 2>/dev/null || true
  security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain 2>/dev/null || true
} > "$OUT"

echo "Wrote combined CA bundle to: $OUT"
echo "Set this in your .env: SNOWFLAKE_CA_BUNDLE=$OUT"
