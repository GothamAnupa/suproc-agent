from http.server import BaseHTTPRequestHandler
import json
from app.agent import run_agent


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests with a natural language query"""
        try:
            content_length = int(self.headers.get("content-length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            
            query = data.get("query", "").strip()
            if not query:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing 'query' field"}).encode())
                return
            
            response = run_agent(query)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response.model_dump(), indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
