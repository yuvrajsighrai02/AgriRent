from flask import Flask
# REMOVED: from eoms.secret import SECRET_KEY
# ADDED: Import the Config class from the new config file
from config import Config

app = Flask(__name__)

# This line tells Flask to load all settings from your new config.py file
app.config.from_object(Config)

# Flask will now automatically use the SECRET_KEY from your config file
# app.secret_key = SECRET_KEY <-- This is no longer needed here

# Routes
from eoms.route import home
from eoms.route import user_auth
from eoms.route.dashboard import dashboard
from eoms.route.dashboard import bookings
from eoms.route.dashboard import equipment_returned_today
from eoms.route.dashboard import get_customer_details
from eoms.route.dashboard import reports
from eoms.route import profile
from eoms.route import product_manage
from eoms.route import menu_utils
from eoms.route import equipment
from eoms.route import stock_utils
from eoms.route.customer import customer
from eoms.route import customer_receipt
from eoms.route import shopping_cart
from eoms.route import booking_processing
from eoms.route import my_store_utils
from eoms.route import error
from eoms.route import inventory
from eoms.route import administration
from eoms.route import stores
from eoms.route import promotion
from eoms.route import contact
from eoms.route import about
from eoms.route import news
from eoms.route import terms
# ADDED: Make sure to import your new payment route file
from eoms.route import payment

