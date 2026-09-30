from flask import Flask
from flask_cors import CORS

from app.routes.auth import auth_bp


def create_app():
    app = Flask(__name__)

    CORS(app)

    app.register_blueprint(auth_bp)

    @app.get("/health")
    def health_check():
        return {
            "status": "ok",
            "service": "taskflow-api"
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)