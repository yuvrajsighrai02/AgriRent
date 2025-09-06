import stripe
from flask import jsonify, request, redirect, url_for, render_template, session, flash
from eoms import app
from eoms.model import cart, booking, db, mail, customer
from eoms.model.session_utils import allow_role

# Set your Stripe API key from the config file
stripe.api_key = app.config['STRIPE_SECRET_KEY']

@app.route('/create-payment-intent', methods=['POST'])
@allow_role(['customer'])
def create_payment_intent():
    """
    Creates a Stripe PaymentIntent.
    It passes all necessary booking info to Stripe as metadata.
    """
    try:
        data = request.json or {}
        note = data.get('note', '') 

        cart_id = session.get('cart_id')
        customer_id = session.get('customer_id')
        store_id = session.get('my_store')
        
        if not all([cart_id, customer_id, store_id]):
             return jsonify(error={'message': 'Session is missing required information.'}), 400

        cart_items = cart.get_cart_items_by_cart_id(cart_id)
        if not cart_items:
            return jsonify(error={'message': 'Your cart is empty.'}), 400

        _, _, cart_total, _ = cart.get_cart_items_totals(cart_items)
        amount_in_cents = int(cart_total * 100)

        customer_email = session.get('email', '')
        if not customer_email:
            return jsonify(error={'message': 'Customer email not found in session.'}), 400


        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency='inr',
            automatic_payment_methods={'enabled': True},
            receipt_email=customer_email,
            metadata={
                'cart_id': cart_id,
                'customer_id': customer_id,
                'store_id': store_id,
                'note': note,
                'customer_email': customer_email,
                'payment_type': 'new_booking'
            }
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        print(f"Error in create-payment-intent: {e}")
        return jsonify(error={'message': str(e)}), 500

@app.route('/payment-success')
def payment_success():
    """
    Handles the redirect from Stripe after a successful payment.
    It retrieves the booking_id from the session (placed there by the webhook)
    and redirects to the final receipt page.
    """
    # --- THIS IS THE FIX ---
    # Retrieve the booking_id from the session
    booking_id = session.pop('latest_booking_id', None)

    if not booking_id:
        # If for some reason the booking_id isn't in the session,
        # provide a generic success message and redirect to their main booking page.
        flash('Your payment was successful and your booking is confirmed!', 'success')
        return redirect(url_for('mybooking'))

    # Redirect to the specific receipt page for the booking that was just made
    return redirect(url_for('receipt', booking_id=booking_id))


@app.route('/payment-cancelled')
def payment_cancelled():
    flash('Your payment was cancelled or failed. Your booking has not been confirmed.', 'warning')
    return redirect(url_for('view_cart'))

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """
    Listens for events from Stripe. This is the heart of the booking logic.
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        metadata = payment_intent['metadata']
        payment_type = metadata.get('payment_type')

        with app.app_context():
            if payment_type == 'new_booking':
                try:
                    booking_id = booking.finalize_booking_from_payment(
                        cart_id=int(metadata['cart_id']),
                        customer_id=int(metadata['customer_id']),
                        store_id=int(metadata['store_id']),
                        note=metadata['note'],
                        payment_intent_id=payment_intent['id']
                    )

                    if booking_id:
                        # --- THIS IS THE FIX ---
                        # Store the new booking_id in the user's session.
                        # This allows the /payment-success route to find it.
                        session['latest_booking_id'] = booking_id

                        print(f"Booking {booking_id} successful. Sending receipt...")
                        customer_email = metadata.get('customer_email')
                        if customer_email:
                            subject = f"Your AgriRent Booking Confirmation #{booking_id}"
                            receipt_url = url_for('receipt', booking_id=booking_id, _external=True)
                            body = (
                                f"Thank you for your order!\\n\\n"
                                f"Your booking #{booking_id} has been confirmed.\\n\\n"
                                f"You can view your receipt online here:\\n{receipt_url}"
                            )
                            mail.send_email('no-reply@agrihire.com', customer_email, subject, body)
                        else:
                            print(f"WARNING: Could not send receipt for booking {booking_id}. No customer email in metadata.")

                except Exception as e:
                    print(f"CRITICAL ERROR: Webhook failed to process new booking for payment {payment_intent['id']}. Error: {e}")
                    return 'Error processing booking', 500

    elif event['type'] == 'payment_intent.payment_failed':
        print(f"Payment failed for {event['data']['object']['id']}.")

    return 'OK', 200
