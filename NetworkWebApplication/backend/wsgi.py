from .app import create_app

# PUBLIC_INTERFACE
def application():
    """WSGI application factory for servers like gunicorn/uwsgi."""
    return create_app()

# For servers expecting a module-level 'app' callable
app = create_app()
