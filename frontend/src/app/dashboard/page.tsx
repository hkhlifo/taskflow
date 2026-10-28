
"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/supabase/api";

type TaskStatus = "TODO" | "IN_PROGRESS" | "COMPLETED";
type TaskPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";

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
  status: TaskStatus;
  priority: TaskPriority;
  created_by: string;
  assigned_to: string | null;
  due_date: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
};

const DEFAULT_ERROR = "Something went wrong. Please try again.";

const PRIORITY_OPTIONS: { value: TaskPriority; label: string }[] = [
  { value: "LOW", label: "Low Priority" },
  { value: "MEDIUM", label: "Medium Priority" },
  { value: "HIGH", label: "High Priority" },
  { value: "URGENT", label: "Urgent" },
];

function getErrorMessage(error: unknown, fallback = DEFAULT_ERROR): string {
  return error instanceof Error ? error.message : fallback;
}

function getPluralLabel(count: number, singular: string): string {
  return `${count} ${singular}${count !== 1 ? "s" : ""}`;
}

export default function DashboardPage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("MEDIUM");
  const [assignedTo, setAssignedTo] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [completingTaskId, setCompletingTaskId] = useState<string | null>(
    null
  );

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [userData, taskData, usersData] = await Promise.all([
          apiFetch("/api/auth/me"),
          apiFetch("/api/tasks"),
          apiFetch("/api/users"),
        ]);

        setUser(userData.user);
        setTasks(taskData.tasks ?? []);
        setUsers(usersData.users ?? []);
      } catch (error) {
        setError(getErrorMessage(error));
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, []);

  async function handleCompleteTask(taskId: string) {
    try {
      setError(null);
      setSuccess(null);
      setCompletingTaskId(taskId);

      const data = await apiFetch(`/api/tasks/${taskId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: "COMPLETED" }),
      });

      setTasks((currentTasks) =>
        currentTasks.map((task) =>
          task.id === taskId ? data.task : task
        )
      );

      setSuccess("Task marked as completed.");
    } catch (error) {
      setError(getErrorMessage(error, "Failed to complete task."));
    } finally {
      setCompletingTaskId(null);
    }
  }

  async function handleCreateTask() {
    const trimmedTitle = title.trim();

    if (!trimmedTitle) {
      setError("Task title is required.");
      setSuccess(null);
      return;
    }

    try {
      setIsCreating(true);
      setError(null);
      setSuccess(null);

      const data = await apiFetch("/api/tasks", {
        method: "POST",
        body: JSON.stringify({
          title: trimmedTitle,
          description: description.trim() || null,
          priority,
          assigned_to: assignedTo || null,
        }),
      });

      setTasks((currentTasks) => [data.task, ...currentTasks]);

      setTitle("");
      setDescription("");
      setPriority("MEDIUM");
      setAssignedTo("");

      setSuccess("Task created successfully.");
    } catch (error) {
      setError(getErrorMessage(error, "Failed to create task."));
    } finally {
      setIsCreating(false);
    }
  }

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading dashboard...</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <p className="text-red-500" role="alert">
          {error ?? "Unable to load your profile. Please try again."}
        </p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-4 sm:p-8">
      <div className="mx-auto max-w-5xl">
        <header>
          <h1 className="text-3xl font-bold">TaskFlow Dashboard</h1>

          <p className="mt-4 text-gray-700">
            Logged in as: {user.email}
          </p>

          <p className="mt-2 text-sm text-gray-500">
            Backend authentication successful
          </p>
        </header>

        <section
          aria-labelledby="create-task-heading"
          className="mt-8 rounded-xl border bg-white p-6"
        >
          <h2 id="create-task-heading" className="text-xl font-semibold">
            Create Task
          </h2>

          <form
            className="mt-5 space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              void handleCreateTask();
            }}
          >
            <input
              type="text"
              placeholder="Task title"
              aria-label="Task title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              required
              className="w-full rounded-lg border px-4 py-3 outline-none focus:ring-2 focus:ring-black"
            />

            <textarea
              placeholder="Task description"
              aria-label="Task description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={4}
              className="w-full rounded-lg border px-4 py-3 outline-none focus:ring-2 focus:ring-black"
            />

            <div className="grid gap-4 md:grid-cols-2">
              <select
                aria-label="Task priority"
                value={priority}
                onChange={(event) =>
                  setPriority(event.target.value as TaskPriority)
                }
                className="rounded-lg border px-4 py-3"
              >
                {PRIORITY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              <select
                aria-label="Assign task to"
                value={assignedTo}
                onChange={(event) => setAssignedTo(event.target.value)}
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
              type="submit"
              disabled={isCreating}
              className="rounded-lg bg-black px-6 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isCreating ? "Creating..." : "Create Task"}
            </button>
          </form>
        </section>

        <section
          aria-label="Dashboard statistics"
          className="mt-8 grid gap-6 md:grid-cols-2"
        >
          <div className="rounded-xl border bg-white p-6">
            <h2 className="text-xl font-semibold">Tasks</h2>
            <p className="mt-2 text-gray-500">
              {getPluralLabel(tasks.length, "task")}
            </p>
          </div>

          <div className="rounded-xl border bg-white p-6">
            <h2 className="text-xl font-semibold">Users</h2>
            <p className="mt-2 text-gray-500">
              {getPluralLabel(users.length, "user")}
            </p>
          </div>
        </section>

        <section
          aria-labelledby="tasks-heading"
          className="mt-8 rounded-xl border bg-white p-6"
        >
          <h2 id="tasks-heading" className="text-xl font-semibold">
            Your Tasks
          </h2>

          {tasks.length === 0 ? (
            <p className="mt-4 text-gray-500">No tasks yet.</p>
          ) : (
            <ul className="mt-4 space-y-3">
              {tasks.map((task) => (
                <li key={task.id} className="rounded-lg border p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h3 className="font-semibold">{task.title}</h3>

                    <span className="text-sm text-gray-500">
                      {task.status.replaceAll("_", " ")}
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
                      type="button"
                      onClick={() => void handleCompleteTask(task.id)}
                      disabled={completingTaskId !== null}
                      className="mt-3 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {completingTaskId === task.id
                        ? "Completing..."
                        : "Mark as Complete"}
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        {(error || success) && (
          <div className="mt-6 space-y-2" aria-live="polite">
            {error && (
              <p className="text-sm text-red-600" role="alert">
                {error}
              </p>
            )}

            {success && (
              <p className="text-sm text-green-600">{success}</p>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
