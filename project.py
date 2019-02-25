from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify, flash


# importing sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item

# importing flask
from flask import session as login_session
import random, string

# importing oauth libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# connecting the client secrets downloaded from google API
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Web client 1"

# creating engine object for the item catalog database
engine = create_engine('sqlite:///itemcatalog.db')

# binding the base class to the engine
Base.metadata.bind = engine

# creating sesion object
DBSession = sessionmaker(bind=engine)

session = DBSession()


# login route and its decorator function
@app.route('/login')
def showLogin():
    # creating a randonly generated state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    # assigning the state token as a property of the login_session object
    login_session['state'] = state
    print login_session['state']
    # rendering the login page
    return render_template('login.html', state=state)


# when user is routed to /gconnect, the decorator function runs
@app.route('/gconnect', methods=['POST', 'GET'])
def gconnect():
    # comparing server-generated state token with what was passed from url
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        print "state doesn't match"
        response.headers['Content-Type'] = 'application/json'
        return response
    # getting access token from the google authenticator
    code = request.data
    print code
    # establishing handshake between client and server
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print "credentials established"
    # if there's an error in the exchange
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print response
        return response
    # retreving the access token assigned to the credentials object
    access_token = credentials.access_token
    print "access token established"
    # putting access token in the url
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    # getting a result from the httplib2 library's GET method
    result = json.loads(h.request(url, 'GET')[1])
    # if an error exists in the get method
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        print response
        return response

    # getting user's google+ id
    gplus_id = credentials.id_token['sub']
    print "google + id assigned"
    # verifying the correct user is attempting to log in
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        print response
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        print response
        return response

    # storing the access token and google+ id
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    print "still working on line 151"
    # verifying the user isn't already logged in
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        print response
        return response

    print "still working on line 158"

    # assigning the access token and google+ id to login_session
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # making a json file
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = json.loads(answer.text)

    # capturing the user's picture and email
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # login is established
    print "working"
    flash("you are now logged in as %s" % login_session['email'])

    return "hi"


# decorator function when the url is /gdisconnect
@app.route("/gdisconnect")
def gdisconnect():
    # ensuring the login session ends
    del login_session['email']
    credentials = login_session.get('access_token')
    # in case the user is already logged out
    if credentials is None:
        response = make_response(json.dumps('User not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # revoking the access token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # if logout is successful, delete the user's info
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']

        response = make_response(json.dumps('now disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # if unsuccessful logout
    else:
        response = make_response(json.dumps('Unsuccessful revoke'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    logged_out = True
    return render_template('logging_out.html', logged_out=logged_out)


# the main screen
@app.route('/')
def catalog():
    # querying the database for the category table
    category = session.query(Category).all()
    # querying the database for the category table
    items = session.query(Item).all()
    # checking to see if user is logged in
    if 'email' not in login_session:
        print login_session.get('access_token')
        print 'nope not logged in'
        is_logged_in = False
    else:
        print 'yup you are logged in'
        is_logged_in = True
    return render_template(
                           'catalog.html',
                           category=category,
                           is_logged_in=is_logged_in,
                           items=items
                          )


# rendering the login page
@app.route('/login')
def login():
    return render_tempate('login.html')


# if user goes to category page to see its list of items
@app.route('/categories/<int:category_id>/', methods=['GET', 'POST'])
def items(category_id):
    # if user submits the form for a new item
    if request.method == "POST":
        # adding the new item to the database
        newItem = Item(
                       name=request.form['item-name'],
                       description=request.form['item-description'],
                       price=request.form['item-price'],
                       company=request.form['item-company'],
                       cat_id=category_id
                       )
        session.add(newItem)
        session.commit()
    # retrieving the specific category the user wants and its items
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(cat_id=category_id)
    # checking if user is logged in
    if 'email' not in login_session:
        print login_session.get('access_token')
        print 'nope'
        is_logged_in = False
    else:
        print 'yup'
        is_logged_in = True
    return render_template(
                           'items.html',
                           category=category,
                           is_logged_in=is_logged_in,
                           items=items
                           )


# function to delete items
@app.route('/categories/<int:category_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(item_id, category_id):
    if request.method == "POST":
        toDelete = session.query(Item).filter_by(id=item_id).one()
        session.delete(toDelete)
        session.commit()
        return redirect(url_for('items', category_id=category_id))
    item = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    return render_template('delete.html', item=item, category=category)


# function to edit items
@app.route('/categories/<int:category_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(item_id, category_id):
    if request.method == "POST":
        editedItem = session.query(Item).filter_by(id=item_id).one()
        editedItem.name = request.form['item-name']
        editedItem.description = request.form['item-description']
        editedItem.price = request.form['item-price']
        editedItem.company = request.form['item-company']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('items', category_id=category_id))
    item = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    return render_template('edit.html', item=item, category=category)


# creating JSON endpoint for categories
@app.route('/categories/<int:category_id>/JSON')
def catalogJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(cat_id=category_id).all()

    return jsonify(Items=[i.serialize for i in items])


# creating JSON endpoint for items in a requested category
@app.route('/categories/<int:category_id>/<int:item_id>/JSON/')
def itemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()

    return jsonify(Item=[item.serialize])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
