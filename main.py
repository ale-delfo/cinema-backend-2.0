from flask import Flask
import logging
import sys
from blueprints.basic_blueprint import bp

# ----------------------------------------
# WSGI entry point
# ________________________________________


def appfactory(**kwargs):
    root_logger = logging.getLogger()
    root_logger.setLevel(level=logging.DEBUG)
    logger = logging.getLogger('apilogger')
    logger.setLevel(logging.INFO)
    # debug = kwargs.pop('debug', False)
    # if not isinstance(debug, bool):
    #     raise TypeError('debug argument has to be boolean')
    # elif debug:
    #     logging.basicConfig(level=logging.DEBUG)
    fh = logging.FileHandler('./log/complete.txt', mode='a')
    fh_main = logging.FileHandler('./log/mainlog.txt', mode='a')
    ff = logging.Formatter(fmt='[%(asctime)s] %(funcName)s - %(levelname)s : %(message)s',
                           datefmt='%d/%m/%Y %H:%M:%S')
    fh.setFormatter(ff)
    fh_main.setFormatter(ff)
    logger.addHandler(fh_main)
    root_logger.addHandler(fh)
    app = Flask('Cinema-Backend')
    app.register_blueprint(bp)
    return app


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = Flask('Cinema-Backend')
    app.register_blueprint(bp)
    app.run()
