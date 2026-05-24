# Official AI Agent Secure Ecosystem

Welcome! This repository provides an enterprise-grade secure launcher for the world's most powerful open-source AI agent frameworks.

By using this repository, you can safely run **OpenClaw**, **ZeroClaw**, **Nanobot**, and **Hermes Agent** natively on your machine without fearing that they will delete your system files or silently exfiltrate your data to the internet.

## Included Agents
We support seamlessly sandboxing the following official tools:
1. **OpenClaw**: The viral Node.js autonomous worker.
2. **ZeroClaw**: The ultra-lightweight Rust runtime.
3. **Nanobot**: The highly-capable Python SDK.
4. **Hermes Agent**: The self-improving persistent agent by Nous Research.

## Installation

### Step 1: Install Official Frameworks
Run the one-click universal installer to automatically download and configure all 4 official agents onto your machine:
```bash
chmod +x install_official_agents.sh
./install_official_agents.sh
```

### Step 2: Configure API Keys
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and put in your NVIDIA NIM API key. Our configuration automatically overrides the default OpenAI settings in all 4 agents so they magically route through your blazing-fast local NVIDIA NIM endpoint!

## Usage: The Secure Launcher

Never run the agents blindly! Use our universal cross-platform `secure_run.sh` launcher.

```bash
./secure_run.sh openclaw chat
```
Or:
```bash
./secure_run.sh hermes
```

### How the Security Works
When you use `./secure_run.sh`:
1. **File System Cage**: On macOS, we use Seatbelt (`sandbox-exec`). On Linux, we use Bubblewrap (`bwrap`). The agent is physically incapable of writing to any folder outside of `agent_workspace/`.
2. **Network Exfiltration Block**: The OS kernel drops all outbound traffic. We spin up a local Python proxy (`proxy.py`) on `localhost:8081` that *only* forwards traffic directly to NVIDIA NIM. It is impossible for the agent to `curl` or connect to an attacker's server!

*Note: On Windows (Git Bash), the network proxy is active, but the filesystem sandbox requires using WSL (Windows Subsystem for Linux).*
