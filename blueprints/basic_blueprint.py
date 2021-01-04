from flask import Blueprint, request, jsonify
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

# ------------------------------------------------------------------
# Utilities configuration
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# Defining routes associated to the blueprint  -  Cart Section
# ------------------------------------------------------------------


@bp.route('/api/cart/addproduct', methods=['POST'])
@authorization.login_required
def add_product_to_cart():
    uid = authorization.current_user()
    db = DatabaseConnector(user, passw, host, defaultdb)
    logging.info(f'User {uid} requested cart/add_product_to_cart api')
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
    logging.info(f'User {uid} requested cart/remove_product_from_cart api')
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
    logging.info(f'User {uid} requested cart/empty_cart api')
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


@bp.route('/api/cart/getcart', methods=['GET'])
@authorization.login_required
def get_cart():
    uid = authorization.current_user()
    logging.info(f'User {uid} requested cart/get_cart api')
    db = DatabaseConnector(user, passw, host, defaultdb)
    response = []
    try:
        # Check if there's a pending cart for the user
        cartid = db.query(f'SELECT Cart_ID from cart WHERE Customer_ID = \'{uid}\' AND status = \'PENDING\'')
        # If there is one, remove the requested item
        if len(cartid) != 0:
            cartid = cartid[0][0]
            logging.debug(f'Cart ID found: {cartid}')
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
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logging.error(e)
    return jsonify(response), 200

# ------------------------------------------------------------------
# Defining routes associated to the blueprint  -  Product Section
# ------------------------------------------------------------------


@bp.route('/api/product/getall', methods=['GET'])
@authorization.login_required
def get_all_food():
    uid = authorization.current_user()
    logging.info(f'User {uid} requested product/getall api')
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
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logging.error(e)
        #response['status'] = 'fail'
    return jsonify(response), 200


@bp.route('/api/product/getdrinks', methods=['GET'])
@authorization.login_required
def get_all_drinks():
    uid = authorization.current_user()
    logging.info(f'User {uid} requested product/getall api')
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
    except Exception as e:
        # Log the exception and not raise it in order to provide a response to the client
        logging.error(e)
        #response['status'] = 'fail'
    return jsonify(response), 200