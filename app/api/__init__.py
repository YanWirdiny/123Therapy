from app.api.rooms import rooms_bp
from app.api.sessions import sessions_bp
from app.api.test_routes import test_bp
from app.api.pages import pages_bp

#Function to register the blueprints
def register_blueprints(app):
    app.register_blueprint(pages_bp)  # Frontend pages (must be first for '/')
    app.register_blueprint(rooms_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(test_bp)


__all__ = ['rooms_bp', 'sessions_bp', 'test_bp', 'pages_bp', 'register_blueprints']
