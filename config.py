import os
basedir = os.path.abspath(os.path.dirname(__file__))

HEROKU = os.environ.get('HEROKU') is not None

SQLALCHEMY_DATABASE_URI = (
     os.environ.get('DATABASE_URL') or
     'postgresql://postgres:postgres@localhost/monkeysdb'
)

WTF_CSRF_ENABLED = True
SECRET_KEY = 'why-would-i-tell-you-that?'

MONKEYS_PER_PAGE = 10

DEBUG = not HEROKU
