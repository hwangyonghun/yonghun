from flask import Blueprint, session, redirect, url_for, request, jsonify, render_template
from app import db
from app.models import User, Payment
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_pic'] = user.profile_pic
            
            return redirect(url_for('main.index'))
        else:
            return render_template('login.html', error="Invalid email or password")
            
    return render_template('login.html')

@auth.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return render_template('login.html', error="Email already registered")
        
    new_user = User(
        email=email,
        name=name,
        provider='local',
        password_hash=generate_password_hash(password),
        profile_pic=f"https://ui-avatars.com/api/?name={name}&background=random"
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Auto login
    session['user_id'] = new_user.id
    session['user_name'] = new_user.name
    session['user_pic'] = new_user.profile_pic
    
    # Redirect to setup for phone/address
    return redirect(url_for('auth.profile_setup'))

@auth.route('/auth/<provider>')
def social_login(provider):
    """
    Simulates a Social Login. 
    In a real app, this would redirect to Google/Naver/Kakao OAuth URL.
    For this prototype/demo, it automatically treats the user as 'Verified'.
    """
    # Simulate data based on provider
    mock_data = {
        'google': {'email': 'demo_user@gmail.com', 'name': 'Demo User', 'id': 'google_12345'},
        'naver': {'email': 'demo_user@naver.com', 'name': 'Kim Demo', 'id': 'naver_67890'},
        'kakao': {'email': 'demo_user@daum.net', 'name': 'Lee Demo', 'id': 'kakao_11111'}
    }
    
    data = mock_data.get(provider, mock_data['google'])
    
    # Check or Create User
    user = User.query.filter_by(social_id=data['id'], provider=provider).first()
    if not user:
        user = User(
            name=data['name'],
            email=data['email'],
            provider=provider,
            social_id=data['id'],
            profile_pic=f"https://ui-avatars.com/api/?name={data['name']}&background=random"
        )
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_pic'] = user.profile_pic
    
    # Check if critical info (Phone, Address) is missing
    if not user.phone_number or not user.address:
        return redirect(url_for('auth.profile_setup'))
    
    return redirect(url_for('main.index'))

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@auth.route('/setup', methods=['GET', 'POST'])
def profile_setup():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.phone_number = request.form.get('phone_number')
        user.address = request.form.get('address')
        db.session.commit()
        
        # update session name if changed
        session['user_name'] = user.name
        
        return redirect(url_for('main.index'))
    
    return render_template('profile_setup.html', user=user)

@auth.route('/api/refund', methods=['POST'])
def request_refund():
    # In a real app, this would call Toss/PayPal API to process refund
    transaction_id = request.json.get('transaction_id')
    reason = request.json.get('reason', 'Customer requested')
    
    payment = Payment.query.filter_by(transaction_id=transaction_id).first()
    
    if not payment:
        # Mocking a payment if not exists for demo
        payment = Payment(
            transaction_id=transaction_id,
            amount=1000,
            currency="KRW",
            status="COMPLETED",
            created_at=datetime.datetime.utcnow()
        )
        if 'user_id' in session:
            payment.user_id = session['user_id']
        db.session.add(payment)
        db.session.commit()
    
    payment.status = "REFUNDED"
    payment.refund_requested_at = datetime.datetime.utcnow()
    payment.refund_reason = reason
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Refund processed successfully.'})
