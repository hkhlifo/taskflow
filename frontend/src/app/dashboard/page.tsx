"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/supabase/api";

type UserProfile = {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
};

type Task = {
  id: string;
  title: string;
  description: string | null;
  status: "TODO" | "IN_PROGRESS" | "COMPLETED";
  priority: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
  created_by: string;
  assigned_to: string | null;
  due_date: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
};

export default function DashboardPage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<
    "LOW" | "MEDIUM" | "HIGH" | "URGENT"
  >("MEDIUM");
  const [assignedTo, setAssignedTo] = useState("");

  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const userData = await apiFetch("/api/auth/me");
        setUser(userData.user);

        const taskData = await apiFetch("/api/tasks");
        console.log("TASKS:", taskData);
        setTasks(taskData.tasks || []);

        const usersData = await apiFetch("/api/users");
        console.log("USERS:", usersData);
        setUsers(usersData.users || []);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Something went wrong"
        );
      }
    }

    loadDashboard();
  }, []);

  async function completeTask(taskId: string) {
    try {
      setError(null);

      const data = await apiFetch(`/api/tasks/${taskId}`, {
        method: "PATCH",
        body: JSON.stringify({
          status: "COMPLETED",
        }),
      });

      console.log("COMPLETED TASK:", data);

      setTasks((currentTasks) =>
        currentTasks.map((task) =>
          task.id === taskId ? data.task : task
        )
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to complete task"
      );
    }
  }

  async function createTask() {
    if (!title.trim()) {
      setError("Task title is required");
      return;
    }

    try {
      setCreating(true);
      setError(null);
      setSuccess(null);

      const data = await apiFetch("/api/tasks", {
        method: "POST",
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() || null,
          priority,
          assigned_to: assignedTo || null,
        }),
      });

      console.log("CREATED TASK:", data);

      setTasks((currentTasks) => [data.task, ...currentTasks]);

      setTitle("");
      setDescription("");
      setPriority("MEDIUM");
      setAssignedTo("");

      setSuccess("Task created successfully.");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create task"
      );
    } finally {
      setCreating(false);
    }
  }

  if (error && !user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-red-500">{error}</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Loading...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-5xl">
        <h1 className="text-3xl font-bold">
          TaskFlow Dashboard
        </h1>

        <p className="mt-4">
          Logged in as: {user.email}
        </p>

        <p className="mt-2 text-sm text-gray-500">
          Backend authentication successful
        </p>

        {/* Create Task */}
        <div className="mt-8 rounded-xl border bg-white p-6">
          <h2 className="text-xl font-semibold">
            Create Task
          </h2>

          <div className="mt-5 space-y-4">
            <input
              type="text"
              placeholder="Task title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full rounded-lg border px-4 py-3 outline-none focus:ring-2"
            />

            <textarea
              placeholder="Task description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="w-full rounded-lg border px-4 py-3 outline-none focus:ring-2"
            />

            <div className="grid gap-4 md:grid-cols-2">
              <select
                value={priority}
                onChange={(e) =>
                  setPriority(
                    e.target.value as
                    | "LOW"
                    | "MEDIUM"
                    | "HIGH"
                    | "URGENT"
                  )
                }
                className="rounded-lg border px-4 py-3"
              >
                <option value="LOW">Low Priority</option>
                <option value="MEDIUM">Medium Priority</option>
                <option value="HIGH">High Priority</option>
                <option value="URGENT">Urgent</option>
              </select>

              <select
                value={assignedTo}
                onChange={(e) => setAssignedTo(e.target.value)}
                className="rounded-lg border px-4 py-3"
              >
                <option value="">Assign to...</option>

                {users.map((userOption) => (
                  <option key={userOption.id} value={userOption.id}>
                    {userOption.full_name || userOption.email}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={createTask}
              disabled={creating}
              className="rounded-lg bg-black px-6 py-3 font-medium text-white disabled:opacity-50"
            >
              {creating ? "Creating..." : "Create Task"}
            </button>

            {success && (
              <p className="text-sm text-green-600">
                {success}
              </p>
            )}

            {error && (
              <p className="text-sm text-red-500">
                {error}
              </p>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <div className="rounded-xl border bg-white p-6">
            <h2 className="text-xl font-semibold">
              Tasks
            </h2>

            <p className="mt-2 text-gray-500">
              {tasks.length} task{tasks.length !== 1 ? "s" : ""}
            </p>
          </div>

          <div className="rounded-xl border bg-white p-6">
            <h2 className="text-xl font-semibold">
              Users
            </h2>

            <p className="mt-2 text-gray-500">
              {users.length} user{users.length !== 1 ? "s" : ""}
            </p>
          </div>
        </div>

        {/* Tasks */}
        <div className="mt-8 rounded-xl border bg-white p-6">
          <h2 className="text-xl font-semibold">
            Your Tasks
          </h2>

          {tasks.length === 0 ? (
            <p className="mt-4 text-gray-500">
              No tasks yet.
            </p>
          ) : (
            <div className="mt-4 space-y-3">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="rounded-lg border p-4"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">
                      {task.title}
                    </h3>

                    <span className="text-sm text-gray-500">
                      {task.status}
                    </span>
                  </div>

                  {task.description && (
                    <p className="mt-2 text-sm text-gray-600">
                      {task.description}
                    </p>
                  )}

                  <p className="mt-2 text-sm text-gray-500">
                    Priority: {task.priority}
                  </p>

                  {task.status !== "COMPLETED" && (
                    <button
                      onClick={() => completeTask(task.id)}
                      className="mt-3 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white"
                    >
                      Mark as Complete
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}