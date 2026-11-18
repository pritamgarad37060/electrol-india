-- Public source snapshots used to generate the website's cached JSON.
-- Existing election IDs, candidate records and account tables are untouched.
create table if not exists public.website_datasets (
 path text primary key check (path ~ '^/data/[a-zA-Z0-9_./-]+\.json$' and position('..' in path)=0),
 content jsonb not null,
 checksum text not null check (checksum ~ '^[a-f0-9]{64}$'),
 source text not null default 'existing-project-import',
 updated_at timestamptz not null default now()
);
alter table public.website_datasets enable row level security;
revoke all on public.website_datasets from public, anon, authenticated;
grant select on public.website_datasets to anon, authenticated;
grant all on public.website_datasets to service_role;
drop policy if exists website_datasets_public_read on public.website_datasets;
create policy website_datasets_public_read on public.website_datasets for select to anon, authenticated using (true);
comment on table public.website_datasets is 'Public project dataset master. Source imports retain their stated coverage; no private account records. Generate cached JSON with tools/sync-public-data.mjs pull.';
notify pgrst, 'reload schema';
