from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        msg = "All is working, hello from python backend! :)"
        # Print request info to container logs.
        print(f"{datetime.datetime.utcnow().isoformat()} path={self.path}")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(msg.encode("utf-8"))

    def log_message(self, fmt, *args):
        # Silence default BaseHTTPRequestHandler logs.
        return


def main():
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("backend listening on http://0.0.0.0:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()

