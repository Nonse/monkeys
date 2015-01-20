from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    from monkeygod.models import db
    db.init_app(app)
    Bootstrap(app)

    from monkeygod.views import monkey_views
    app.register_blueprint(monkey_views)

    return app
