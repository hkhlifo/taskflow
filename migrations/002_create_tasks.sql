create table public.tasks (
    id uuid primary key default gen_random_uuid(),

    title text not null,
    description text,

    status text not null default 'TODO',
    priority text not null default 'MEDIUM',

    created_by uuid not null
        references public.profiles(id) on delete cascade,

    assigned_to uuid
        references public.profiles(id) on delete set null,

    due_date timestamptz,

    completed_at timestamptz,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint tasks_status_check
        check (status in ('TODO', 'IN_PROGRESS', 'COMPLETED')),

    constraint tasks_priority_check
        check (priority in ('LOW', 'MEDIUM', 'HIGH', 'URGENT'))
);
