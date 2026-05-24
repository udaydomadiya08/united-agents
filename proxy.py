import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
from dotenv import load_dotenv

load_dotenv()

# We expect OPENAI_API_KEY to hold the nvapi key, but we will fall back to NVIDIA_API_KEY
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("NVIDIA_API_KEY")
base_url = "https://integrate.api.nvidia.com/v1"

class NvidiaProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        target_url = base_url + self.path.replace('/v1', '')
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        req = urllib.request.Request(target_url, data=post_data, method="POST")
        for key, value in self.headers.items():
            if key.lower() not in ['host']:
                req.add_header(key, value)
        
        # Ensure our nvapi key is passed
        req.add_header("Authorization", f"Bearer {api_key}")
                
        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_response(500)
            self.end_headers()
            
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    if not api_key:
        print("Error: No API key found. Set OPENAI_API_KEY in .env")
        sys.exit(1)
        
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, NvidiaProxyHandler)
    print("🔒 Secure Proxy running on 127.0.0.1:8081")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
