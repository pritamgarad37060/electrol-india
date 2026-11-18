begin;
-- Trigram indexes for fast fuzzy entity searches in followable_entities and updates.
-- Supports ILIKE %query% pattern matching using PostgreSQL GIN index with gin_trgm_ops.
create extension if not exists pg_trgm;

create index if not exists idx_entities_name_trgm on public.followable_entities using gin (name gin_trgm_ops);
create index if not exists idx_entities_subtitle_trgm on public.followable_entities using gin (subtitle gin_trgm_ops);
create index if not exists idx_updates_title_trgm on public.updates using gin (title gin_trgm_ops);

commit;
