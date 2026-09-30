from flask import Blueprint, jsonify, request

from app.auth import require_auth
from app.supabase_client import supabase
from app.email import send_email


tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


@tasks_bp.get("")
@require_auth
def get_tasks():
    user_id = request.current_user.id

    response = (
        supabase
        .table("tasks")
        .select("*")
        .or_(f"created_by.eq.{user_id},assigned_to.eq.{user_id}")
        .order("created_at", desc=True)
        .execute()
    )

    return jsonify({
        "tasks": response.data or []
    }), 200


@tasks_bp.post("")
@require_auth
def create_task():
    user_id = request.current_user.id
    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()
    description = data.get("description")
    priority = data.get("priority", "MEDIUM")
    assigned_to = data.get("assigned_to")
    due_date = data.get("due_date")

    if not title:
        return jsonify({
            "error": "Task title is required"
        }), 400

    if len(title) > 200:
        return jsonify({
            "error": "Task title must be 200 characters or less"
        }), 400

    allowed_priorities = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "URGENT",
    }

    if priority not in allowed_priorities:
        return jsonify({
            "error": "Invalid priority"
        }), 400

    task_data = {
        "title": title,
        "description": description,
        "priority": priority,
        "created_by": user_id,
        "assigned_to": assigned_to,
        "due_date": due_date,
    }

    response = (
        supabase
        .table("tasks")
        .insert(task_data)
        .execute()
    )

    task = response.data[0] if response.data else None

    if not task:
        return jsonify({
            "error": "Failed to create task"
        }), 500

    # Send notification to assigned user
    if assigned_to:
        user_response = (
            supabase
            .table("profiles")
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
                body=f"""Hi {assigned_user.get("full_name") or "there"},

You have been assigned a new task in TaskFlow.

Task: {task["title"]}
Priority: {task["priority"]}

Please log in to TaskFlow to view the task.

— TaskFlow
""",
            )

    return jsonify({
        "task": task
    }), 201


@tasks_bp.patch("/<task_id>")
@require_auth
def update_task(task_id):
    user_id = request.current_user.id
    data = request.get_json(silent=True) or {}

    # Find the task
    existing_response = (
        supabase
        .table("tasks")
        .select("*")
        .eq("id", task_id)
        .execute()
    )

    existing_tasks = existing_response.data or []

    if not existing_tasks:
        return jsonify({
            "error": "Task not found"
        }), 404

    existing_task = existing_tasks[0]

    # Check authorization
    if (
        existing_task["created_by"] != user_id
        and existing_task["assigned_to"] != user_id
    ):
        return jsonify({
            "error": "You are not authorized to update this task"
        }), 403

    updates = {}

    # Update title
    if "title" in data:
        title = str(data["title"]).strip()

        if not title:
            return jsonify({
                "error": "Task title cannot be empty"
            }), 400

        if len(title) > 200:
            return jsonify({
                "error": "Task title must be 200 characters or less"
            }), 400

        updates["title"] = title

    # Update description
    if "description" in data:
        updates["description"] = data["description"]

    # Update priority
    if "priority" in data:
        allowed_priorities = {
            "LOW",
            "MEDIUM",
            "HIGH",
            "URGENT",
        }

        if data["priority"] not in allowed_priorities:
            return jsonify({
                "error": "Invalid priority"
            }), 400

        updates["priority"] = data["priority"]

    # Update status
    if "status" in data:
        allowed_statuses = {
            "TODO",
            "IN_PROGRESS",
            "COMPLETED",
        }

        if data["status"] not in allowed_statuses:
            return jsonify({
                "error": "Invalid status"
            }), 400

        updates["status"] = data["status"]

        if data["status"] == "COMPLETED":
            updates["completed_at"] = "now()"
        else:
            updates["completed_at"] = None

    # Update due date
    if "due_date" in data:
        updates["due_date"] = data["due_date"]

    # Update assigned user
    if "assigned_to" in data:
        updates["assigned_to"] = data["assigned_to"]

    if not updates:
        return jsonify({
            "error": "No valid fields to update"
        }), 400

    response = (
        supabase
        .table("tasks")
        .update(updates)
        .eq("id", task_id)
        .execute()
    )

    updated_task = response.data[0] if response.data else None

    if not updated_task:
        return jsonify({
            "error": "Failed to update task"
        }), 500

    # Send completion notification to task creator
    if (
        data.get("status") == "COMPLETED"
        and existing_task["status"] != "COMPLETED"
        and existing_task["created_by"] != user_id
    ):
        creator_response = (
            supabase
            .table("profiles")
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
                body=f"""Hi {creator.get("full_name") or "there"},

Your task has been completed in TaskFlow.

Task: {updated_task["title"]}
Priority: {updated_task["priority"]}

The assigned user has marked this task as completed.

— TaskFlow
""",
            )

    return jsonify({
        "task": updated_task
    }), 200


@tasks_bp.delete("/<task_id>")
@require_auth
def delete_task(task_id):
    user_id = request.current_user.id

    # Find the task
    existing_response = (
        supabase
        .table("tasks")
        .select("*")
        .eq("id", task_id)
        .execute()
    )

    existing_tasks = existing_response.data or []

    if not existing_tasks:
        return jsonify({
            "error": "Task not found"
        }), 404

    existing_task = existing_tasks[0]

    # Only creator can delete
    if existing_task["created_by"] != user_id:
        return jsonify({
            "error": "Only the task creator can delete this task"
        }), 403

    (
        supabase
        .table("tasks")
        .delete()
        .eq("id", task_id)
        .execute()
    )

    return jsonify({
        "message": "Task deleted successfully"
    }), 200