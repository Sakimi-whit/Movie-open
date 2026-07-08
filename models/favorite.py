from extensions import db
from datetime import datetime

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # ✅ 改为 user.id
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False, index=True)  # ✅ 改为 movie.id
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 防止重复收藏
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_favorite'),)

    def __repr__(self):
        return f'<Favorite user={self.user_id} movie={self.movie_id}>'