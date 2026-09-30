from flask import Blueprint, jsonify, request

from app.auth import require_auth
from app.supabase_client import supabase


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.get("/me")
@require_auth
def get_current_user():

    user_id = request.current_user.id

    response = (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", user_id)
        .single()
        .execute()
    )

    profile = response.data

    if not profile:
        return jsonify({
            "error": "Profile not found"
        }), 404

    return jsonify({
        "user": profile
    }), 200