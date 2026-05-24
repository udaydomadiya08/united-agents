# Native AI Orchestrator

A blazing-fast, **ultra-secure**, and multi-agent AI orchestrator powered by NVIDIA NIM APIs. 

Say goodbye to heavy 8GB Docker sandboxes. This orchestrator runs entirely native on your machine while utilizing kernel-level sandboxing to mathematically guarantee **zero data exfiltration** and protect your local files.

## Features
- **🧠 Multi-Agent Router**: Uses Llama 3.1 to intelligently route your prompts to the best-suited lightweight agent (ZeroClaw, OpenClaw, Hermes, or Nanobot).
- **🛡️ Data Exfiltration Security**: A built-in local proxy securely channels agent reasoning to the NVIDIA API, while macOS Seatbelt or Linux Bubblewrap permanently blocks the agent from connecting to the internet.
- **📁 Safe Workspace Isolation**: Agents can *read* your whole system to answer questions, but can only *write/delete* files inside the `agent_workspace/` directory by default. 

## Installation

### Prerequisites
- Python 3.9+
- NVIDIA NIM API Key (`NVIDIA_API_KEY`)

### 🍎 macOS Setup (Native Seatbelt Sandbox)
1. Clone the repository: `git clone https://github.com/udaydomadiya08/united-agents.git && cd united-agents`
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run the agent setup script (installs OpenClaw and local agent binaries):
   ```bash
   chmod +x setup_agents.sh && ./setup_agents.sh
   ```
4. Copy `.env.example` to `.env` and insert your API keys.

### 🐧 Linux Setup (Bubblewrap Sandbox)
1. Install Bubblewrap for kernel-level sandboxing:
   - Ubuntu/Debian: `sudo apt-get install bubblewrap`
   - Arch Linux: `sudo pacman -S bubblewrap`
   - Fedora: `sudo dnf install bubblewrap`
2. Clone the repository: `git clone https://github.com/udaydomadiya08/united-agents.git && cd united-agents`
3. Install Python dependencies: `pip install -r requirements.txt`
4. Run the setup script:
   ```bash
   chmod +x setup_agents.sh && ./setup_agents.sh
   ```
5. Copy `.env.example` to `.env` and insert your API keys.

### 🪟 Windows Setup
*Note: Strict file-write sandboxing requires Windows Subsystem for Linux (WSL). Running directly in PowerShell will default to Unsafe mode, but the Network Exfiltration Proxy will still protect you.*

**Option 1: Using WSL (Recommended for full security)**
- Open your WSL terminal and follow the **Linux Setup** instructions above.

**Option 2: Native Windows (PowerShell/CMD)**
1. Clone the repository and navigate into it.
2. Install Python dependencies: `pip install -r requirements.txt`
3. Install OpenClaw globally (requires Node.js): `npm install -g openclaw`
4. Copy `.env.example` to `.env` and insert your API keys.

## Usage

Run the orchestrator by passing your task in quotes:
```bash
python orchestrator.py "read my python files and suggest improvements"
```

### God Mode (Danger!)
By default, the agents are restricted to writing files only in the local `agent_workspace/` folder. If you actually want an agent to globally modify or delete files anywhere on your hard drive, you can explicitly bypass the file-system sandbox using the God Mode flag:
```bash
python orchestrator.py "refactor my entire global project" --unsafe-god-mode
```

## OS Support
- **macOS**: ✅ Full Support (Kernel Sandboxing via `sandbox-exec`)
- **Linux**: ✅ Full Support (User-space Sandboxing via `bwrap`)
- **Windows**: ⚠️ Partial Support (The Data Exfiltration Proxy works natively, but strict file-write sandboxing requires running the orchestrator inside WSL).
