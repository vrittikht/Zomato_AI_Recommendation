import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8081
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "src" / "frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

def main():
    os.chdir(FRONTEND_DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Frontend available at http://localhost:{PORT}")
        print("💡 Make sure the Backend API (Phase 7) is running on port 8000!")
        webbrowser.open(f"http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
