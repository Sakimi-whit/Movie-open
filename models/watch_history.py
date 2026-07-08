# models/watch_history.py
from extensions import db
from datetime import datetime

class WatchHistory(db.Model):
    __tablename__ = 'watch_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False, index=True)
    watched_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    progress = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_history'),)

    def __repr__(self):
        return f'<WatchHistory user={self.user_id} movie={self.movie_id}>'
