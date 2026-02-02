import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Gemini AI Settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
    GEMINI_MAX_TOKENS = int(os.environ.get('GEMINI_MAX_TOKENS', 1024))
    GEMINI_TEMPERATURE = float(os.environ.get('GEMINI_TEMPERATURE', 0.7))
    GEMINI_CONTEXT_WINDOW = int(os.environ.get('GEMINI_CONTEXT_WINDOW', 50))
    GEMINI_RATE_LIMIT_DELAY = float(os.environ.get('GEMINI_RATE_LIMIT_DELAY', 1.0))

    # Room settings
    ROOM_TIMEOUT_HOURS = 2
    RECONNECT_WINDOW_MINUTES = 5
    EXPORT_WINDOW_MINUTES = 10

    # Cleanup interval (seconds)
    CLEANUP_INTERVAL = 300  # 5 minutes

    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    GEMINI_API_KEY = 'test-key'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
