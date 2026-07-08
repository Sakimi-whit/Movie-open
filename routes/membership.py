from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db  # 👈 必须从 extensions 导入，不能 from app import db
from models.membership import UserMembership, MembershipLevel
from datetime import datetime, timedelta

membership_bp = Blueprint('membership', __name__)


@membership_bp.route('/profile')
@login_required
def profile():
    user_membership = UserMembership.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).order_by(UserMembership.created_at.desc()).first()

    membership_levels = MembershipLevel.query.filter_by(is_active=True).all()

    return render_template('profile.html',
                           user_membership=user_membership,
                           membership_levels=membership_levels)


@membership_bp.route('/upgrade', methods=['POST'])
@login_required
def upgrade_membership():
    membership_level_id = request.form.get('membership_level_id')

    if not membership_level_id:
        flash('请选择会员等级!', 'error')
        return redirect(url_for('membership.profile'))

    # 将当前有效会员设为过期
    current_membership = UserMembership.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).first()
    if current_membership:
        current_membership.status = 'expired'

    # 创建新的会员记录
    new_membership = UserMembership(
        user_id=current_user.id,
        membership_level_id=int(membership_level_id),
        start_date=datetime.now().date(),
        end_date=(datetime.now().date() + timedelta(days=30)),
        status='active'
    )

    db.session.add(new_membership)
    db.session.commit()

    flash('会员升级成功!', 'success')
    return redirect(url_for('membership.profile'))