from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        response = {
            "bot": "Dolphin",
            "status": "online"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(
            json.dumps(response).encode("utf-8")
        )
