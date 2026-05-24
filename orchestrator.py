import os
import sys
import json
import subprocess
import threading
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")
base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
model_name = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")

if not api_key:
    print("Error: NVIDIA_API_KEY not found in environment.")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

class NvidiaProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        target_url = base_url + self.path.replace('/v1', '')
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        req = urllib.request.Request(target_url, data=post_data, method="POST")
        for key, value in self.headers.items():
            if key.lower() not in ['host']:
                req.add_header(key, value)
                
        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            
    def log_message(self, format, *args):
        pass

def start_proxy():
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, NvidiaProxyHandler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd

def load_configs():
    with open('agent_configs.json', 'r') as f:
        return json.load(f)

def decide_agent(task, configs):
    agent_descriptions = "\n".join([f"- {name}: {info['description']}" for name, info in configs.items()])
    
    prompt = f"""You are an intelligent task router. Your job is to select the most appropriate AI agent for a user's task.
Here are the available agents and their strengths:
{agent_descriptions}

The user's task is: "{task}"

Analyze the task and output ONLY a JSON object containing your decision. Do not include markdown formatting or backticks.
Format: {{"selected_agent": "agent_name", "reason": "short explanation"}}"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.2,
            max_tokens=150,
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        decision = json.loads(content)
        return decision
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return {"selected_agent": "openclaw", "reason": "fallback"}

def execute_agent(agent_name, task, configs, unsafe_god_mode=False):
    if agent_name not in configs:
        print(f"Agent {agent_name} not found in configs.")
        return
        
    command_prefix = configs[agent_name]["command"]
    workspace_dir = os.path.abspath("agent_workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    
    secure_env = os.environ.copy()
    secure_env["NVIDIA_BASE_URL"] = "http://127.0.0.1:8081/v1"
    
    command = []
    
    if sys.platform == "darwin":
        if unsafe_god_mode:
            print("⚠️ RUNNING IN UNSAFE GOD MODE. FULL SYSTEM WRITE ACCESS GRANTED.")
            command = command_prefix + [task]
        else:
            print("🛡️ SECURE WORKSPACE SANDBOX ENABLED (macOS Seatbelt)")
            sb_profile = os.path.abspath("agent_profile.sb")
            command = ["sandbox-exec", "-D", f"WORKSPACE={workspace_dir}", "-f", sb_profile] + command_prefix + [task]
            
    elif sys.platform.startswith("linux"):
        if unsafe_god_mode:
            print("⚠️ RUNNING IN UNSAFE GOD MODE. FULL SYSTEM WRITE ACCESS GRANTED.")
            command = command_prefix + [task]
        else:
            print("🛡️ SECURE WORKSPACE SANDBOX ENABLED (Linux Bubblewrap)")
            # Bubblewrap sandbox: read-only root, read-write workspace
            command = [
                "bwrap", 
                "--ro-bind", "/", "/", 
                "--bind", workspace_dir, workspace_dir,
                "--dev", "/dev",
                "--proc", "/proc",
                "--tmpfs", "/tmp"
            ] + command_prefix + [task]
            
    elif sys.platform == "win32":
        if unsafe_god_mode:
            print("⚠️ RUNNING IN UNSAFE GOD MODE. FULL SYSTEM WRITE ACCESS GRANTED.")
        else:
            print("⚠️ Windows Detected. Network proxy active, but strict local file sandboxing requires WSL.")
        command = command_prefix + [task]
    else:
        command = command_prefix + [task]
        
    print(f"\n🚀 Routing to: {agent_name.upper()}")
    print(f"💻 Command: {' '.join(command)}")
    print("-" * 50)
    
    try:
        process = subprocess.Popen(command, env=secure_env)
        process.wait()
    except Exception as e:
        print(f"Failed to execute agent: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent AI Orchestrator")
    parser.add_argument("task", help="The task you want the AI agent to perform")
    parser.add_argument("--unsafe-god-mode", action="store_true", help="Allow agents to write/delete files anywhere on your system")
    args = parser.parse_args()
    
    print(f"Task received: {args.task}")
    
    httpd = start_proxy()
    print("🔒 Started local secure proxy on port 8081")
    
    configs = load_configs()
    decision = decide_agent(args.task, configs)
    
    selected_agent = decision.get("selected_agent", "openclaw").lower()
    print(f"🧠 Orchestrator Decision: Use {selected_agent}")
    print(f"📝 Reason: {decision.get('reason', 'N/A')}")
    
    execute_agent(selected_agent, args.task, configs, args.unsafe_god_mode)
