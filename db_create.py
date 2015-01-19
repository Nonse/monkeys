#!venv/bin/python
import config
from monkeygod import create_app, models
from monkeygod.models import db


def create_db():
    db.create_all()


if __name__ == '__main__':
    app = create_app(config)
    with app.app_context():
        print('Creating database..')
        create_db()
        print('Done')
