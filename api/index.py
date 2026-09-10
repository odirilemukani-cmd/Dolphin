from http.server import BaseHTTPRequestHandler
import json

from _viper import (
    BOT_NAME,
    json_safe_state
)


class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        response = {
            "bot": BOT_NAME,
            "status": "online",
            "message": "Viper API is online",
            "state": json_safe_state()
        }

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(
            json.dumps(response).encode("utf-8")
        )
