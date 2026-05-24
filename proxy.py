import urllib.request
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

base_url = "https://integrate.api.nvidia.com/v1"

class NvidiaProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        target_url = base_url + self.path.replace('/v1', '')
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        post_data = post_data.replace(b'"openai/', b'"')
        
        was_stream = False
        try:
            body = json.loads(post_data)
            was_stream = body.get("stream", False)
            if was_stream:
                body["stream"] = False
            
            if "stream_options" in body:
                del body["stream_options"]
                
            post_data = json.dumps(body).encode('utf-8')
        except:
            pass
        
        req = urllib.request.Request(target_url, data=post_data, method="POST")
        for key, value in self.headers.items():
            if key.lower() not in ['host', 'content-length', 'accept-encoding']: req.add_header(key, value)
        req.add_header('Content-Length', str(len(post_data)))
                
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read()
                
                if was_stream:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Cache-Control', 'no-cache')
                    self.end_headers()
                    raw_json = json.loads(res_body)
                    chunk_json = {
                        "id": raw_json.get("id", "chatcmpl-123"),
                        "object": "chat.completion.chunk",
                        "created": raw_json.get("created", 0),
                        "model": raw_json.get("model", ""),
                        "choices": [{
                            "index": 0,
                            "delta": raw_json["choices"][0]["message"] if "choices" in raw_json and raw_json["choices"] else {"content": ""},
                            "finish_reason": raw_json["choices"][0].get("finish_reason", "stop") if "choices" in raw_json and raw_json["choices"] else "stop"
                        }]
                    }
                    self.wfile.write(f"data: {json.dumps(chunk_json)}\n\n".encode('utf-8'))
                    self.wfile.write(b"data: [DONE]\n\n")
                else:
                    self.send_response(response.status)
                    for k, v in response.headers.items():
                        if k.lower() not in ['transfer-encoding']: self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(res_body)
        except urllib.error.HTTPError as e:
            err = e.read()
            with open("last_error.json", "wb") as f:
                f.write(err)
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(err)
        except Exception as e:
            self.send_error(500, str(e))

if __name__ == "__main__":
    httpd = ThreadingHTTPServer(('0.0.0.0', 8081), NvidiaProxyHandler)
    httpd.serve_forever()
