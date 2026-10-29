
from flask import Blueprint, jsonify, request

from app.auth import require_auth
from app.email import send_email
from app.supabase_client import supabase


tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

ALLOWED_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "URGENT"}
ALLOWED_STATUSES = {"TODO", "IN_PROGRESS", "COMPLETED"}
MAX_TITLE_LENGTH = 200


@tasks_bp.get("")
@require_auth
def get_tasks():
    """Retrieve tasks created by or assigned to the current user."""
    current_user_id = request.current_user.id

    response = (
        supabase.table("tasks")
        .select("*")
        .or_(
            f"created_by.eq.{current_user_id},"
            f"assigned_to.eq.{current_user_id}"
        )
        .order("created_at", desc=True)
        .execute()
    )

    return jsonify({"tasks": response.data or []}), 200


@tasks_bp.post("")
@require_auth
def create_task():
    """Create a task and notify the assigned user."""
    current_user_id = request.current_user.id
    data = request.get_json(silent=True) or {}

    title = data.get("title", "")
    title = title.strip() if isinstance(title, str) else ""

    description = data.get("description")
    priority = data.get("priority", "MEDIUM")
    assigned_to = data.get("assigned_to")
    due_date = data.get("due_date")

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    if len(title) > MAX_TITLE_LENGTH:
        return jsonify({
            "error": "Task title must be 200 characters or less"
        }), 400

    if priority not in ALLOWED_PRIORITIES:
        return jsonify({"error": "Invalid priority"}), 400

    task_data = {
        "title": title,
        "description": description,
        "priority": priority,
        "created_by": current_user_id,
        "assigned_to": assigned_to,
        "due_date": due_date,
    }

    response = (
        supabase.table("tasks")
        .insert(task_data)
        .execute()
    )

    task = response.data[0] if response.data else None

    if not task:
        return jsonify({"error": "Failed to create task"}), 500

    if assigned_to:
        user_response = (
            supabase.table("profiles")
            .select("email, full_name")
            .eq("id", assigned_to)
            .execute()
        )

        assigned_user = (
            user_response.data[0]
            if user_response.data
            else None
        )

        if assigned_user:
            send_email(
                recipient=assigned_user["email"],
                subject=f"New Task Assigned: {task['title']}",
                body=(
                    f"Hi {assigned_user.get('full_name') or 'there'},\n\n"
                    "You have been assigned a new task in TaskFlow.\n\n"
                    f"Task: {task['title']}\n"
                    f"Priority: {task['priority']}\n\n"
                    "Please log in to TaskFlow to view the task.\n\n"
                    "— TaskFlow"
                ),
            )

    return jsonify({"task": task}), 201


@tasks_bp.patch("/<task_id>")
@require_auth
def update_task(task_id):
    """Update a task and notify its creator when completed."""
    current_user_id = request.current_user.id
    data = request.get_json(silent=True) or {}

    existing_response = (
        supabase.table("tasks")
        .select("*")
        .eq("id", task_id)
        .execute()
    )

    existing_tasks = existing_response.data or []

    if not existing_tasks:
        return jsonify({"error": "Task not found"}), 404

    existing_task = existing_tasks[0]

    if (
        existing_task["created_by"] != current_user_id
        and existing_task["assigned_to"] != current_user_id
    ):
        return jsonify({
            "error": "You are not authorized to update this task"
        }), 403

    updates = {}

    if "title" in data:
        title = data["title"]

        if not isinstance(title, str) or not title.strip():
            return jsonify({
                "error": "Task title cannot be empty"
            }), 400

        title = title.strip()

        if len(title) > MAX_TITLE_LENGTH:
            return jsonify({
                "error": "Task title must be 200 characters or less"
            }), 400

        updates["title"] = title

    if "description" in data:
        updates["description"] = data["description"]

    if "priority" in data:
        if data["priority"] not in ALLOWED_PRIORITIES:
            return jsonify({"error": "Invalid priority"}), 400

        updates["priority"] = data["priority"]

    if "status" in data:
        status = data["status"]

        if status not in ALLOWED_STATUSES:
            return jsonify({"error": "Invalid status"}), 400

        updates["status"] = status
        updates["completed_at"] = (
            "now()" if status == "COMPLETED" else None
        )

    if "due_date" in data:
        updates["due_date"] = data["due_date"]

    if "assigned_to" in data:
        updates["assigned_to"] = data["assigned_to"]

    if not updates:
        return jsonify({
            "error": "No valid fields to update"
        }), 400

    response = (
        supabase.table("tasks")
        .update(updates)
        .eq("id", task_id)
        .execute()
    )

    updated_task = response.data[0] if response.data else None

    if not updated_task:
        return jsonify({"error": "Failed to update task"}), 500

    task_completed = (
        data.get("status") == "COMPLETED"
        and existing_task["status"] != "COMPLETED"
        and existing_task["created_by"] != current_user_id
    )

    if task_completed:
        creator_response = (
            supabase.table("profiles")
            .select("email, full_name")
            .eq("id", existing_task["created_by"])
            .execute()
        )

        creator = (
            creator_response.data[0]
            if creator_response.data
            else None
        )

        if creator:
            send_email(
                recipient=creator["email"],
                subject=f"Task Completed: {updated_task['title']}",
                body=(
                    f"Hi {creator.get('full_name') or 'there'},\n\n"
                    "Your task has been completed in TaskFlow.\n\n"
                    f"Task: {updated_task['title']}\n"
                    f"Priority: {updated_task['priority']}\n\n"
                    "The assigned user has marked this task as completed.\n\n"
                    "— TaskFlow"
                ),
            )

    return jsonify({"task": updated_task}), 200


@tasks_bp.delete("/<task_id>")
@require_auth
def delete_task(task_id):
    """Delete a task created by the current user."""
    current_user_id = request.current_user.id

    existing_response = (
        supabase.table("tasks")
        .select("id, created_by")
        .eq("id", task_id)
        .execute()
    )

    existing_tasks = existing_response.data or []

    if not existing_tasks:
        return jsonify({"error": "Task not found"}), 404

    existing_task = existing_tasks[0]

    if existing_task["created_by"] != current_user_id:
        return jsonify({
            "error": "Only the task creator can delete this task"
        }), 403

    (
        supabase.table("tasks")
        .delete()
        .eq("id", task_id)
        .execute()
    )

    return jsonify({
        "message": "Task deleted successfully"
    }), 200
