from extensions import db
from sqlalchemy import Numeric

class Movie(db.Model):
    __tablename__ = 'movie'
    video_updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    original_title = db.Column(db.String(200))
    year = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    duration = db.Column(db.Integer)
    rating = db.Column(Numeric(3, 1))
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(255))
    bg_color = db.Column(db.String(20))
    trailer_url = db.Column(db.String(255))
    play_url = db.Column(db.String(255))

    # ========== 新增字段 ==========
    video_url = db.Column(db.String(500), nullable=True)    # 视频播放地址 (m3u8/mp4)
    external_id = db.Column(db.Integer, nullable=True)      # 可可影视的外部ID

    is_active = db.Column(db.Boolean, default=True)
    is_upcoming = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'genre': self.genre,
            'rating': float(self.rating) if self.rating else None,
            'poster_url': self.poster_url,
            'is_upcoming': self.is_upcoming,
            'has_video': bool(self.video_url)  # 新增：是否有视频
        }