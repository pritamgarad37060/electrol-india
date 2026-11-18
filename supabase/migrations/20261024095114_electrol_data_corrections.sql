-- Additive schema only. Existing election/account tables are preserved.
begin;
create table if not exists public.data_corrections (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 page_url text not null check (left(page_url,1)='/' and left(page_url,2)<>'//' and length(page_url)<=2048),
 category text not null check (category in ('result','identity','boundary','other')),
 description text not null check (length(description) between 20 and 4000),
 source_url text check (source_url is null or length(source_url)<=2048),
 status text not null default 'pending' check (status in ('pending','reviewing','resolved','dismissed')),
 created_at timestamptz not null default now()
);
create index if not exists data_corrections_user_created on public.data_corrections(user_id,created_at desc);
alter table public.data_corrections enable row level security;
revoke all on public.data_corrections from anon,authenticated;
grant select,insert on public.data_corrections to authenticated;
grant all on public.data_corrections to service_role;
drop policy if exists corrections_own_select on public.data_corrections;
create policy corrections_own_select on public.data_corrections for select to authenticated using ((select auth.uid())=user_id);
drop policy if exists corrections_own_insert on public.data_corrections;
create policy corrections_own_insert on public.data_corrections for insert to authenticated with check ((select auth.uid())=user_id and status='pending');
commit;
