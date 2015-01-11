#!venv/bin/python
from app import db

print('Creating database..')
db.create_all()
print('Done')
