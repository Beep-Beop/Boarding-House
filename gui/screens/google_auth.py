import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class GoogleAuthHandler:
    def __init__(self, api, app, on_success, on_error):
        self.api = api
        self.app = app
        self.on_success = on_success
        self.on_error = on_error
        self.server = None
        self.port = 9876
        self._done = False
        self._server_event = threading.Event()

    def _find_free_port(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def start(self):
        self.port = self._find_free_port()

        class CallbackHandler(BaseHTTPRequestHandler):
            result = None

            def log_message(self, format, *args):
                pass

            def do_GET(self):
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)

                if parsed.path == "/token":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"OK")

                    access_token = params.get("access_token", [None])[0]
                    user_id = params.get("user_id", [None])[0]
                    role = params.get("role", [None])[0]
                    name = params.get("name", [None])[0]
                    email = params.get("email", [None])[0]
                    is_new = params.get("is_new", ["false"])[0] == "true"

                    if access_token and user_id:
                        self.server._result = {
                            "access_token": access_token,
                            "user_id": int(user_id),
                            "role": role,
                            "name": name,
                            "email": email,
                            "is_new": is_new,
                        }
                        self.server._server_event.set()
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><p>Waiting for login...</p></body></html>")

        self.server = HTTPServer(("127.0.0.1", self.port), CallbackHandler)
        self.server._result = None
        self.server._server_event = self._server_event
        self.server.timeout = 0.2

        def run():
            while not self._server_event.is_set():
                self.server.handle_request()

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

        login_url = f"{self.api.base_url}/auth/google/login?redirect_port={self.port}"
        webbrowser.open(login_url)

        self._poll()

    def _poll(self):
        if self._done:
            return
        if not self._server_event.is_set():
            self.app.after(300, self._poll)
            return

        self._done = True
        result = self.server._result if self.server else None
        self._shutdown()

        if result:
            self.api.access_token = result["access_token"]
            self.app.after(0, lambda: self.on_success(result))
        else:
            self.app.after(0, lambda: self.on_error("Google login failed"))

    def _shutdown(self):
        if self.server:
            try:
                self.server.server_close()
            except Exception:
                pass
            self.server = None
