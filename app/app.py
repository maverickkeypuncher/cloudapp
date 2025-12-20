from flask import Flask
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.provider_routes import provider_bp

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET_KEY"

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(provider_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
