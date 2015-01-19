#!venv/bin/python
import random
import config
from monkeygod import create_app, models
from monkeygod.models import db


def clear_db():
    for monkey in models.Monkey.query:
        db.session.delete(monkey)
    db.session.commit()


def insert_data():
    monkeys = []
    for i in range(100):
        monkeys.append(
            models.Monkey(
                name='monkey{}'.format(i+1),
                age=random.randint(0, 99),
                email='monkey{}@example.com'.format(i+1)
            )
        )

    db.session.add_all(monkeys)
    db.session.commit()

    for monkey in monkeys:
        friends = random.sample(monkeys, random.randint(0, 100))
        for friend in friends:
            if random.randint(0, 5) == 0: #rolling a die..
                monkey.add_best_friend(friend)
            else:
                monkey.add_friend(friend)

    db.session.add_all(monkeys)
    db.session.commit()


if __name__ == '__main__':
    app = create_app(config)
    with app.app_context():
        print('Clearing data..')
        clear_db()
        print('Inserting test data..')
        insert_data()
        print('Done')
