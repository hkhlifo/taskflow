from functools import wraps

from flask import request, jsonify

from app.supabase_client import supabase


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "error": "Authorization header is required"
            }), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Invalid authorization format"
            }), 401

        access_token = auth_header.split(" ", 1)[1]

        if not access_token:
            return jsonify({
                "error": "Access token is missing"
            }), 401

        try:
            response = supabase.auth.get_user(access_token)

            user = response.user

            if not user:
                return jsonify({
                    "error": "Invalid access token"
                }), 401

            request.current_user = user

        except Exception:
            return jsonify({
                "error": "Authentication failed"
            }), 401

        return f(*args, **kwargs)

    return decorated_function