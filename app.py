from __future__ import annotations

import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from flask import Flask, send_from_directory, jsonify

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
RUNS_DIR = ROOT / "runs"
CACHE_DIR = ROOT / "data_layer" / ".cache"

# Ensure critical runtime directories exist on startup
os.makedirs(RUNS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    
    # Import and register API blueprint
    from api.routes import api
    from core_engine.landis_executor import is_landis_installed
    app.register_blueprint(api)

    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND, "index.html")

    @app.get("/health")
    @app.get("/api/health")
    def health_check():
        """Production health check endpoint for cloud load balancers and orchestrators."""
        landis_ready = is_landis_installed()
        return jsonify({
            "status": "healthy",
            "service": "LANDIS-II India Forest Landscape Decision Support & Intelligence Platform",
            "timestamp": datetime.now().isoformat(),
            "platform_os": sys.platform,
            "environment": "windows_workstation" if sys.platform.startswith("win") else "linux_cloud",
            "landis_engine_available": landis_ready,
            "scientific_core": "OPERATIONAL (FROZEN ARCHITECTURE)",
            "reduced_order_simulator": "OPERATIONAL"
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    url = f"http://127.0.0.1:{port}/"
    print("=" * 70)
    print("LANDIS-II Coupled India Forest Decision Support & Intelligence Platform")
    print(f"Scientific Workstation active on http://{host}:{port}/")
    print("=" * 70)
    
    # Open local browser only when explicitly running on local Windows desktop
    if sys.platform.startswith("win") and not os.environ.get("NO_BROWSER") and not os.environ.get("PORT"):
        try:
            webbrowser.open(url)
        except Exception:
            pass

    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)


