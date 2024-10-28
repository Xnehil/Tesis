# app.py
from flask import Flask
from config import Config
from models import db
from api import api  # Import the api blueprint
from web import web  # Import the web blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize the database with the app
    db.init_app(app)
    
    # Register the blueprints
    app.register_blueprint(api)  # API routes with /api prefix
    app.register_blueprint(web)  # Webpage routes without prefix

    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
