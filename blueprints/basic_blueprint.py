from flask import Blueprint, request
from utils.authorizaton import authorization
from dbconnector import DatabaseConnector
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

# ----------------------------------------------
# Utilities configuration
# ----------------------------------------------

db = DatabaseConnector(user, passw, host, defaultdb)

# ----------------------------------------------
# Defining routes associated to the blueprint
# ----------------------------------------------


@bp.route('/api/cart/addproduct', methods=['POST'])
@authorization.login_required
def add_product_to_cart():
    uid = authorization.current_user()
    logging.info(f'User {uid} requested add_product_to_cart api')
    productid = request.form.get('productId')
    response = dict()
    response['productId'] = productid
    try:
        # Check if there's a pending cart for the user
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # If not, create one and retrieve the ID
        if len(cartid) == 0:
            db.query(f'INSERT INTO cart (Customer_ID,totalDue,status) VALUES (\'{uid}\',0.0,\'PENDING\')')
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
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logging.error(e)
        response['status'] = 'fail'
    return response, 200

@bp.route('/api/cart/removeproduct', methods=['POST'])
@authorization.login_required
def remove_product_from_cart():
    uid = authorization.current_user()
    logging.info(f'User {uid} requested remove_product_from_cart api')
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
            logging.debug(f'Cart ID found: {cartid}')
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
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logging.error(e)
        response['status'] = 'fail'
    return response, 200


@bp.route('/api/cart/emptycart', methods=['GET'])
@authorization.login_required
def empty_cart():
    uid = authorization.current_user()
    logging.info(f'User {uid} requested empty_cart api')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = dict()
    try:
        # Check if there's a pending cart for the user
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # If there is one, remove the requested item
        if len(cartid) != 0:
            cartid = cartid[0][0]
            logging.debug(f'Cart ID found: {cartid}')
            db.query(f'DELETE FROM cart_item WHERE Cart_ID={cartid}')
        response['status'] = 'success'
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logging.error(e)
        response['status'] = 'fail'
    return response, 200
