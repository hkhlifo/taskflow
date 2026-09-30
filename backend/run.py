from flask import Flask
from flask_cors import CORS

from app.routes.auth import auth_bp
from app.routes.tasks import tasks_bp
from app.routes.users import users_bp


app = Flask(__name__)

CORS(app)


app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(users_bp)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)