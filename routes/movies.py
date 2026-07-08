from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc
from extensions import db
from models.movie import Movie
from models.carousel import Carousel
from models.membership import UserMembership
import os
import re
import logging
import time
import random
import requests
import urllib3
from urllib.parse import quote, urlparse, urljoin, unquote
import urllib.parse
from datetime import datetime

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

movies_bp = Blueprint('movies', __name__)
logger = logging.getLogger(__name__)

# ==================== 【核心】解析站配置 ====================
RESOLVER_SITES = [
    {
        "name": "万能解析(liumingye)",
        "base_url": "https://tool.liumingye.cn/video/?url=",
        "referer": "https://tool.liumingye.cn/",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    {
        "name": "酷云解析",
        "base_url": "https://jx.realdou.cn/api.php?url=",
        "referer": "https://jx.realdou.cn/",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    {
        "name": "OK解析",
        "base_url": "https://okjx.cc/?url=",
        "referer": "https://okjx.cc/",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    {
        "name": "无名解析",
        "base_url": "https://jx.887987.xyz/?url=",
        "referer": "https://jx.887987.xyz/",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    {
        "name": "爱豆解析",
        "base_url": "https://jx.aidouer.net/?url=",
        "referer": "https://jx.aidouer.net/",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    {
        "name": "极速解析",
        "base_url": "https://jx.8090g.cn/jiexi/?url=",
        "referer": "https://jx.8090g.cn/",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
]

def get_resolver_url(video_url):
    """获取最佳解析站URL（自动轮询）"""
    try:
        decoded_url = unquote(video_url)
        encoded_url = urllib.parse.quote(decoded_url, safe='')

        for resolver in RESOLVER_SITES:
            resolver_url = f"{resolver['base_url']}{encoded_url}"
            try:
                resp = requests.head(resolver_url, timeout=3, allow_redirects=True)
                if resp.status_code < 400:
                    logger.info(f"✅ [解析] 选用 {resolver['name']}: {resolver_url[:60]}...")
                    return {
                        "url": resolver_url,
                        "referer": resolver['referer'],
                        "user_agent": resolver['user_agent'],
                        "name": resolver['name']
                    }
                else:
                    logger.warning(f"⚠️ [解析] {resolver['name']} 状态码 {resp.status_code}，尝试下一个")
            except Exception as e:
                logger.warning(f"⚠️ [解析] {resolver['name']} 不可用: {str(e)[:50]}，尝试下一个")
                continue

    except Exception as e:
        logger.warning(f"⚠️ [解析] 编码失败: {str(e)}")

    logger.warning("⚠️ [解析] 所有解析站检测失败，使用第一个作为备用")
    if RESOLVER_SITES:
        resolver = RESOLVER_SITES[0]
        resolver_url = f"{resolver['base_url']}{urllib.parse.quote(unquote(video_url), safe='')}"
        return {
            "url": resolver_url,
            "referer": resolver['referer'],
            "user_agent": resolver['user_agent'],
            "name": resolver['name'] + "(备用)"
        }

    return {
        "url": video_url,
        "referer": "https://www.yfvod.com/",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "name": "备用源"
    }

# ==================== 【关键】嵌入播放器路由 ====================
@movies_bp.route('/watch/<int:movie_id>')
@login_required
def watch_movie(movie_id):
    """嵌入第三方解析站播放器"""
    movie = Movie.query.get_or_404(movie_id)
    movie.views_count += 1
    db.session.commit()

    if not movie.video_url:
        if movie.external_id:
            movie.video_url = f"https://www.yfvod.com/vod/play/id/{movie.external_id}.html"
            db.session.commit()
            logger.info(f"🔄 [修复] 从external_id重建URL: {movie.video_url}")

        if not movie.video_url:
            logger.error(f"❌ 无视频源: 电影ID={movie_id}, 标题={movie.title}")
            return render_template('error.html',
                                   message=f"《{movie.title}》暂无可用视频源",
                                   now=datetime.now())

    resolver = get_resolver_url(movie.video_url)

    embed_data = {
        'movie': {
            'id': movie.id,
            'title': movie.title,
            'year': movie.year or '',
            'rating': float(movie.rating) if movie.rating else 8.8,
            'description': movie.description or '精彩影片，不容错过',
            'poster_url': match_poster_for_movie(movie)
        },
        'resolver': resolver,
        'autofullscreen': request.args.get('fullscreen', '0') == '1'
    }

    logger.info(f"🎬 [播放] {movie.title} | 解析站: {resolver['name']}")
    return render_template('embed_resolver.html', **embed_data, now=datetime.now())

# ==================== 辅助函数 ====================
def match_poster_for_movie(movie):
    """匹配海报"""
    poster_path = os.path.join(current_app.static_folder, 'posters')
    if not os.path.exists(poster_path):
        return None
    for filename in os.listdir(poster_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
            name_key = os.path.splitext(filename)[0]
            if name_key in movie.title or movie.title in name_key:
                return f'/static/posters/{filename}'
    return None

# ==================== 路由 ====================

@movies_bp.route('/api/search')
def search_movies():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 1:
        return jsonify({'results': []})
    movies = Movie.query.filter(Movie.is_active == True, Movie.title.contains(q)).order_by(desc(Movie.rating)).limit(8).all()
    results = []
    for movie in movies:
        poster = movie.poster_url or match_poster_for_movie(movie)
        results.append({
            'id': movie.id,
            'title': movie.title,
            'year': movie.year or '',
            'genre': (movie.genre or '').split(',')[0] if movie.genre else '',
            'rating': float(movie.rating) if movie.rating else None,
            'poster_url': poster,
            'is_upcoming': movie.is_upcoming,
            'has_video': bool(movie.video_url)
        })
    return jsonify({'results': results})

@movies_bp.route('/search')
def search_page():
    q = request.args.get('q', '').strip()
    if not q:
        return render_template('search_results.html', query=q, results=[], total=0, now=datetime.now())
    movies = Movie.query.filter(Movie.is_active == True, Movie.title.contains(q)).order_by(desc(Movie.rating)).all()
    for movie in movies:
        movie.poster_url = match_poster_for_movie(movie)
    return render_template('search_results.html', query=q, results=movies, total=len(movies), now=datetime.now())

@movies_bp.route('/movie/<int:movie_id>')
@login_required
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    movie.views_count += 1
    db.session.commit()
    membership = UserMembership.query.filter_by(user_id=current_user.id, status='active').first()
    movie.poster_url = match_poster_for_movie(movie)
    logger.info(f'[🎬 详情页] 电影: {movie.title}, video_url: {movie.video_url or "无"}')

    watch_url = url_for('movies.watch_movie', movie_id=movie_id)
    return render_template('movie_detail.html',
                           movie=movie,
                           membership=membership,
                           watch_url=watch_url,
                           now=datetime.now())

@movies_bp.route('/api/test', methods=['GET'])
def api_test():
    logger.info('🧪 API 测试 (解析站模式)')
    return jsonify({'status': 'ok', 'message': '第三方解析站模式已启用！'})

@movies_bp.route('/api/fetch_video/<int:movie_id>', methods=['POST'])
@login_required
def api_fetch_video(movie_id):
    """简化：仅用于记录访问，实际播放由解析站处理"""
    movie = Movie.query.get_or_404(movie_id)
    logger.info(f'📡 [解析] 准备播放 | 电影ID={movie_id}, 标题={movie.title}')

    if not movie.video_url:
        PRESET_IDS = {
            "肖申克的救赎": "7033",
            "星际穿越": "31253",
            "泰坦尼克号": "1072",
            "盗梦空间": "28489",
            "阿甘正传": "945",
            "这个杀手不太冷": "687",
            "教父": "254",
            "搏击俱乐部": "3810",
            "蝙蝠侠：黑暗骑士": "12920",
            "指环王：王者归来": "8216"
        }

        if movie.title in PRESET_IDS:
            movie.video_url = f"https://www.yfvod.com/vod/play/id/{PRESET_IDS[movie.title]}.html"
            db.session.commit()
            logger.info(f'✅ [预置] 生成URL | {movie.video_url}')

    return jsonify({
        'success': True,
        'message': '准备就绪（解析站模式）',
        'video_url': movie.video_url or ''
    })

@movies_bp.route('/api/check_video/<int:movie_id>', methods=['GET'])  # ✅ 修复：多了个括号
@login_required
def api_check_video(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    has_video = bool(movie.video_url)
    return jsonify({
        'has_video': has_video,
        'video_url': movie.video_url or '',
        'message': '解析站模式已启用' if has_video else '未设置视频地址'
    })

@movies_bp.route('/api/fetch_all_videos', methods=['POST'])
@login_required
def api_fetch_all_videos():
    """简化：批量检查视频状态"""
    movies = Movie.query.all()
    logger.info(f'🔄 [解析] 批量检查 {len(movies)} 部电影')
    results = []
    success_count = 0

    PRESET_IDS = {
        "肖申克的救赎": "7033",
        "星际穿越": "31253",
        "泰坦尼克号": "1072",
        "盗梦空间": "28489",
        "阿甘正传": "945",
        "这个杀手不太冷": "687",
        "教父": "254",
        "搏击俱乐部": "3810",
        "蝙蝠侠：黑暗骑士": "12920",
        "指环王：王者归来": "8216"
    }

    for idx, movie in enumerate(movies, 1):
        logger.info(f'🔄 [{idx}/{len(movies)}] 处理: {movie.title}')
        if not movie.video_url and movie.title in PRESET_IDS:
            movie.video_url = f"https://www.yfvod.com/vod/play/id/{PRESET_IDS[movie.title]}.html"
            db.session.commit()
            success_count += 1
            results.append({'id': movie.id, 'title': movie.title, 'video_url': movie.video_url, 'status': 'fixed'})
        elif movie.video_url:
            success_count += 1
            results.append({'id': movie.id, 'title': movie.title, 'video_url': movie.video_url, 'status': 'exists'})
        else:
            results.append({'id': movie.id, 'title': movie.title, 'video_url': None, 'status': 'missing'})

    logger.info(f'✅ 批量完成: 有效 {success_count}, 无效 {len(movies) - success_count}')
    return jsonify({
        'total': len(movies),
        'success': success_count,
        'failed': len(movies) - success_count,
        'results': results
    })

# ==================== 直接解析URL路由 ====================
@movies_bp.route('/play')
@login_required
def direct_play():
    """直接解析任意URL（用于书签/分享）"""
    url = request.args.get('url', '').strip()
    title = request.args.get('title', '未知影片')

    if not url:
        return render_template('error.html',
                               message="缺少视频URL参数",
                               now=datetime.now())

    resolver = get_resolver_url(url)

    movie_stub = {
        'id': 0,
        'title': title,
        'year': '',
        'rating': 8.8,
        'description': '外部视频源'
    }

    embed_data = {
        'movie': movie_stub,
        'resolver': resolver,
        'autofullscreen': False
    }

    logger.info(f"🎬 [直连] {title} | URL: {url[:50]}...")
    return render_template('embed_resolver.html', **embed_data, now=datetime.now())

# ==================== 电影列表页 ====================
@movies_bp.route('/movies')
def movie_list():
    """电影列表页（支持搜索、筛选、排序、分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    keyword = request.args.get('keyword', '').strip()
    genre_filter = request.args.get('genre', '').strip()
    sort_by = request.args.get('sort', 'rating')

    query = Movie.query.filter_by(is_active=True)

    if keyword:
        query = query.filter(Movie.title.contains(keyword))

    if genre_filter:
        query = query.filter(Movie.genre.contains(genre_filter))

    if sort_by == 'rating':
        query = query.order_by(desc(Movie.rating))
    elif sort_by == 'year':
        query = query.order_by(desc(Movie.year))
    elif sort_by == 'title':
        query = query.order_by(Movie.title)
    else:
        query = query.order_by(desc(Movie.rating))

    movies = query.paginate(page=page, per_page=per_page, error_out=False)

    for movie in movies.items:
        movie.poster_url = match_poster_for_movie(movie)

    all_genres = db.session.query(Movie.genre).filter(Movie.is_active == True).distinct().all()
    genre_list = []
    for g in all_genres:
        if g[0]:
            for item in g[0].split(','):
                item = item.strip()
                if item and item not in genre_list:
                    genre_list.append(item)

    return render_template('movie_list.html',
                           movies=movies,
                           keyword=keyword,
                           genre_filter=genre_filter,
                           sort_by=sort_by,
                           genre_list=genre_list,
                           now=datetime.now())