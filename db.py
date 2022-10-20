from flask import g
import sqlite3
from werkzeug.security import generate_password_hash


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('database.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e):
    if 'db' in g:
        g.db.close()
        g.pop('db', None)

def init_db():
    db = get_db()
    db.execute('DROP TABLE IF EXISTS users')
    db.execute('DROP TABLE IF EXISTS items')
    db.execute('DROP TABLE IF EXISTS listings')
    db.execute('CREATE TABLE users (username TEXT UNIQUE NOT NULL, balance INTEGER DEFAULT 100 NOT NULL, password TEXT NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT)')
    db.execute('CREATE TABLE items (name TEXT NOT NULL, price INTEGER NOT NULL, description TEXT NOT NULL, image_ref TEXT NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER NOT NULL, FOREIGN KEY (owner_id) REFERENCES users (id))')
    db.execute('CREATE TABLE listings (listing_id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER NOT NULL, FOREIGN KEY (item_id) REFERENCES items (id))')

def register_admin():
    db = get_db()
    db.execute('INSERT INTO users (username, password, id) VALUES ("admin", ?, 0)', (generate_password_hash("1234"),))
    db.commit()

def create_admin_listings():
    animals = ['dog', 'cat', 'elephant', 'cheetah', 'lion', 'kangaroo', 'monkey', 'fish', 'pig', 'cow', 'horse', 'chicken', 'shark', 'bird']
    prices = [20, 20, 80, 150, 300, 30, 100, 10, 10, 10, 50, 5, 200, 40]
    descriptions = ["The dog is a sturdy and reliable animal. They are known for being taken on walks and barking excessively at late hours.", "The cat is a feline in name only. While highly independent, the cat will inevitably return to your house when needing to urinate.", "The elephant while large and cuddly, serves a dual purpose as a water hose. Its trunk, while unwieldy at first glance, is quite versatile.", "The cheetah, the fastest land animal, is surprisingly skittish due to its compromise of strength in acquisition of speed. While cuddling is not recommended, it is possible.", "The lion aka the king of the jungle, is most commonly pictured laying around.", "The kangaroo is an odd cirtter (it is classified as a rodent in australia), while quite bouncy and equiped with quick access to storage, they are known to exhibit their boxing skills on the unprepared.", "The monkey, human's closest relative, are often found eating their own poop in the zoo.", "Fish, while very untasty, contain oils very beneficial for one's health.", "The pig, often called bacon, are actually rather intelligent (some say more intelligent than dogs). They are often fat shamed and thus get a bad reputation.", "The cow is a peaceful animal. So peaceful they often lollygag in the road as there is really no rush to cross it.", "A horse is quite confusing. They sleep standing, which is a trait often envied by humans. They are also quick, bumpy, and quite rude/hard to become friends with.", "The chicken is more capable than one might think from just looking. They are highly capable in combat and should thus be treated with respect.", "The shark, a rare sea-creature, is about as hungry for you as you are for them. In other words, it depends on the shark.", "The bird possesses one of superman's powers, and also the best one."]
    db = get_db()
    for i in range(len(animals)):
        db.execute('INSERT INTO items (name, price, description, image_ref, owner_id) VALUES (?, ?, ?, ?, ?)', (animals[i], prices[i], descriptions[i], f'{animals[i]}.jpg',0))
        db.execute('INSERT INTO listings (item_id) VALUES (?)', (i+1,))
    db.commit()