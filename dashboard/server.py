import http.server
import socketserver
import webbrowser
import os
import sys
import socket

PORT = 5050
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        sys.stderr.write(f"[LANDIS-II Server] {args[0]} - {args[1]}\n")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_server():
    os.chdir(DIRECTORY)
    url = f"http://localhost:{PORT}/index.html"

    if is_port_in_use(PORT):
        print("=" * 60)
        print("LANDIS-II Simulation Platform is already running!")
        print(f"Opening browser at: {url}")
        print("=" * 60)
        webbrowser.open(url)
        return

    try:
        with CustomTCPServer(("", PORT), Handler) as httpd:
            print("=" * 60)
            print("LANDIS-II Forest Landscape Simulation & Disturbance Framework")
            print(f"Server running at: {url}")
            print("=" * 60)
            webbrowser.open(url)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down LANDIS-II simulation server...")
    except Exception as e:
        print(f"Server notice: {e}")
        webbrowser.open(url)

if __name__ == "__main__":
    run_server()
