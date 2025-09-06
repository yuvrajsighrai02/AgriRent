from eoms import app
from flask import render_template, redirect, request, flash, url_for

# Route for the About Us page
@app.route('/about')
def about():
    return render_template('about.html')
