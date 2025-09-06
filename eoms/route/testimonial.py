from flask import render_template, redirect, url_for, flash, session
from eoms import app
from eoms.model import db
from eoms.form.testimonial_form import TestimonialForm
from eoms.model.session_utils import allow_role

# ==============================================================================
# CUSTOMER-FACING ROUTES
# ==============================================================================

@app.route('/post-testimonial', methods=['GET', 'POST'])
@allow_role(['customer'])
def post_testimonial():
    """
    Handles the testimonial submission form for customers.
    """
    form = TestimonialForm()
    if form.validate_on_submit():
        customer_id = session.get('customer_id')
        rating = form.rating.data
        text = form.testimonial_text.data
        
        try:
            cursor = db.get_cursor()
            sql = """
                INSERT INTO testimonials (customer_id, rating, testimonial_text, status)
                VALUES (%s, %s, %s, 'pending')
            """
            cursor.execute(sql, (customer_id, rating, text))
            db.connection.commit()
            flash('Thank you! Your testimonial has been submitted for review.', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')

    return render_template('customer/post_testimonial.html', form=form)

# ==============================================================================
# ADMIN-FACING ROUTES
# ==============================================================================

@app.route('/admin/testimonials')
@allow_role(['admin', 'nmgr', 'lmgr'])
def manage_testimonials():
    """
    Displays a list of all testimonials for administrators to manage.
    """
    testimonials = get_all_testimonials()
    return render_template('administration/manage_testimonials.html', testimonials=testimonials)

@app.route('/admin/testimonial/approve/<int:testimonial_id>', methods=['POST'])
@allow_role(['admin', 'nmgr', 'lmgr'])
def approve_testimonial(testimonial_id):
    """
    Approves a testimonial, changing its status to 'approved'.
    """
    update_testimonial_status(testimonial_id, 'approved')
    flash('Testimonial has been approved and is now live.', 'success')
    return redirect(url_for('manage_testimonials'))

@app.route('/admin/testimonial/reject/<int:testimonial_id>', methods=['POST'])
@allow_role(['admin', 'nmgr', 'lmgr'])
def reject_testimonial(testimonial_id):
    """
    Rejects a testimonial, changing its status to 'rejected'.
    """
    update_testimonial_status(testimonial_id, 'rejected')
    flash('Testimonial has been rejected.', 'info')
    return redirect(url_for('manage_testimonials'))

# ==============================================================================
# DATABASE HELPER FUNCTIONS
# ==============================================================================

def get_approved_testimonials(limit=3):
    """
    Fetches approved testimonials to display on the homepage.
    """
    cursor = db.get_cursor()
    sql = """
        SELECT t.rating, t.testimonial_text, c.first_name, c.last_name
        FROM testimonials t
        JOIN customer c ON t.customer_id = c.customer_id
        WHERE t.status = 'approved'
        ORDER BY t.created_at DESC
        LIMIT %s
    """
    cursor.execute(sql, (limit,))
    return cursor.fetchall()

def get_all_testimonials():
    """
    Fetches all testimonials regardless of status for the admin panel.
    """
    cursor = db.get_cursor()
    sql = """
        SELECT t.testimonial_id, t.rating, t.testimonial_text, t.created_at, t.status, c.first_name, c.last_name
        FROM testimonials t
        JOIN customer c ON t.customer_id = c.customer_id
        ORDER BY t.created_at DESC
    """
    cursor.execute(sql)
    return cursor.fetchall()

def update_testimonial_status(testimonial_id, status):
    """
    Updates the status of a specific testimonial ('approved', 'rejected').
    """
    cursor = db.get_cursor()
    sql = "UPDATE testimonials SET status = %s WHERE testimonial_id = %s"
    cursor.execute(sql, (status, testimonial_id))
    db.connection.commit()
