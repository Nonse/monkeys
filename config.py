import os
basedir = os.path.abspath(os.path.dirname(__file__))


SQLALCHEMY_DATABASE_URI = (
    'postgresql://postgres:postgres@localhost/monkeysdb'
)

WTF_CSRF_ENABLED = True
SECRET_KEY = 'why-would-i-tell-you-that?'
