from flask import Flask, jsonify
from flask_cors import CORS
from flask_mail import Mail
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from config import ServigoConfig
from models import db, create_admin_user
from routes import routes, export_bp, customer_bp


load_dotenv()

app = Flask(__name__)

# Loading configuration from config class
app.config.from_object(ServigoConfig)

# Some extra mail settings for local testing
app.config["MAIL_DEBUG"] = True
app.config["MAIL_SUPPRESS_SEND"] = False

# JWT configuration 
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt_dev_fallback")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # no expiration during development


app.config["UPLOAD_FOLDER"] = "uploads"

# Initializing Flask extensions
db.init_app(app)
mail = Mail(app)
jwt = JWTManager(app)
cache = Cache(app)


CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)


app.register_blueprint(routes)
app.register_blueprint(export_bp)
app.register_blueprint(customer_bp)

# Seting up database and creating admin user
with app.app_context():
    try:
        db.create_all()
        create_admin_user()
        print(" Database and admin user setup completed.")
    except Exception as e:
        print("Failed to initialize database:", str(e))


@app.route("/", methods=["GET"])
def api_greetings():
    return jsonify({"message": "ServiGo API is up and running"})


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "This route does not exist."
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "error": "Unauthorized",
        "message": "You must be logged in to access this resource."
    }), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
