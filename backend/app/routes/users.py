
from flask import Blueprint, jsonify, request

from app.auth import require_auth
from app.supabase_client import supabase


users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.get("")
@require_auth
def get_users():
    """Retrieve all users except the currently authenticated user."""
    current_user_id = request.current_user.id

    response = (
        supabase.table("profiles")
        .select("id, email, full_name, avatar_url")
        .neq("id", current_user_id)
        .order("full_name")
        .execute()
    )

    users = response.data or []

    return jsonify({"users": users}), 200
