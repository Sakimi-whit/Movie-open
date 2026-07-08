from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import DataError, IntegrityError
from extensions import db
from models.user import User
import traceback

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        next_page = request.args.get('next', '')
        return redirect(url_for('index') + ('?next=' + next_page if next_page else ''))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=bool(request.form.get('remember')))
            # 修复：改为 dashboard.index
            next_page = request.args.get('next') or request.form.get('next') or url_for('dashboard.index')
            return redirect(next_page)
        else:
            flash('邮箱或密码错误，请重新输入', 'danger')
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('所有字段都必须填写', 'warning')
            return redirect(url_for('index'))
        if password != confirm:
            flash('两次输入的密码不一致', 'warning')
            return redirect(url_for('index'))
        if len(password) < 6:
            flash('密码长度至少为 6 位', 'warning')
            return redirect(url_for('index'))

        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册，请换一个', 'warning')
            return redirect(url_for('index'))
        if User.query.filter_by(username=username).first():
            flash('该用户名已被占用，请换一个', 'warning')
            return redirect(url_for('index'))

        try:
            hashed = generate_password_hash(password)
            new_user = User(username=username, email=email, password_hash=hashed)
            db.session.add(new_user)
            db.session.commit()
            flash('🎉 注册成功！请登录', 'success')
            return redirect(url_for('index'))

        except DataError as e:
            db.session.rollback()
            print("数据库数据错误:", e)
            print(traceback.format_exc())
            if 'Data too long' in str(e.orig) or 'password_hash' in str(e.orig):
                flash('密码加密数据过长，请联系管理员（需调整数据库字段）', 'danger')
            else:
                flash('注册信息有误，请检查输入的数据格式', 'danger')
            return redirect(url_for('index'))

        except IntegrityError as e:
            db.session.rollback()
            print("数据库完整性错误:", e)
            print(traceback.format_exc())
            flash('该邮箱或用户名已被注册，请换一个', 'warning')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            print("未知错误:", e)
            print(traceback.format_exc())
            flash('注册失败，请稍后重试', 'danger')
            return redirect(url_for('index'))

    return redirect(url_for('index'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('index'))