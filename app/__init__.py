# App factory - will be implemented in Step 10
import os
from flask import Flask

from .config import config
from .extensions import socketio, cors
from .websocket.events import register_events
from .api import register_blueprints


def create_app(config_name='development'):
    # Get the project root directory (parent of app/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, 'templates'),
        static_folder=os.path.join(project_root, 'static')
    )
    app.config.from_object(config[config_name])
    socketio.init_app(app, cors_allowed_origins=app.config['CORS_ORIGINS'])
    cors.init_app(app)
    register_events(app)
    register_blueprints(app)
    return app