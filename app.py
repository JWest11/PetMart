from operator import truediv
from flask import Flask, render_template, request, g, get_flashed_messages, flash, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import click
import sqlite3
from db import init_db, close_db, get_db, register_admin, create_admin_listings

app = Flask(__name__)
app.secret_key = '1234'


    
@app.cli.command('init-db')
def init_db_command():
    init_db()
    click.echo('DB initialized')

@app.cli.command('register-admin')
def register_admin_command():
    register_admin()
    click.echo('admin registered')

@app.cli.command('create-admin-listings')
def create_admin_listings_command():
    create_admin_listings()
    click.echo('admin listings created')

@app.cli.command('init-db-full')
def full_db_init_command():
    init_db()
    register_admin()
    create_admin_listings()
    click.echo('db and admin initialized')


app.teardown_appcontext(close_db)
app.cli.add_command(init_db_command)
app.cli.add_command(register_admin_command)
app.cli.add_command(create_admin_listings_command)
app.cli.add_command(full_db_init_command)

@app.route('/')
def index():
    db = get_db()
    listings = db.execute('SELECT * FROM listings').fetchall()
    listingData = []
    for listing in listings:
        item_id = listing['item_id']
        listingData.append(db.execute(f'SELECT * FROM items WHERE id == {item_id} ').fetchone())
    
    return render_template('index.html', session = session, listings = listings, listingData = listingData)

@app.route('/shop', methods=['POST', 'GET'])
def shop():
    db = get_db()
    listings = db.execute('SELECT * FROM listings').fetchall()
    listingData = []
    print(listings)
    for listing in listings:
        item_id = listing['item_id']
        listingData.append(db.execute(f'SELECT * FROM items WHERE id == {item_id}').fetchone())
    
    if request.method == 'POST':
        if 'priceLow' in request.form:
            swap = True
            p1 = 0
            p2 = 1
            while swap:
                swap = False
                while p2 < len(listingData):
                    if int(listingData[p1]['price']) > int(listingData[p2]['price']):
                        listingData[p1], listingData[p2] = listingData[p2], listingData[p1]
                        swap = True
                    p1 += 1
                    p2 += 1
                p1 = 0
                p2 = 1
            newListingData = listingData
            newListings = []
            for listing in newListingData:
                item_id = listing['id']
                newListings.append(db.execute(f'SELECT * FROM listings WHERE item_id == {item_id}').fetchone())          
        elif 'priceHigh' in request.form:
            swap = True
            p1 = 0
            p2 = 1
            while swap:
                swap = False
                while p2 < len(listingData):
                    if int(listingData[p1]['price']) > int(listingData[p2]['price']):
                        listingData[p1], listingData[p2] = listingData[p2], listingData[p1]
                        swap = True
                    p1 += 1
                    p2 += 1
                p1 = 0
                p2 = 1
            newListingData = listingData
            newListings = []
            for listing in newListingData:
                item_id = listing['id']
                newListings.append(db.execute(f'SELECT * FROM listings WHERE item_id == {item_id}').fetchone())  
            newListingData, newListings = newListingData[::-1], newListings[::-1]
        elif 'name' in request.form:
            swap = True
            p1 = 0
            p2 = 1
            while swap:
                swap = False
                while p2 < len(listingData):
                    if ord(listingData[p1]['name'][0]) > ord(listingData[p2]['name'][0]):
                        listingData[p1], listingData[p2] = listingData[p2], listingData[p1]
                        swap = True
                    p1 += 1
                    p2 += 1
                p1 = 0
                p2 = 1
            newListingData = listingData
            newListings = []
            for listing in newListingData:
                item_id = listing['id']
                newListings.append(db.execute(f'SELECT * FROM listings WHERE item_id == {item_id}').fetchone())
        elif 'recent' in request.form:
            newListings, newListingData = listings[::-1], listingData[::-1]

        return render_template('shop.html', session = session, listings = newListings, listingData = newListingData)

    else:
        return render_template('shop.html', session = session, listings = listings, listingData = listingData)
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['newUsername']
        password = request.form['newPassword']

        if not username or not password:
            error = 'username and password required'
        
        if not error:
            try:
                db = get_db()
                db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, generate_password_hash(password)),)
                db.commit()
                session.clear()
                flash(f'successfully registered new user {username}')
                return redirect(url_for('login'))
            except db.IntegrityError:
                error = 'username taken'

    return render_template('register.html', error = error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            error = 'Please enter your username and password'
        
        if not error:
            db = get_db()
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user == None:
                error = 'Invalid Username'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect Password'
            else:
                session.clear()
                session['username'] = username
                session['userId'] = user['id']
                session['balance'] = user['balance']
                flash(f'Logged in as user: {username}')
                return redirect(url_for('shop'))
            

    return render_template('login.html', error = error)

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    db = get_db()
    if request.method == 'POST':
        item_id = request.form['id']
        if 'removeListing' in request.form:
            db.execute('DELETE FROM listings WHERE item_id = ?', (item_id,))
        elif 'createListing' in request.form:
            db.execute('INSERT INTO listings (item_id) VALUES (?)', (item_id,))
        db.commit()

    user_id = session['userId']
    items = db.execute(f'SELECT * FROM items WHERE owner_id == {user_id}').fetchall()
    unlisted_items = []
    listed_items = []
    for item in items:
        item_id = item['id']
        listing = db.execute(f'SELECT * FROM listings WHERE item_id == {item_id}').fetchone()
        if listing:
            listed_items.append(item)
        else:
            unlisted_items.append(item)
    print(unlisted_items)
    
    return render_template('sell.html', session = session, listed_items = listed_items, unlisted_items = unlisted_items)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        if 'addFunds' in request.form:
            userId = session['userId']
            currentFunds = db.execute(f'SELECT balance from users WHERE id == {userId}').fetchone()['balance']
            currentFunds += 100
            db.execute(f'UPDATE users SET balance = {currentFunds} WHERE id == {userId}')
            session['balance'] += 100
        db.commit()
    listings = db.execute('SELECT * FROM listings').fetchall()
    listingData = []
    print(listings)
    for listing in listings:
        item_id = listing['item_id']
        listingData.append(db.execute(f'SELECT * FROM items WHERE id == {item_id}').fetchone())
    
    return render_template('checkout.html', session = session, listings = listings, listingData = listingData)

@app.route('/account', methods=['GET', 'POST'])
def account():
    db = get_db()
    if request.method == 'POST':
        if 'removeListing' in request.form:
            item_id = request.form['id']
            db.execute('DELETE FROM listings WHERE item_id = ?', (item_id,))
        elif 'createListing' in request.form:
            item_id = request.form['id']
            db.execute('INSERT INTO listings (item_id) VALUES (?)', (item_id,))
        elif 'addFunds' in request.form:
            userId = session['userId']
            currentFunds = db.execute(f'SELECT balance from users WHERE id == {userId}').fetchone()['balance']
            currentFunds += 100
            db.execute(f'UPDATE users SET balance = {currentFunds} WHERE id == {userId}')
        db.commit()

    
    user_id = session['userId']
    userData = db.execute(f'SELECT * FROM users WHERE id == {user_id}').fetchone()
    session['balance'] = userData['balance']
    items = db.execute(f'SELECT * FROM items WHERE owner_id == {user_id}').fetchall()
    unlisted_items = []
    listed_items = []
    for item in items:
        item_id = item['id']
        listing = db.execute(f'SELECT * FROM listings WHERE item_id == {item_id}').fetchone()
        if listing:
            listed_items.append(item)
        else:
            unlisted_items.append(item)
    
    return render_template('account.html', session = session, listed_items = listed_items, unlisted_items = unlisted_items)

@app.route('/logout')
def logout():
    session.clear()
    
    return redirect(url_for('index'))

@app.route('/completePurchase', methods = ['GET','POST'])
def completePurchase():
    if request.method == 'POST':
        userId = session['userId']
        db = get_db()
        
        listingIds = request.get_json(force=True)['listingIds']
        print(listingIds)
        for id in listingIds:
            currentUser = db.execute(f'SELECT * FROM users WHERE id == {userId}').fetchone()
            currentUserBalance = currentUser['balance']
            listing = db.execute(f'SELECT * FROM listings WHERE listing_id == {id}').fetchone()
            itemId = listing['item_id']
            item = db.execute(f'SELECT * FROM items WHERE id == {itemId}').fetchone()
            currentUserBalance -= item['price']
            db.execute(f'UPDATE users SET balance = {currentUserBalance} WHERE id == {userId}')
            db.commit()
            itemOwnerId = item['owner_id']
            itemOwner = db.execute(f'SELECT * FROM users WHERE id == {itemOwnerId}').fetchone()
            itemOwnerNewBalance = itemOwner['balance'] + item['price']
            print(itemOwner['balance'], item['price'])
            print(itemOwnerNewBalance)
            db.execute(f'UPDATE users SET balance = {itemOwnerNewBalance} WHERE id == {itemOwnerId}')
            db.execute(f'UPDATE items SET owner_id = {userId} WHERE id == {itemId}')
            db.execute(f'DELETE FROM listings WHERE listing_id == {id}')
        db.commit()
        session['balance'] = currentUserBalance
    return ('')
