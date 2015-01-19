#!venv/bin/python
import config
from monkeygod import create_app, models
from monkeygod.models import db


def drop_db():
    db.drop_all(bind=None)


if __name__ == '__main__':
    app = create_app(config)
    with app.app_context():
        print('Dropping previous tables..')
        drop_db()
        print('Done')
