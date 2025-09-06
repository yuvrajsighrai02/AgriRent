from eoms import app
from flask import render_template, redirect, request, flash, url_for, session
from eoms.model.product import select_3_rand_products, select_4_rand_products
from eoms.form.registration_form import RegistrationForm
from eoms.model import auth
from eoms.model.session_utils import allow_role, logged_in
from eoms.model import promotion, product
from eoms.route.testimonial import get_approved_testimonials

# Route for the home page

@app.route('/')
def home():
    home_products = select_3_rand_products()
    home_popular_products = select_4_rand_products()
    
    # Get poplular products
    popular_products = product.get_products_by_categroy(category_code=None)
    popular_products.sort(key=lambda x: x['price_a'])

    testimonials = get_approved_testimonials(limit=3)
    # Get products on promotion
    promo_products = promotion.get_products_on_promo()
    if promo_products:
        promo_products.sort(key=lambda x: x['disc_rate'], reverse=True)
    else:
        for p in popular_products:
            p['disc_rate'] = 0
        promo_products = popular_products
    return render_template('home.html', 
                           popular_products=popular_products, 
                           promo_products=promo_products,
                           home_products=home_products, 
                           testimonials=testimonials,
                           home_popular_products=home_popular_products)