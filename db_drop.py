#!venv/bin/python
from app import db


print('Dropping previous tables..')
db.drop_all(bind=None)
