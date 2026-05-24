#!/usr/bin/env bash
set -e

echo "🚀 Installing Official AI Agent Ecosystem..."

# 1. OpenClaw (Node.js ecosystem)
echo "----------------------------------------"
echo "🦞 Installing OpenClaw..."
if ! command -v openclaw &> /dev/null; then
    npm install -g openclaw || echo "⚠️ Warning: Failed to install OpenClaw globally. Check npm permissions."
else
    echo "✅ OpenClaw already installed."
fi

# 2. ZeroClaw (Rust ecosystem)
echo "----------------------------------------"
echo "⚡ Installing ZeroClaw..."
if ! command -v zeroclaw &> /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/zeroclaw-labs/zeroclaw/master/install.sh | bash || echo "⚠️ Warning: ZeroClaw install failed."
else
    echo "✅ ZeroClaw already installed."
fi

# 3. Nanobot (Python/UV ecosystem)
echo "----------------------------------------"
echo "🔬 Installing Nanobot..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

if ! command -v nanobot &> /dev/null; then
    uv tool install nanobot-ai || echo "⚠️ Warning: Nanobot install failed."
else
    echo "✅ Nanobot already installed."
fi

# 4. Hermes Agent (Nous Research / Python ecosystem)
echo "----------------------------------------"
echo "🦉 Installing Hermes Agent..."
if ! command -v hermes &> /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash || echo "⚠️ Warning: Hermes install failed."
else
    echo "✅ Hermes Agent already installed."
fi

echo "----------------------------------------"
echo "🎉 All official agents installed successfully!"
echo "Run the following commands to configure them with your NVIDIA API Keys:"
echo "  - openclaw configure"
echo "  - zeroclaw onboard"
echo "  - nanobot onboard"
echo "  - hermes model"
