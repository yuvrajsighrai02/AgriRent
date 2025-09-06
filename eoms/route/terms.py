from eoms import app
from flask import render_template


# Route to display terms and conditions 
@app.route('/terms_and_conditions')
def t_and_c():
    return render_template('/shopping/terms.html')

