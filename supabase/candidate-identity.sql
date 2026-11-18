-- Source-scoped identities; legacy primary keys and account relationships are preserved.
begin;
alter table public.candidates add column if not exists candidate_uid uuid;
update public.candidates set candidate_uid=md5('electrol-identity-v1'||chr(31)||'database-candidate'||chr(31)||id::text)::uuid where candidate_uid is null;
alter table public.candidates alter column candidate_uid set default gen_random_uuid();
alter table public.candidates alter column candidate_uid set not null;
create unique index if not exists candidates_candidate_uid_unique on public.candidates(candidate_uid);
create table if not exists public.candidate_identity_registry (
 record_uid uuid primary key,
 source_key text not null unique,
 record_kind text not null check(record_kind in ('result','local','representative')),
 display_name text not null,
 election_level text not null,
 state text,
 body_id text,
 election_year integer,
 seat_key text,
 party text,
 source_path text not null,
 source_url text,
 legacy_key text,
 identity_status text not null default 'source-scoped',
 updated_at timestamptz not null default now()
);
create index if not exists candidate_identity_registry_name on public.candidate_identity_registry(lower(display_name));
create index if not exists candidate_identity_registry_scope on public.candidate_identity_registry(election_level,state,election_year,body_id,seat_key);
create index if not exists candidate_identity_registry_legacy on public.candidate_identity_registry(legacy_key) where legacy_key is not null;
alter table public.candidate_identity_registry enable row level security;
revoke all on public.candidate_identity_registry from public,anon,authenticated;
grant select on public.candidate_identity_registry to anon,authenticated;
grant all on public.candidate_identity_registry to service_role;
drop policy if exists candidate_identity_registry_public_read on public.candidate_identity_registry;
create policy candidate_identity_registry_public_read on public.candidate_identity_registry for select to anon,authenticated using(true);
comment on table public.candidate_identity_registry is 'Public source-record IDs. A candidacy ID identifies a contest entry, not a verified human across elections. Same-name candidates are not merged. Source-scoped does not certify current office.';
commit;
