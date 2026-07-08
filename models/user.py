from extensions import db
from flask_login import UserMixin
from sqlalchemy import Text

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(Text, nullable=False)   # 改成 Text 避免长度问题
    avatar = db.Column(db.String(255), default='/static/default_avatar.png')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def avatar_url(self):
        if self.avatar and self.avatar.startswith('/static/') and self.avatar != '/static/default_avatar.png':
            return self.avatar
        elif self.avatar:
            return '/static/uploads/avatars/' + self.avatar
        return '/static/uploads/avatars/default.svg'
