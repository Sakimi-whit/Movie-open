from extensions import db

class UserMembership(db.Model):
    __tablename__ = 'user_membership'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    membership_type = db.Column(db.String(20), default='basic')
    status = db.Column(db.String(20), default='active')
    expire_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref='memberships', lazy=True)