import logging
from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS

from .config import get_config
from .utils.responses import success
from .utils.logging_config import configure_logging
from .services.db import ensure_indexes
from .services.scheduler import init_scheduler, shutdown_scheduler


def create_app() -> Flask:
    """Create and configure the Flask application instance.

    This configures:
    - Flask-RESTful API under /api
    - CORS for /api/* routes with configurable origins
    - Background scheduler lifecycle hooks
    """
    # Configure logging early
    configure_logging()

    # Create app (no static folder: frontend is served separately)
    app = Flask(__name__)

    # Load config
    cfg = get_config()
    app.config["APP_CFG"] = cfg

    # Enable CORS for API routes only; allow configurable origins via env FRONTEND_ORIGIN (default "*")
    # Keep permissive for development by default.
    cors_origins = "*"
    try:
        # Try to read an optional FRONTEND_ORIGIN value from environment via config if later added
        # For now, allow override via FLASK_CORS_ORIGINS env read by flask-cors when set.
        # If project later adds FRONTEND_ORIGIN to config.py, this can be wired here.
        pass
    finally:
        CORS(app, resources={r"/api/*": {"origins": cors_origins}})

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

    # Register resources
    api.add_resource(HealthResource, "/health", endpoint="health")

    # Devices resources
    from .resources.devices import DevicesListResource, DeviceResource
    api.add_resource(DevicesListResource, "/devices", endpoint="devices_list")
    api.add_resource(DeviceResource, "/devices/<string:device_id>", endpoint="device_detail")

    # Status resource (manual device status check)
    from .resources.status import DeviceStatusResource
    api.add_resource(
        DeviceStatusResource,
        "/devices/<string:device_id>/status",
        endpoint="device_status",
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

    logging.getLogger(__name__).info("Application initialized (no static serving enabled).")
    return app


# PUBLIC_INTERFACE
def run():
    """Run the Flask development server using configuration from environment variables."""
    app = create_app()
    cfg = app.config.get("APP_CFG")
    app.run(host="0.0.0.0", port=cfg.APP_PORT, debug=cfg.DEBUG)


if __name__ == "__main__":
    run()
