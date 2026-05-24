#!/usr/bin/env bash
set -e

if [ "$#" -eq 0 ]; then
    echo "Usage: ./secure_run.sh <agent_command> [args...]"
    echo "Example: ./secure_run.sh openclaw chat"
    exit 1
fi

echo "🛡️ Initializing Secure Sandbox Launcher..."

# 1. Start the proxy
python proxy.py &
PROXY_PID=$!
sleep 1 # Wait for proxy to bind

# 2. Setup Workspace
WORKSPACE_DIR="$(pwd)/agent_workspace"
mkdir -p "$WORKSPACE_DIR"
echo "📁 Workspace locked to: $WORKSPACE_DIR"

# 3. Export environment variables to force local proxy usage
export OPENAI_BASE_URL="http://127.0.0.1:8081/v1"
export OPENCLAW_BASE_URL="http://127.0.0.1:8081/v1"

# 4. OS Detection & Sandbox Wrapping
OS_NAME=$(uname -s)
echo "🚀 OS Detected: $OS_NAME"
echo "----------------------------------------"

set +e
if [[ "$OS_NAME" == "Darwin" ]]; then
    # macOS: Seatbelt sandbox
    sandbox-exec -D WORKSPACE="$WORKSPACE_DIR" -f agent_profile.sb "$@"
elif [[ "$OS_NAME" == "Linux" ]]; then
    # Linux: Bubblewrap sandbox
    if command -v bwrap &> /dev/null; then
        bwrap --ro-bind / / \
              --bind "$WORKSPACE_DIR" "$WORKSPACE_DIR" \
              --dev /dev \
              --proc /proc \
              --tmpfs /tmp \
              --unshare-net \
              "$@"
    else
        echo "⚠️ Warning: bwrap not installed! Running natively without filesystem sandbox."
        "$@"
    fi
elif [[ "$OS_NAME" == MINGW* ]] || [[ "$OS_NAME" == CYGWIN* ]]; then
    # Windows fallback
    echo "⚠️ Windows Detected. Network proxy active, but strict local file sandboxing requires WSL."
    "$@"
else
    # Unknown OS
    "$@"
fi
EXIT_CODE=$?
set -e

echo "----------------------------------------"
echo "🛑 Shutting down Secure Proxy..."
kill $PROXY_PID

exit $EXIT_CODE
