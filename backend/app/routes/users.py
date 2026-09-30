from flask import Blueprint, jsonify, request

from app.auth import require_auth
from app.supabase_client import supabase


users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.get("")
@require_auth
def get_users():
    user_id = request.current_user.id

    response = (
        supabase
        .table("profiles")
        .select("id, email, full_name, avatar_url")
        .neq("id", user_id)
        .order("full_name")
        .execute()
    )

    return jsonify({
        "users": response.data or []
    }), 200