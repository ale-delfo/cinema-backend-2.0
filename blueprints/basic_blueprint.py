from flask import Blueprint, request, jsonify
from utils.authorizaton import authorization
from dbconnector import DatabaseConnector
from datetime import datetime
import logging
import configparser

bp = Blueprint('Basic Blueprint', __name__)

# ----------------------------------------------
# Importing configuration
# ----------------------------------------------

config = configparser.ConfigParser()
config.read('./config/basic_config.ini')
user = config['MYSQL']['user']
passw = config['MYSQL']['password']
host = config['MYSQL']['host']
defaultdb = config['MYSQL']['defaultdb']
environment = config['GENERAL']['environment']

if environment not in ['local', 'production']:
    raise Exception('Error in environment configuration, please check basic_config.ini')

# ------------------------------------------------------------------
# Utilities configuration
# ------------------------------------------------------------------

# Get main app logger
logger = logging.getLogger('apilogger')

# ------------------------------------------------------------------
# Defining routes associated to the blueprint  -  Cart Section
# ------------------------------------------------------------------


@bp.route('/api/cart/addproduct', methods=['POST'])
@authorization.login_required
def add_product_to_cart():
    uid = authorization.current_user()
    db = DatabaseConnector(user, passw, host, defaultdb)
    logger.info(f'User {uid} requested cart/add_product_to_cart api')
    productid = request.form.get('productId')
    response = dict()
    response['productId'] = productid
    try:
        # Check if there's a pending cart for the user
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # If not, create one and retrieve the ID
        if len(cartid) == 0:
            db.query(f'INSERT INTO cart (Customer_ID,status) VALUES (\'{uid}\',\'PENDING\')')
            uid = authorization.current_user()
            cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # Get numeric id from the query
        cartid = cartid[0][0]
        # Now we can insert the cart item
        # First check if there's already a record for that product
        item_id = db.query(f'SELECT Item_ID FROM cart_item WHERE Cart_ID={cartid} AND Product_ID={productid}')
        if len(item_id) == 0:
            db.query(f'INSERT INTO cart_item (Product_ID,Cart_ID) VALUES ({productid},{cartid})')
        else:
            item_id = item_id[0][0]
            db.query(f'UPDATE cart_item SET qty=qty+1 WHERE Item_ID={item_id}')
        response['status'] = 'success'
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
        response['status'] = 'fail'
    return response, 200

@bp.route('/api/cart/removeproduct', methods=['POST'])
@authorization.login_required
def remove_product_from_cart():
    uid = authorization.current_user()
    logger.info(f'User {uid} requested cart/remove_product_from_cart api')
    productid = request.form.get('productId')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = dict()
    response['productId'] = productid
    try:
        # Check if there's a pending cart for the user
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # If there is one, remove the requested item
        if len(cartid) != 0:
            cartid = cartid[0][0]
            logger.debug(f'Cart ID found: {cartid}')
            item = db.query(f'SELECT Item_ID, qty FROM cart_item WHERE Cart_ID={cartid} AND Product_ID={productid}')
            if len(item) != 0:
                item = item.pop(0)
                if item[1] == 1:
                    # There is only one of the product, delete the cart_item entry
                    db.query(f'DELETE FROM cart_item WHERE Item_ID={item[0]}')
                elif item[1] > 1:
                    db.query(f'UPDATE cart_item SET qty=qty-1 WHERE Item_ID={item[0]}')
                else:
                    raise BaseException("Error in quantity!")
        response['status'] = 'success'
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
        response['status'] = 'fail'
    return response, 200

@bp.route('/api/cart/removeallproduct', methods=['POST'])
@authorization.login_required
def remove_all_product_from_cart():
    uid = authorization.current_user()
    logger.info(f'User {uid} requested cart/removeallproduct api')
    productid = request.form.get('productId')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = dict()
    response['productId'] = productid
    try:
        # Check if there's a pending cart for the user
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # If there is one, remove the requested item
        if len(cartid) != 0:
            cartid = cartid[0][0]
            logger.debug(f'Cart ID found: {cartid}')
            item = db.query(f'SELECT Item_ID, qty FROM cart_item WHERE Cart_ID={cartid} AND Product_ID={productid}')
            if len(item) != 0:
                item = item.pop(0)
                db.query(f'DELETE FROM cart_item WHERE Item_ID={item[0]}')
        response['status'] = 'success'
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
        response['status'] = 'fail'
    return response, 200


@bp.route('/api/cart/emptycart', methods=['GET'])
@authorization.login_required
def empty_cart():
    uid = authorization.current_user()
    logger.info(f'User {uid} requested cart/empty_cart api')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = dict()
    try:
        # Check if there's a pending cart for the user
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # If there is one, remove the requested item
        if len(cartid) != 0:
            cartid = cartid[0][0]
            logger.debug(f'Cart ID found: {cartid}')
            db.query(f'DELETE FROM cart_item WHERE Cart_ID={cartid}')
        response['status'] = 'success'
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
        response['status'] = 'fail'
    return response, 200


@bp.route('/api/cart/getcart', methods=['GET'])
@authorization.login_required
def get_cart():
    uid = authorization.current_user()
    logger.info(f'User {uid} requested cart/get_cart api')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = []
    try:
        # Check if there's a pending cart for the user
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # If there is one, remove the requested item
        if len(cartid) != 0:
            cartid = cartid[0][0]
            logger.debug(f'Cart ID found: {cartid}')
            query = db.query(f'SELECT product.*, qty '
                             f'FROM '
                             f'(SELECT Product_ID,qty FROM cart_item WHERE Cart_ID = {cartid}) T '
                             f'JOIN product '
                             f'ON T.Product_ID = product.Product_ID')
            for food in query:
                food_dict = dict()
                food_dict['id'] = food[0]
                food_dict['title'] = food[1]
                food_dict['ingredients'] = food[2]
                food_dict['image'] = food[3]
                food_dict['price'] = food[4]
                food_dict['calories'] = food[5]
                food_dict['description'] = food[6]
                food_dict['size'] = food[7]
                food_dict['cat'] = food[8]
                food_dict['qty'] = food[9]
                response.append(food_dict)
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
    return jsonify(response), 200


@bp.route('/api/cart/getitemqty', methods=['POST'])
@authorization.login_required
def get_item_qty():
    uid = authorization.current_user()
    product_id = request.form.get('productId')
    logger.info(f'User {uid} requested /api/cart/getitemqty')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = dict()
    response['qty'] = 0
    try:
        # Check if there's a pending cart for the user
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # If there is one, remove the requested item
        if len(cartid) != 0:
            cartid = cartid[0][0]
            logger.debug(f'Cart ID found: {cartid}')
            query = db.query(f'SELECT qty FROM cart_item WHERE Cart_ID = {cartid} AND Product_ID={product_id}')
            if len(query) != 0 :
                response['qty'] = query.pop()[0]
        response['status'] = 'success'
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
        response['status'] = 'fail'
    return jsonify(response), 200

# ------------------------------------------------------------------
# Defining routes associated to the blueprint  -  Product Section
# ------------------------------------------------------------------


@bp.route('/api/product/getall', methods=['GET'])
@authorization.login_required
def get_all_food():
    uid = authorization.current_user()
    logger.info(f'User {uid} requested product/getall api')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = []
    try:
        for food in db.query('SELECT * FROM product'):
            food_dict = dict()
            food_dict['id'] = food[0]
            food_dict['title'] = food[1]
            food_dict['ingredients'] = food[2]
            food_dict['image'] = food[3]
            food_dict['price'] = food[4]
            food_dict['calories'] = food[5]
            food_dict['description'] = food[6]
            food_dict['size'] = food[7]
            food_dict['cat'] = food[8]
            response.append(food_dict)
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
        #response['status'] = 'fail'
    return jsonify(response), 200


@bp.route('/api/product/getdrinks', methods=['GET'])
@authorization.login_required
def get_all_drinks():
    uid = authorization.current_user()
    logger.info(f'User {uid} requested product/getall api')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = []
    try:
        for food in db.query('SELECT * FROM product WHERE cat = \'DRINK\''):
            food_dict = dict()
            food_dict['id'] = food[0]
            food_dict['title'] = food[1]
            food_dict['ingredients'] = food[2]
            food_dict['image'] = food[3]
            food_dict['price'] = food[4]
            food_dict['calories'] = food[5]
            food_dict['description'] = food[6]
            food_dict['size'] = food[7]
            food_dict['cat'] = food[8]
            response.append(food_dict)
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
        #response['status'] = 'fail'
    return jsonify(response), 200


# ------------------------------------------------------------------
# Defining routes associated to the blueprint  -  Ticket Section
# ------------------------------------------------------------------

@bp.route('/api/ticket/buyticket', methods=['POST'])
@authorization.login_required
def buy_ticket():
    uid = authorization.current_user()
    showid = request.form.get('show_id')
    logger.info(f'User {uid} requested ticket/buyticket api')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = dict()
    response['show_id'] = showid
    try:
        seatsAvailable = db.query(f'SELECT seatsAvailable FROM film_show WHERE Show_ID={showid}')
        if len(seatsAvailable) != 0:
            seatsAvailable = (seatsAvailable.pop())[0]
            logger.debug(f'Available seats: {seatsAvailable}')
            if seatsAvailable > 1:
                db.query(f'INSERT INTO ticket (Show_ID,Customer_ID,seat) VALUES ({showid},\'{uid}\',\'A00\')')
                db.query(f'UPDATE film_show SET seatsAvailable=seatsAvailable-1 WHERE Show_ID={showid}')
                response['status'] = 'success'
            else:
                response['status'] = 'fail'
        else:
            response['status'] = 'fail'
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
        response['status'] = 'fail'
    return jsonify(response), 200


@bp.route('/api/ticket/gettickets', methods=['GET'])
@authorization.login_required
def get_tickets():
    uid = authorization.current_user()
    logger.info(f'User {uid} requested ticket/gettickets api')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = []
    try:
        for ticket in db.query(f'SELECT Ticket_ID, showTime, Film_ID, seat, showRoom '
                               f'FROM ticket JOIN film_show ON ticket.Show_ID = film_show.Show_ID '
                               f'WHERE ticket.Customer_ID = \'{uid}\''):
            ticket_dict = dict()
            ticket_dict['Ticket_ID'] = ticket[0]
            ticket_dict['showTime'] = ticket[1]
            ticket_dict['Film_ID'] = ticket[2]
            ticket_dict['seat'] = ticket[3]
            ticket_dict['room'] = ticket[4]
            response.append(ticket_dict)
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logger.error(e)
    return jsonify(response), 200

# ------------------------------------------------------------------
# Defining routes associated to the blueprint  -  Order Section
# ------------------------------------------------------------------


@bp.route('/api/order/placeorder', methods=['POST'])
@authorization.login_required
def place_order():
    uid = authorization.current_user()
    ticket_id = request.form.get('ticket_id')
    logger.info(f'User {uid} requested the order/placeorder api')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = dict()
    response['ticket_id'] = ticket_id
    try:
        # Look for the pending cart
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        cartid = cartid[0][0]
        # Fetch all the product in the cart and calculate the total price
        items = db.query(f'SELECT product.price, cart_item.qty '
                         f'FROM cart_item '
                         f'JOIN product ON cart_item.Product_ID = product.Product_ID '
                         f'WHERE cart_item.Cart_ID = {cartid}')
        totalprice = 0.0
        for item in items:
            print(item)
            totalprice += item[0]*item[1]
        # Get current timestamp
        timeplaced = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # WHEN?
        timeplanned = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Finally insert entry in order and close the cart
        db.query(f'INSERT INTO '
                 f'cart_order (Cart_ID, Ticket_ID, timePlaced, totalDue, timePlanned) '
                 f'VALUES ({cartid}, {ticket_id}, \'{timeplaced}\', {totalprice}, \'{timeplaced}\')')

        db.query(f'UPDATE cart '
                 f'SET status = \'CLOSED\' '
                 f'WHERE cart_id={cartid}')
        response['status'] = 'success'
        logger.info('Request served successfully')
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        response['status'] = 'fail'
        logger.error(e)
    return jsonify(response), 200
