from flask import Flask , render_template, request, redirect, url_for, jsonify, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

@app.route('/')
def catalog():
	category = session.query(Category).all()
	items = session.query(Item).all()
	return render_template('catalog.html', category = category, items = items)

@app.route('/categories/<int:category_id>/', methods=['GET', 'POST'])
def items(category_id):
	# session.rollback()
	if request.method == "POST":
		newItem = Item(name=request.form['item-name'], description=request.form['item-description'], price=request.form['item-price'], company=request.form['item-company'], cat_id=category_id)
		session.add(newItem)
		session.commit()
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(Item).filter_by(cat_id = category_id)

	return render_template('items.html', category = category, items = items)

@app.route('/categories/<int:category_id>/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id,category_id):
	if request.method == "POST":
		toDelete = session.query(Item).filter_by(id = item_id).one()
		session.delete(toDelete)
		session.commit()
		return redirect(url_for('items', category_id=category_id))
	item = session.query(Item).filter_by(id=item_id).one()
	category = session.query(Category).filter_by(id=category_id).one()
	return render_template('delete.html', item = item, category = category)

@app.route('/categories/<int:category_id>/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id,category_id):
	if request.method == "POST":
		editedItem = session.query(Item).filter_by(id = item_id).one()
		editedItem.name = request.form['item-name']
		editedItem.description = request.form['item-description']
		editedItem.price = request.form['item-price']
		editedItem.company = request.form['item-company']
		session.add(editedItem)
		session.commit()
		return redirect(url_for('items', category_id = category_id))
	item = session.query(Item).filter_by(id=item_id).one()
	category = session.query(Category).filter_by(id=category_id).one()
	return render_template('edit.html', item = item, category = category)


@app.route('/categories/<int:category_id>/JSON')
def catalogJSON(category_id):
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(Item).filter_by(cat_id = category_id).all()

	return jsonify(Items=[i.serialize for i in items])


@app.route('/categories/<int:category_id>/<int:item_id>/JSON/')
def itemJSON(category_id,item_id):
	item = session.query(Item).filter_by(id=item_id).one()

	return jsonify(Item=[item.serialize])

@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', state = state)

# @app.route('/gconnect', methods=['POST'])
# def gconnect():
# 	if request.args.get('state') != login_session['state']:
# 		response = make_response(json.dumps('Invalid state'), 401)
# 		response.headers['Content-Type'] = 'application/json'
# 		return response
# 	code = request.data
# 	try:
# 		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
# 		oauth_flow.redirect_uri = 'postmessage'
# 		credentials = oauth_flow.step2_exchange(code)
# 	except FlowExchangeError:
# 		response = make_response(json.dumps('Authorization code failed'), 401)
# 		response.headers['Content-Type'] = 'application/json'
# 		return response
# 	access_token = credentials.access_token
# 	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
# 	h = httplib2.Http()
# 	result = json.loads(h.request(url, 'GET')[1])
# 	if result.get('error') is not None:
# 		response = make_response(json.dumps(result.get('error')), 50)
# 		response.headers['Content-Type'] = 'application/json'
# 	gplus_id = credentials.id.token['sub']
# 	if result['user_id'] != gplus_id:
# 		response = make_response(json.dumps("Token doesn't match"), 401)
# 		response.headers['Content-Type'] = 'application/json'
# 		return response
# 	if result['issued_to'] != CLIENT_ID:
# 		response = make_response(json.dumps("Client ID doesn't match app's Client ID"), 401)
# 		response.headers['Content-Type'] = 'application/json'
# 		return response
# 	stored_credentials = login_session.get('credentials')
# 	stored_gplus_id = login_session.get('gplus_id')
# 	if stored_credentials is not None and gplus_id == stored_gplus_id:
# 		response = make_response(json.dumps('Already connected'), 200)
# 		response.headers['Content-Type'] = 'application/json'
#
# 	login_session['credentials'] = credentials
# 	login_session['gplus_id'] = gplus_id
#
# 	userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
# 	params = {'access_token': credentials.access_token, 'alt': 'json'}
# 	answer = requests.get(userinfo_url, params=params)
# 	data = json.loads(answer.text)
#
# 	login_session['username'] = data['name']
# 	login_session['picture'] = data['picture']
# 	login_session['email'] = data['email']
#
# 	output = ""
# 	output += "<h1>"
# 	output += "Ok you are logged in as" %login_session['username']
# 	output += "</h1>"
# 	output += login_session['picture']
# 	return output

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    print login_session['state']
    other_state = request.args.get('state')
    print other_state
    if request.args.get('state') != login_session['state']:
        print "error"
        response = make_response(json.dumps('Invalid state'), 401)
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
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

    data = json.loads(answer.text)

    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    print "working"
    flash("you are now logged in as %s" % login_session['email'])

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
