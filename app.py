import os
import logging
from logging import StreamHandler, Formatter
import re
from flask import Flask, render_template, current_app, request, jsonify
from config import Config
from extensions import db, login_manager
from models.user import User
from models.movie import Movie
from sqlalchemy import desc
from flask_wtf.csrf import CSRFProtect
from datetime import datetime  # 修复: 添加 datetime 导入

# 初始化 CSRF 实例
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False

    # ===== 🔑 核心修复：统一日志配置 =====
    app.logger.handlers.clear()
    logging.getLogger('werkzeug').handlers.clear()

    handler = StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(Formatter(
        '\033[1;36m[%(asctime)s]\033[0m \033[1;32m%(name)-15s\033[0m | '
        '\033[1;33m%(levelname)-8s\033[0m | %(message)s',
        datefmt='%H:%M:%S'
    ))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    logging.getLogger('werkzeug').propagate = True
    app.logger.propagate = True
    # ===== 修复结束 =====

    # ==================== 内网访问限制配置 ====================
    ALLOWED_NETWORKS = [
        '127.0.0.1',
        '192.168.',
        '10.',
        '172.16.',
        '172.17.',
        '172.18.',
        '172.19.',
        '172.20.',
        '172.21.',
        '172.22.',
        '172.23.',
        '172.24.',
        '172.25.',
        '172.26.',
        '172.27.',
        '172.28.',
        '172.29.',
        '172.30.',
        '172.31.'
    ]

    def is_internal_ip(ip):
        return any(ip.startswith(net) for net in ALLOWED_NETWORKS)

    @app.before_request
    def limit_player_access():
        if request.path.startswith('/watch/') and not is_internal_ip(request.remote_addr):
            app.logger.warning(f"🚫 非法公网访问尝试: {request.remote_addr} -> {request.path}")
            return render_template('access_denied.html',
                                   message="此功能仅限家庭内部网络使用",
                                   now=datetime.now()), 403

    # ==================== 初始化扩展 ====================
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ==================== 注册蓝图 ====================
    from routes.auth import auth_bp
    from routes.movies import movies_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(movies_bp)
    app.register_blueprint(dashboard_bp)

    # ==================== 首页路由 ====================
    @app.route('/')
    def index():
        carousels = []
        carousel_path = os.path.join(current_app.static_folder, 'carousel')
        if os.path.exists(carousel_path):
            files = sorted([f for f in os.listdir(carousel_path)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])[:5]
            for idx, filename in enumerate(files):
                movie_title = os.path.splitext(filename)[0]
                movie = Movie.query.filter(Movie.title.contains(movie_title)).first()
                if movie:
                    carousels.append({
                        'poster_url': f'/static/carousel/{filename}',
                        'movie_id': movie.id,
                        'title': movie.title,
                        'tag': '推荐',
                        'rating': float(movie.rating) if movie.rating else 0.0,
                        'year': movie.year or '2025',
                        'genre': movie.genre or '精彩推荐',
                        'duration': movie.duration or 0,
                        'description': movie.description or f'《{movie.title}》精彩呈现',
                        'bg_class': 'bg-dark' if idx % 2 == 0 else 'bg-light'
                    })
                else:
                    carousels.append({
                        'poster_url': f'/static/carousel/{filename}',
                        'movie_id': None,
                        'title': movie_title,
                        'tag': '未关联',
                        'rating': 0.0,
                        'year': '未知',
                        'genre': '未知',
                        'duration': 0,
                        'description': f'未找到包含"{movie_title}"的电影，请检查文件名',
                        'bg_class': 'bg-dark' if idx % 2 == 0 else 'bg-light'
                    })
                    app.logger.warning(f'⚠️ 轮播图警告：未找到标题包含"{movie_title}"的电影')
                    # 正在热映
        hot_movies = Movie.query.filter_by(is_active=True, is_upcoming=False).order_by(desc(Movie.rating)).limit(6).all()
        poster_path = os.path.join(current_app.static_folder, 'posters')
        poster_files = {}
        if os.path.exists(poster_path):
            for f in os.listdir(poster_path):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    poster_files[os.path.splitext(f)[0]] = f
        for movie in hot_movies:
            matched_url = None
            for key, filename in poster_files.items():
                if key in movie.title or movie.title in key:
                    matched_url = f'/static/posters/{filename}'
                    break
            movie.poster_url = matched_url

        # 即将上映
        upcoming_movies = Movie.query.filter_by(is_active=True, is_upcoming=True).order_by(desc(Movie.year)).limit(6).all()

        return render_template('index.html',
                               carousels=carousels,
                               hot_movies=hot_movies,
                               upcoming_movies=upcoming_movies,
                               now=datetime.now())  # 传递 now 变量

    # ==================== 代理路由 ====================
    @app.route('/api/proxy/third-party')
    def proxy_third_party():
        target = request.args.get('url', '')
        if not target:
            return 'Missing url', 400
        try:
            import requests as req_lib
            from flask import Response as FlaskResp
            hdrs = {'User-Agent': 'Mozilla/5.0'}
            resp = req_lib.get(target, headers=hdrs, timeout=10)
            c = resp.content
            ct = resp.headers.get('Content-Type', '')
            if 'text/html' in ct:
                h = c.decode('utf-8', errors='replace')
                base = target[:target.rfind('/')+1] if '/' in target else target
                h = h.replace('<head>', '<head>' + chr(10) + '<base href="' + base + '">')
                c = h.encode('utf-8')
            fr = FlaskResp(c, status=resp.status_code)
            if ct:
                fr.headers['Content-Type'] = ct
            fr.headers.pop('X-Frame-Options', None)
            fr.headers.pop('Content-Security-Policy', None)
            fr.headers.pop('X-Content-Type-Options', None)
            return fr
        except Exception as e:
            app.logger.error(f'Proxy error: {str(e)}')
            return 'Proxy error', 502

    @app.route('/api/video-source')
    def video_source():
        u = request.args.get('url', '')
        if not u:
            return jsonify({'ok': False})
        try:
            import requests as reqs
            r = reqs.get(u, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            return jsonify({'ok': True, 'h': r.text[:80000]})
        except Exception as e:
            app.logger.error(f'Video source fetch error: {str(e)}')
            return jsonify({'ok': False, 'e': str(e)})

    # ==================== 安全头配置 ====================
    @app.after_request
    def add_security_headers(response):
        if request.path.startswith('/watch/'):
            response.headers['Content-Security-Policy'] = (
                "frame-ancestors 'self'; "
                "frame-src 'self' https://www.yfvod.com https://*.yfvod.com; "
                "child-src 'self' https://www.yfvod.com; "
                "script-src 'self' 'unsafe-inline' https://www.yfvod.com; "
                "connect-src 'self' https://www.yfvod.com"
            )
            response.headers.pop('X-Frame-Options', None)
        return response

    # ==================== 403错误处理（移入 create_app 内部） ====================
    @app.errorhandler(403)
    def access_denied(error):
        return render_template('access_denied.html',
                               message="访问被拒绝 - 仅限家庭内部网络",
                               now=datetime.now()), 403

    return app

if __name__ == '__main__':
    app = create_app()

    # 自动检测可用端口（从 5000 开始递增）
    import socket
    port = 5000
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                break
            except OSError:
                port += 1  # 端口被占用则自动+1
                continue

    print(f"\n✅ 启动成功！端口 {port}\n")
    app.run(debug=True, host='127.0.0.1', port=port, use_reloader=False)

