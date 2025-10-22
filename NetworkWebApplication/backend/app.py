import os
import logging
from flask import Flask, jsonify, send_from_directory, request
from flask_restful import Api, Resource
from flask_cors import CORS

from .config import get_config
from .utils.responses import success, error
from .utils.logging_config import configure_logging
from .services.db import ensure_indexes


def create_app() -> Flask:
    """Create and configure the Flask application instance."""
    # Configure logging early
    configure_logging()

    # Resolve static folder path (frontend build)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    static_folder = os.path.join(base_dir, "frontend", "build")
    template_folder = static_folder  # index.html lives in build

    # Create app with static setup; tolerate missing folder
    app = Flask(
        __name__,
        static_folder=static_folder if os.path.isdir(static_folder) else None,
        template_folder=template_folder if os.path.isdir(template_folder) else None,
    )

    # Load config
    cfg = get_config()
    app.config["APP_CFG"] = cfg

    # Enable CORS (optional, can be restricted later)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize API with prefix /api
    api = Api(app, prefix="/api")

    # Initialize database indexes at startup
    try:
        ensure_indexes()
    except Exception as db_exc:
        # Log the exception; app can still run, but DB operations may fail without proper config.
        logging.getLogger(__name__).error("Failed to ensure DB indexes: %s", db_exc)

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

    # Static file serving
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react_app(path: str):
        """Serve the React build if available; otherwise provide a helpful message."""
        if app.static_folder and os.path.isdir(app.static_folder):
            # If the requested file exists, serve it
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

    # Root API index helper
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
