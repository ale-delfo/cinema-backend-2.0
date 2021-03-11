# cinema-backend-2.0
Backend software for Cinema Food application

## Project Structure
This project mainly contains the source code for the Cinema Food backend application.<br>
It contains wheels files to install different versions of the dbconnectot module, a simple wrapper for mysql-connector-python module developed in order to provide more useful functions to this application.<br>
Since it has been developed to be run into a container, the repository contains a Dockerfile for building the image.<br>
A YAML file is needed in order to give instructions to the CI Server to perform the operation needed for the CI/CD pipeline.

## APIs
- /api/cart/addproduct [POST] <br>
  Add product to cart
- /api/cart/removeproduct [POST] <br>
  Remove product from cart
- /api/cart/removeallproduct [POST] <br>
  Remove all instances of a given product from cart
- /api/cart/emptycart [GET] <br>
  Empty cart
- /api/cart/getcart [GET] <br>
  Get cart
- /api/cart/getitemqty [POST] <br>
  Get the quantity of instances in cart for a given product
- /api/product/getall [GET] <br>
  Get all product in the menu
- /api/product/getdrinks [GET] <br>
  Get all drinks in the menu
- /api/ticket/buyticket [POST] <br>
  Buy a ticket for a given show
- /api/ticket/gettickets [GET] <br>
  Get all purchased tickets
- /api/ticket/placeorder [POST] <br>
  Place an order for a given ticket with the active cart.
- /api/scheduling/schedule [GET] <br>
  Get delivery scheduling
  
## Configuration file
```shell
[GENERAL]
environment= <production/local>
[MYSQL]
user= <username>
password= <password>
host= <mysql_host_address>
defaultdb= <default db>
```
 The _environment_ configuration in the _GENERAL_ section is used to switch authentication mode and setting during development sessions. <br>
 The _MYSQL_ section contains credentials and settings for the DBMS connection.
