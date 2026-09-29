create table public.email_notifications (
    id uuid primary key default gen_random_uuid(),

    task_id uuid
        references public.tasks(id) on delete cascade,

    recipient_id uuid not null
        references public.profiles(id) on delete cascade,

    event_type text not null,

    status text not null default 'PENDING',

    error_message text,

    sent_at timestamptz,

    created_at timestamptz not null default now(),

    constraint email_notification_event_check
        check (
            event_type in (
                'TASK_CREATED',
                'TASK_COMPLETED'
            )
        ),

    constraint email_notification_status_check
        check (
            status in (
                'PENDING',
                'SENT',
                'FAILED'
            )
        )
);
