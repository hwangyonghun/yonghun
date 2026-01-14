from datetime import datetime
from app import db

class AnalysisLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    deepfake_score = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<AnalysisLog {self.filename}: {self.deepfake_score:.2f}>'

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cert_id = db.Column(db.String(20), index=True) # The public ID
    analysis_uuid = db.Column(db.String(36), unique=True) # To prevent dupes per analysis
    filename = db.Column(db.String(128))
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    verdict = db.Column(db.String(20))
    confidence_score = db.Column(db.String(10))
    ip_address = db.Column(db.String(50))
    file_hash = db.Column(db.String(64))  # SHA256 matches
    original_filename = db.Column(db.String(255)) # Track original file name
    user_name = db.Column(db.String(100)) # For > 10 usage
    user_address = db.Column(db.String(200)) # For > 10 usage

    def __repr__(self):
        return f'<Certificate {self.cert_id} #{self.id}>'

class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_url = db.Column(db.String(500), nullable=False)  # Where it was found
    image_url = db.Column(db.String(500), nullable=False)   # The image source
    ai_probability = db.Column(db.Float)
    status = db.Column(db.String(20), default='DETECTED')   # DETECTED, WARNING_SENT, RESOLVED
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    contact_info = db.Column(db.String(200)) # Extracted email/phone

    def __repr__(self):
        return f'<Violation {self.id} - {self.status}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True) # Optional for some social auth?
    name = db.Column(db.String(100))
    provider = db.Column(db.String(20)) # google, naver, kakao, local
    social_id = db.Column(db.String(100), unique=True, nullable=True) # Nullable for local auth
    password_hash = db.Column(db.String(200)) # For local auth
    profile_pic = db.Column(db.String(500))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='user', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Nullable for guest checkout
    transaction_id = db.Column(db.String(100), unique=True)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(10))
    status = db.Column(db.String(20)) # COMPLETED, REFUNDED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    refund_requested_at = db.Column(db.DateTime)
    refund_reason = db.Column(db.String(200))
    payer_name = db.Column(db.String(100)) # Name registered at payment
    payer_address = db.Column(db.String(200)) # Address registered at payment

    def __repr__(self):
        return f'<Payment {self.transaction_id} : {self.status}>'
