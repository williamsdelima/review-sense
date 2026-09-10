import os


class Config:

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "c6a13df44d13eadab7e86a0c5910e8e428cd4ea93e30a980a3d121b080e3733a")
    BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")
    BACKEND_API_TIMEOUT_SECONDS = int(os.environ.get("BACKEND_API_TIMEOUT_SECONDS", 30))
