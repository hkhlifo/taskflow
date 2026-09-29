create table public.task_activity (
    id uuid primary key default gen_random_uuid(),

    task_id uuid not null
        references public.tasks(id) on delete cascade,

    user_id uuid not null
        references public.profiles(id) on delete cascade,

    action text not null,

    metadata jsonb,

    created_at timestamptz not null default now()
);
