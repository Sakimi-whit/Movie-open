from app import create_app
from extensions import db
from models.movie import Movie

app = create_app()
with app.app_context():
    movie = Movie.query.get(1)
    if movie:
        movie.video_url = "https://svipsvip.ffzyread1.com/20250123/35304_62442aaa/index.m3u8"
        db.session.commit()
        print(f"✅ 已更新: {movie.title}")
        print(f"   video_url: {movie.video_url}")
    else:
        print("未找到电影")