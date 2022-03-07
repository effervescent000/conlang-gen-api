from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
cors = CORS()


def create_app():
    app = Flask(__name__)

    cors.init_app(app)

    with app.app_context():

        from . import routes

        app.register_blueprint(routes.bp)

        return app
