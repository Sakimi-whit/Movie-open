from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.movie import Movie
from models.watch_history import WatchHistory
from models.favorite import Favorite
from werkzeug.security import generate_password_hash
import uuid
import os
import re
import traceback
import sys

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


def match_poster_for_movie(movie):
    """根据电影标题从 static/posters/ 文件夹匹配海报图片"""
    poster_path = os.path.join(current_app.static_folder, 'posters')
    if not os.path.exists(poster_path):
        return None
    for filename in os.listdir(poster_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
            name_key = os.path.splitext(filename)[0]
            if name_key in movie.title or movie.title in name_key:
                return f'/static/posters/{filename}'
    return None


@dashboard_bp.route('/')
@login_required
def index():
    import sys
    sys.stdout.write('\n' + '='*60 + '\n')
    sys.stdout.write('🔥🔥🔥 INDEX() 函数被执行了！🔥🔥🔥\n')
    sys.stdout.write('='*60 + '\n')
    sys.stdout.flush()

    # 观看历史
    history_records = db.session.query(WatchHistory, Movie) \
        .join(Movie, WatchHistory.movie_id == Movie.id) \
        .filter(WatchHistory.user_id == current_user.id) \
        .order_by(WatchHistory.watched_at.desc()) \
        .limit(20).all()

    history = [{
        'movie_id': m.id,
        'title': m.title,
        'poster_url': m.poster_url or url_for('static', filename='img/default-poster.jpg'),
        'watched_at': h.watched_at,
        'progress': h.progress
    } for h, m in history_records]

    # ===== 使用原生SQL查询收藏 =====
    from sqlalchemy import text

    result = db.session.execute(
        text("SELECT movie_id FROM favorites WHERE user_id = :user_id"),
        {"user_id": current_user.id}
    )
    favorite_movie_ids = [row[0] for row in result]

    sys.stdout.write(f'🔥 当前用户ID: {current_user.id}\n')
    sys.stdout.write(f'🔥 收藏电影ID列表: {favorite_movie_ids}\n')
    sys.stdout.flush()

    if favorite_movie_ids:
        favorites = Movie.query.filter(Movie.id.in_(favorite_movie_ids)).all()
        for movie in favorites:
            if not movie.poster_url:
                movie.poster_url = match_poster_for_movie(movie)
    else:
        favorites = []

    sys.stdout.write(f'🔥 最终收藏电影数: {len(favorites)}\n')
    for m in favorites:
        sys.stdout.write(f'  - {m.title}\n')
    sys.stdout.write('='*60 + '\n\n')
    sys.stdout.flush()

    return render_template('dashboard.html',
                           history=history,
                           favorites=favorites,
                           history_count=len(history),
                           favorites_count=len(favorites))


@dashboard_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()
    new_password = request.form.get('new_password', '')

    if not username or not email:
        flash('用户名和邮箱不能为空', 'danger')
        return redirect(url_for('dashboard.index'))

    if not EMAIL_REGEX.match(email):
        flash('邮箱格式不正确', 'warning')
        return redirect(url_for('dashboard.index'))

    if User.query.filter(User.email == email, User.id != current_user.id).first():
        flash('该邮箱已被其他账号使用', 'warning')
        return redirect(url_for('dashboard.index'))

    if User.query.filter(User.username == username, User.id != current_user.id).first():
        flash('该用户名已被使用', 'warning')
        return redirect(url_for('dashboard.index'))

    current_user.username = username
    current_user.email = email

    if new_password:
        if len(new_password) < 6:
            flash('密码长度至少为6位', 'warning')
            return redirect(url_for('dashboard.index'))
        current_user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')

    try:
        db.session.commit()
        flash('资料更新成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('服务器异常，更新失败', 'danger')

    return redirect(url_for('dashboard.index'))


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@dashboard_bp.route('/avatar/upload', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '不支持的文件格式，请上传 JPG/PNG/GIF/WebP'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}'
    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'avatars')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))

    current_user.avatar = filename
    try:
        db.session.commit()
        avatar_url = f'/static/uploads/avatars/{filename}'
        if request.args.get('iframe'):
            return f'<script>window.parent.handleAvatarResult(true, "头像更新成功", "{avatar_url}");</script>'
        return jsonify({
            'success': True,
            'message': '头像更新成功',
            'avatar_url': avatar_url
        })
    except Exception as e:
        db.session.rollback()
        if request.args.get('iframe'):
            return '<script>window.parent.handleAvatarResult(false, "保存失败，请重试", "");</script>'
        return jsonify({'success': False, 'message': '保存失败，请重试'}), 500


@dashboard_bp.route('/favorites')
@login_required
def favorites_page():
    favorites_list = db.session.query(Movie) \
        .join(Favorite, Movie.id == Favorite.movie_id) \
        .filter(Favorite.user_id == current_user.id) \
        .order_by(Favorite.created_at.desc()).all()
    for movie in favorites_list:
        if not movie.poster_url:
            movie.poster_url = match_poster_for_movie(movie)
    return render_template('favorites.html', favorites=favorites_list)


@dashboard_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@dashboard_bp.route('/history/clear', methods=['POST'])
@login_required
def clear_history():
    try:
        WatchHistory.query.filter_by(user_id=current_user.id).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'success': True, 'message': '历史记录已清空'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '清空失败，请重试'}), 500


# ==================== 收藏相关接口 ====================

@dashboard_bp.route('/favorite/toggle/<int:movie_id>', methods=['POST'])
@login_required
def toggle_favorite(movie_id):
    """切换收藏状态（添加/取消）"""
    try:
        print(f'🔍 收到收藏请求: movie_id={movie_id}, user_id={current_user.id}')

        movie = Movie.query.get(movie_id)
        if not movie:
            return jsonify({'success': False, 'message': '电影不存在'}), 404

        fav = Favorite.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()

        if fav:
            db.session.delete(fav)
            db.session.commit()
            print(f'✅ 已取消收藏: {movie.title}')
            return jsonify({
                'success': True,
                'action': 'removed',
                'message': f'已取消收藏《{movie.title}》'
            })
        else:
            new_fav = Favorite(user_id=current_user.id, movie_id=movie_id)
            db.session.add(new_fav)
            db.session.flush()
            db.session.commit()
            print(f'✅ 已添加收藏: {movie.title}')
            return jsonify({
                'success': True,
                'action': 'added',
                'message': f'已收藏《{movie.title}》'
            })
    except Exception as e:
        db.session.rollback()
        print(f'❌ 收藏操作异常: {e}')
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@dashboard_bp.route('/favorite/status/<int:movie_id>', methods=['GET'])
@login_required
def favorite_status(movie_id):
    """获取当前用户对某部电影的收藏状态"""
    try:
        fav = Favorite.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
        return jsonify({
            'is_favorited': fav is not None
        })
    except Exception as e:
        return jsonify({'is_favorited': False, 'error': str(e)}), 500