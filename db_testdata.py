#!venv/bin/python
import random
from app import db, models


def clear_db():
    monkeys = models.Monkey.query.all()
    for monkey in monkeys:
        db.session.delete(monkey)
        db.session.commit()


def insert_data():
    monkeys = []
    for i in range(100):
        monkeys.append(
            models.Monkey(
                name='monkey{}'.format(i+1),
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
    print('Clearing data..')
    clear_db()
    print('Inserting test data..')
    insert_data()
    print('Done')
