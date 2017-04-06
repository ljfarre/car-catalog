from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Dealership, Car, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Classic Car Dealership Catalog"


# Connect to Database and create database session
engine = create_engine('sqlite:///cardealerships.db')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['name']
        del session['picture']
        del session['email']
        del session['user_id']
        return redirect(url_for('showDealerships'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# JSON APIs to view all Dealerships in the catalog
@app.route('/dealership/JSON')
def dealershipsJSON():
    dealerships = session.query(Dealership).all()
    return jsonify(dealerships=[r.serialize for r in dealerships])


# JSON APIs to view a Dealership's inventory of cars
@app.route('/dealership/<int:dealership_id>/inventory/JSON')
def dealershipInventoryJSON(dealership_id):
    dealership = session.query(Dealership).filter_by(id=dealership_id).one()
    cars = session.query(Car).filter_by(dealership_id=dealership_id).all()
    return jsonify(cars=[i.serialize for i in cars])


# JSON APIs to view all coupes in catalog
@app.route('/coupes/JSON')
def allCoupesJSON():
    cars = session.query(Car).filter_by(type="Coupe").all()
    return jsonify(cars=[i.serialize for i in cars])


# JSON APIs to view all sedans in catalog
@app.route('/sedans/JSON')
def allSedansJSON():
    cars = session.query(Car).filter_by(type="Sedan").all()
    return jsonify(cars=[i.serialize for i in cars])


# JSON APIs to view all sports cars in catalog
@app.route('/sportscars/JSON')
def allSportscarsJSON():
    cars = session.query(Car).filter_by(type="Sports Car").all()
    return jsonify(cars=[i.serialize for i in cars])


# JSON APIs to view all trucks in catalog
@app.route('/trucks/JSON')
def allTrucksJSON():
    cars = session.query(Car).filter_by(type="Truck").all()
    return jsonify(cars=[i.serialize for i in cars])


# JSON APIs to view all trucks in catalog
@app.route('/allcars/JSON')
def allCarsJSON():
    cars = session.query(Car).all()
    return jsonify(cars=[i.serialize for i in cars])


# Show all dealerships
@app.route('/')
@app.route('/dealership/')
def showDealerships():
    dealerships = session.query(Dealership).order_by(asc(Dealership.name))
    if 'username' not in login_session:
        return render_template('publicdealerships.html', dealerships=dealerships)
    else:
        return render_template('dealerships.html', dealerships=dealerships)


# Create a new dealership
@app.route('/dealership/new/', methods=['GET', 'POST'])
def newDealership():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newDealership = Dealership(name=request.form['name'],
                                   address=request.form['address'],
                                   phone=request.form['phone'],
                                   user_id=login_session['user_id'])
        session.add(newDealership)
        session.commit()
        flash('New Dealership %s Successfully Created' % newDealership.name)
        return redirect(url_for('showDealerships'))
    else:
        return render_template('newdealership.html')


# Edit a dealership
@app.route('/dealership/<int:dealership_id>/edit/', methods=['GET', 'POST'])
def editDealership(dealership_id):
    editedDealership = session.query(
        Dealership).filter_by(id=dealership_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedDealership.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this dealership. Please create your own dealership in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedDealership.name = request.form['name']
        if request.form['address']:
            editedDealership.address = request.form['address']
        if request.form['phone']:
            editedDealership.phone = request.form['phone']
        session.add(editedDealership)
        session.commit()
        flash('Dealership Successfully Edited %s' % editedDealership.name)
        return redirect(url_for('showDealerships'))
    else:
        return render_template('editdealership.html', dealership=editedDealership)


# Delete a dealership
@app.route('/dealership/<int:dealership_id>/delete/', methods=['GET', 'POST'])
def deleteDealership(dealership_id):
    dealershipToDelete = session.query(
        Dealership).filter_by(id=dealership_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if dealershipToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this dealership. Please create your own dealership in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(dealershipToDelete)
        session.commit()
        flash('%s Successfully Deleted' % dealershipToDelete.name)
        return redirect(url_for('showDealerships', dealership_id=dealership_id))
    else:
        return render_template('deletedealership.html', dealership=dealershipToDelete)


# Show a dealership inventory
@app.route('/dealership/<int:dealership_id>/')
@app.route('/dealership/<int:dealership_id>/inventory/')
def showInventory(dealership_id):
    dealership = session.query(Dealership).filter_by(id=dealership_id).one()
    creator = getUserInfo(dealership.user_id)
    cars = session.query(Car).filter_by(dealership_id=dealership_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicinventory.html', cars=cars, dealership=dealership, creator=creator)
    else:
        return render_template('inventory.html', cars=cars, dealership=dealership, creator=creator)


# Create a new car record in dealership inventory
@app.route('/dealership/<int:dealership_id>/inventory/new/', methods=['GET', 'POST'])
def newCar(dealership_id):
    if 'username' not in login_session:
        return redirect('/login')
    dealership = session.query(Dealership).filter_by(id=dealership_id).one()
    if login_session['user_id'] != dealership.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add inventory items to this dealership. Please create your own dealership in order to add cars.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newCar = Car(name=request.form['name'],
                     brand=request.form['brand'],
                     year=request.form['year'],
                     color=request.form['color'],
                     description=request.form['description'],
                     price=request.form['price'],
                     type=request.form['type'],
                     dealership_id=dealership_id,
                     user_id=dealership.user_id)
        if newCar.name != []:
            session.add(newCar)
            session.commit()
            flash('New %s Car Successfully Created' % (newCar.name))
            return redirect(url_for('showInventory', dealership_id=dealership_id))
        else:
            return render_template('newcar.html', dealership_id=dealership_id)
    else:
        return render_template('newcar.html', dealership_id=dealership_id)


# Edit an car details
@app.route('/dealership/<int:dealership_id>/inventory/<int:inventory_id>/edit', methods=['GET', 'POST'])
def editCar(dealership_id, inventory_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCar = session.query(Car).filter_by(id=inventory_id).one()
    dealership = session.query(Dealership).filter_by(id=dealership_id).one()
    if login_session['user_id'] != dealership.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit inventory items for this dealership. Please create your own dealership in order to edit cars.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCar.name = request.form['name']
        if request.form['brand']:
            editedCar.brand = request.form['brand']
        if request.form['year']:
            editedCar.year = request.form['year']
        if request.form['color']:
            editedCar.color = request.form['color']
        if request.form['description']:
            editedCar.description = request.form['description']
        if request.form['price']:
            editedCar.price = request.form['price']
        if request.form['type']:
            editedCar.type = request.form['type']
        flash('Car Data Successfully Edited')
        session.add(editedCar)
        session.commit()
        return redirect(url_for('showInventory', dealership_id=dealership_id))
    else:
        return render_template('editcar.html', dealership_id=dealership_id, inventory_id=inventory_id, car=editedCar)


# Delete a car from dealerhip inventory
@app.route('/dealership/<int:dealership_id>/inventory/<int:inventory_id>/delete', methods=['GET', 'POST'])
def deleteCar(dealership_id, inventory_id):
    if 'username' not in login_session:
        return redirect('/login')
    dealership = session.query(Dealership).filter_by(id=dealership_id).one()
    carToDelete = session.query(Car).filter_by(id=inventory_id).one()
    if login_session['user_id'] != dealership.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete inventory cars to this dealership. Please create your own dealership in order to delete cars.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(carToDelete)
        session.commit()
        flash('Car Successfully Deleted')
        return redirect(url_for('showInventory', dealership_id=dealership_id))
    else:
        return render_template('deletecar.html', car=carToDelete)


# Show all available sedans
@app.route('/sedans/')
def showSedans():
    cars = session.query(Car).all()
    return render_template('sedans.html', cars=cars)


# Show all available coupes
@app.route('/coupes/')
def showCoupes():
    cars = session.query(Car).all()
    return render_template('coupes.html', cars=cars)


# Show all available sports cars
@app.route('/sportscars/')
def showSportscars():
    cars = session.query(Car).all()
    return render_template('sportscars.html', cars=cars)


# Show all available trucks
@app.route('/trucks/')
def showTrucks():
    cars = session.query(Car).all()
    return render_template('trucks.html', cars=cars)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showDealerships'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showDealerships'))


if __name__ == '__main__':
    app.secret_key = 'lees_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
