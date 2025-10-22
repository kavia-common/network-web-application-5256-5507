import os
import logging
from flask import Flask, jsonify, send_from_directory, request
from flask_restful import Api, Resource
from flask_cors import CORS

from .config import get_config
from .utils.responses import success, error
from .utils.logging_config import configure_logging
from .services.db import ensure_indexes
from .services.scheduler import init_scheduler, shutdown_scheduler


def create_app() -> Flask:
    """Create and configure the Flask application instance.

    This configures:
    - CORS for /api/* routes
    - Flask-RESTful API under /api
    - Static serving of the React app from ../frontend/build
    - SPA catch-all to return index.html for client-side routing
    - Background scheduler lifecycle hooks
    """
    # Configure logging early
    configure_logging()

    # Resolve static folder path (frontend build at ../frontend/build)
    # backend/app.py -> base_dir is the container root (NetworkWebApplication)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    static_folder = os.path.join(base_dir, "frontend", "build")

    # Create app; allow missing build folder (dev-backend only)
    app = Flask(
        __name__,
        static_folder=static_folder if os.path.isdir(static_folder) else None,
        static_url_path="/",  # serve assets at root (e.g., /static/js/main.js resolved from build)
    )

    # Load config
    cfg = get_config()
    app.config["APP_CFG"] = cfg

    # Enable CORS for API routes only; do not affect static file responses
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize API with prefix /api
    api = Api(app, prefix="/api")

    # Initialize database indexes at startup
    try:
        ensure_indexes()
    except Exception as db_exc:
        logging.getLogger(__name__).error("Failed to ensure DB indexes: %s", db_exc)

    # Start background scheduler if enabled
    try:
        init_scheduler()
    except Exception as sched_exc:
        logging.getLogger(__name__).error("Failed to initialize scheduler: %s", sched_exc)

    # Ensure graceful shutdown of scheduler on app teardown
    @app.teardown_appcontext
    def _teardown_scheduler(exception):  # noqa: ARG001
        try:
            shutdown_scheduler()
        except Exception as exc:
            logging.getLogger(__name__).warning("Error during scheduler teardown: %s", exc)

    # Health resource (minimal placeholder)
    class HealthResource(Resource):
        """Simple health check endpoint that returns ok."""
        # PUBLIC_INTERFACE
        def get(self):
            return jsonify(success({"uptime": True, "ping_enabled": cfg.PING_ENABLED}))

    # Register resources (more will be added later)
    api.add_resource(HealthResource, "/health", endpoint="health")

    # Devices resources
    from .resources.devices import DevicesListResource, DeviceResource  # Import here to avoid circulars at module load
    api.add_resource(DevicesListResource, "/devices", endpoint="devices_list")
    api.add_resource(DeviceResource, "/devices/<string:device_id>", endpoint="device_detail")

    # Status resource (manual device status check)
    from .resources.status import DeviceStatusResource
    api.add_resource(
        DeviceStatusResource,
        "/devices/<string:device_id>/status",
        endpoint="device_status",
    )

    # Serve static assets from the React build directory if present
    @app.route("/assets/<path:filename>")
    def serve_static_assets(filename: str):
        """Serve static assets from the React build folder's assets path if present."""
        if app.static_folder and os.path.isdir(app.static_folder):
            asset_path = os.path.join(app.static_folder, filename)
            if os.path.isfile(asset_path):
                return send_from_directory(app.static_folder, filename)
        return jsonify(error("Asset not found", code="ASSET_NOT_FOUND")), 404

    # SPA index and catch-all: serve index.html for root and unrecognized non-API paths
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react_app(path: str):
        """Serve the React build if available; otherwise provide a helpful message.

        - If a specific static file is requested and exists, serve it
        - For any other non-API path, serve index.html (client-side routing)
        - If build folder is missing, return a JSON helper with API health link
        """
        # Do not intercept API endpoints
        if path.startswith("api"):
            return jsonify(error("Endpoint not found", code="NOT_FOUND")), 404

        if app.static_folder and os.path.isdir(app.static_folder):
            # If the requested file exists within the build folder, serve it as-is
            file_path = os.path.join(app.static_folder, path)
            if path and os.path.isfile(file_path):
                return send_from_directory(app.static_folder, path)

            # Otherwise serve index.html (SPA routing)
            index_path = os.path.join(app.static_folder, "index.html")
            if os.path.isfile(index_path):
                return send_from_directory(app.static_folder, "index.html")

        # Fallback message when frontend build is not present
        return jsonify(
            success(
                {
                    "message": "Frontend build not found. API is running.",
                    "api_health": request.host_url.rstrip("/") + "/api/health",
                }
            )
        )

    # Root API index helper (preserved)
    @app.route("/api", methods=["GET"])
    def api_index():
        """Basic API index with available starter routes."""
        return jsonify(
            success(
                {
                    "endpoints": [
                        {"method": "GET", "path": "/api/health", "description": "Health check"},
                        {"method": "GET", "path": "/api/devices", "description": "List devices"},
                        {"method": "POST", "path": "/api/devices", "description": "Create device"},
                        {"method": "GET", "path": "/api/devices/<id>", "description": "Get device by id"},
                        {"method": "PUT", "path": "/api/devices/<id>", "description": "Update device (full)"},
                        {"method": "PATCH", "path": "/api/devices/<id>", "description": "Update device (partial)"},
                        {"method": "DELETE", "path": "/api/devices/<id>", "description": "Delete device"},
                    ]
                }
            )
        )

    logging.getLogger(__name__).info("Application initialized; static at %s", app.static_folder)
    return app


# PUBLIC_INTERFACE
def run():
    """Run the Flask development server using configuration from environment variables."""
    app = create_app()
    cfg = app.config.get("APP_CFG")
    app.run(host="0.0.0.0", port=cfg.APP_PORT, debug=cfg.DEBUG)


if __name__ == "__main__":
    run()
