# models/carousel.py
from extensions import db  # 👈 必须从 extensions 导入，不能 from app import db


class Carousel(db.Model):
    __tablename__ = 'carousel'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(200))
    tag = db.Column(db.String(50))
    rating = db.Column(db.Numeric(3, 1))
    year = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    duration = db.Column(db.Integer)
    description = db.Column(db.Text)
    poster_emoji = db.Column(db.String(10))
    poster_url = db.Column(db.String(500), nullable=True)
    poster_filename = db.Column(db.String(100), nullable=True)  # 只存 'avatar.jpg'
    bg_class = db.Column(db.String(20))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=True)
    order_num = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    movie = db.relationship('Movie', backref='carousels', lazy=True)

    def __repr__(self):
        return f'<Carousel {self.title}>'