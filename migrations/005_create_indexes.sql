create index idx_tasks_created_by
on public.tasks(created_by);

create index idx_tasks_assigned_to
on public.tasks(assigned_to);

create index idx_tasks_status
on public.tasks(status);

create index idx_tasks_due_date
on public.tasks(due_date);

create index idx_task_activity_task_id
on public.task_activity(task_id);

create index idx_email_notifications_recipient
on public.email_notifications(recipient_id);
