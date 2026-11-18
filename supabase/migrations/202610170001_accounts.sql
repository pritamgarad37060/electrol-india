-- Additive migration. Apply to a reviewed staging Supabase project first.
-- No election result table is altered or removed.
begin;
create extension if not exists pgcrypto;

create table public.followable_entities (
 id text primary key check(length(id) between 3 and 240),
 kind text not null check(kind in ('person','office','state','district','constituency','city','ward','body','ministry','portfolio','party','election','administration','country')),
 name text not null check(length(name) between 1 and 300),
 url text not null check(url ~ '^/[^/]' or url='/'),
 subtitle text, parent_id text references public.followable_entities(id),
 metadata jsonb not null default '{}', active boolean not null default true
);
create index entity_kind_name on public.followable_entities(kind,name);
create table public.entity_aliases(alias text primary key, entity_id text not null references public.followable_entities(id) on delete cascade);

create table public.profiles (
 id uuid primary key references auth.users(id) on delete cascade,
 display_name text not null default '' check(length(display_name)<=100),
 avatar_url text check(avatar_url is null or (length(avatar_url)<=2048 and avatar_url ~ '^https://')),
 preferred_state text references public.followable_entities(id),
 preferred_constituency text references public.followable_entities(id),
 language text not null default 'en' check(language in ('en','mr','hi')),
 theme text not null default 'system' check(theme in ('light','dark','system')),
 created_at timestamptz not null default now(), deletion_requested_at timestamptz
);
create table public.account_sessions (
 id uuid primary key, user_id uuid not null references auth.users(id) on delete cascade,
 browser text not null default 'Browser', created_at timestamptz not null default now(),
 last_seen_at timestamptz not null default now(), revoked_at timestamptz
);
create index sessions_user on public.account_sessions(user_id);
create function public.active_account() returns boolean language sql stable security definer set search_path='' as $$
 select auth.uid() is not null and exists(select 1 from public.account_sessions s where s.id=(auth.jwt()->>'session_id')::uuid and s.user_id=auth.uid() and s.revoked_at is null)
$$;
create function public.create_profile() returns trigger language plpgsql security definer set search_path='' as $$
begin
 insert into public.profiles(id,display_name) values(new.id,left(coalesce(new.raw_user_meta_data->>'display_name',''),100)) on conflict do nothing;
 return new;
end $$;
create trigger auth_user_profile after insert on auth.users for each row execute function public.create_profile();

create table public.user_follows (
 user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
 entity_id text not null references public.followable_entities(id), followed_at timestamptz not null default now(),
 muted boolean not null default false,
 alert_types text[] not null default array['elections','representatives','government','news'],
 primary key(user_id,entity_id), check(alert_types <@ array['elections','representatives','government','news']::text[])
);
create index follows_entity on public.user_follows(entity_id,user_id);
create table public.notification_preferences (
 user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
 in_app boolean not null default true, email boolean not null default false,
 push boolean not null default false, security_email boolean not null default true,
 frequency text not null default 'important' check(frequency in ('important','instant','daily','weekly','off')),
 categories text[] not null default array['elections','representatives','government','news'],
 timezone text not null default 'Asia/Kolkata' check(timezone in ('Asia/Kolkata','UTC')),
 consented_at timestamptz,
 check(categories <@ array['elections','representatives','government','news']::text[])
);
create table public.update_sources (
 id uuid primary key default gen_random_uuid(), name text not null check(length(name)<=200),
 url text unique not null check(url ~ '^https://'),
 source_type text not null check(source_type in ('official','news')),
 format text not null default 'jsonfeed' check(format='jsonfeed'),
 enabled boolean not null default false, permission_note text not null default '',
 last_checked_at timestamptz, last_error text
);
create table public.updates (
 id uuid primary key default gen_random_uuid(), source_id uuid references public.update_sources(id),
 canonical_url text not null unique check(length(canonical_url)<=2048 and canonical_url ~ '^https://'),
 title text not null check(length(title) between 1 and 300), summary text not null default '' check(length(summary)<=600),
 source_type text not null check(source_type in ('official','news','correction')),
 category text not null check(category in ('elections','representatives','government','news')),
 published_at timestamptz not null, ingested_at timestamptz not null default now(),
 important boolean not null default false, status text not null default 'pending' check(status in ('pending','published','rejected')),
 reviewed_by uuid references auth.users(id) on delete set null, reviewed_at timestamptz
);
create index updates_published on public.updates(published_at desc) where status='published';
create table public.update_entities (
 update_id uuid not null references public.updates(id) on delete cascade,
 entity_id text not null references public.followable_entities(id),
 approved boolean not null default false, primary key(update_id,entity_id)
);
create index update_entity_lookup on public.update_entities(entity_id,update_id) where approved;
create table public.scheduled_elections (
 id uuid primary key default gen_random_uuid(), entity_id text not null references public.followable_entities(id),
 name text not null, event_type text not null check(event_type in ('nomination','polling','counting','results')),
 event_at timestamptz not null, source_url text not null check(source_url ~ '^https://'),
 approved boolean not null default false, unique(entity_id,event_type,event_at)
);
create table public.notifications (
 id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
 update_id uuid references public.updates(id) on delete cascade,
 category text not null check(category in ('elections','representatives','government','news','security')),
 title text not null check(length(title)<=300), url text not null default '/account/notifications/' check(url ~ '^/[^/]' or url ~ '^https://'),
 created_at timestamptz not null default now(), deliver_after timestamptz not null default now(),
 read_at timestamptz, archived_at timestamptz, dedupe_key text not null,
 unique(user_id,dedupe_key)
);
create index notifications_unread on public.notifications(user_id,deliver_after desc) where read_at is null and archived_at is null;
create table public.notification_deliveries (
 id uuid primary key default gen_random_uuid(), notification_id uuid not null references public.notifications(id) on delete cascade,
 channel text not null check(channel in ('email','push')), status text not null default 'pending' check(status in ('pending','processing','sent','failed','blocked')),
 attempts integer not null default 0, next_attempt_at timestamptz not null default now(), lease_until timestamptz,
 provider_id text, last_error text, idempotency_key uuid not null default gen_random_uuid() unique,
 unique(notification_id,channel)
);
create table public.push_subscriptions (
 id uuid primary key default gen_random_uuid(), user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
 endpoint text not null check(endpoint ~ '^https://' and length(endpoint)<2048),
 keys jsonb not null, created_at timestamptz not null default now(), unique(user_id,endpoint)
);
create table public.saved_searches (
 id uuid primary key default gen_random_uuid(), user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
 name text not null check(length(name) between 1 and 100), url text not null check(url ~ '^/[^/]'),
 filters jsonb not null default '{}' check(octet_length(filters::text)<12000), created_at timestamptz not null default now()
);
create table public.bookmarks (
 user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
 update_id uuid not null references public.updates(id) on delete cascade, created_at timestamptz not null default now(), primary key(user_id,update_id)
);
create table public.hidden_updates (
 user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
 update_id uuid not null references public.updates(id) on delete cascade, primary key(user_id,update_id)
);
create table public.security_audit_events (
 id bigint generated always as identity primary key, user_id uuid references auth.users(id) on delete set null,
 event_type text not null check(length(event_type)<=100), success boolean not null,
 created_at timestamptz not null default now(), detail jsonb not null default '{}'
);
create index audit_user_date on public.security_audit_events(user_id,created_at desc);
create table public.staff_roles(user_id uuid primary key references auth.users(id) on delete cascade, role text not null check(role in ('reviewer','operator','admin','owner')));
create table public.account_rate_limits(key text not null, bucket timestamptz not null, attempts integer not null, primary key(key,bucket));

create function public.account_staff() returns boolean language sql stable security definer set search_path='' as $$
 select public.active_account() and auth.jwt()->>'aal'='aal2' and exists(select 1 from public.staff_roles where user_id=auth.uid())
$$;
-- Explicit RLS on every table; policies never use browser-supplied identity.
do $$ declare t text; begin
 foreach t in array array['followable_entities','entity_aliases','profiles','account_sessions','user_follows','notification_preferences','update_sources','updates','update_entities','scheduled_elections','notifications','notification_deliveries','push_subscriptions','saved_searches','bookmarks','hidden_updates','security_audit_events','staff_roles','account_rate_limits'] loop
  execute format('alter table public.%I enable row level security',t);
 end loop;
end $$;
create policy entity_public_read on public.followable_entities for select to anon,authenticated using(active);
create policy alias_public_read on public.entity_aliases for select to anon,authenticated using(true);
create policy profile_read on public.profiles for select to authenticated using(id=auth.uid() and public.active_account());
create policy profile_update on public.profiles for update to authenticated using(id=auth.uid() and public.active_account()) with check(id=auth.uid() and public.active_account());
create policy sessions_read on public.account_sessions for select to authenticated using(user_id=auth.uid() and public.active_account());
do $$ declare t text; begin
 foreach t in array array['user_follows','notification_preferences','push_subscriptions','saved_searches','bookmarks','hidden_updates'] loop
  execute format('create policy own_select on public.%I for select to authenticated using(user_id=auth.uid() and public.active_account())',t);
  execute format('create policy own_insert on public.%I for insert to authenticated with check(user_id=auth.uid() and public.active_account())',t);
  execute format('create policy own_update on public.%I for update to authenticated using(user_id=auth.uid() and public.active_account()) with check(user_id=auth.uid() and public.active_account())',t);
  execute format('create policy own_delete on public.%I for delete to authenticated using(user_id=auth.uid() and public.active_account())',t);
 end loop;
end $$;
create policy published_updates on public.updates for select to anon,authenticated using(status='published' or public.account_staff());
create policy published_matches on public.update_entities for select to anon,authenticated using(exists(select 1 from public.updates u where u.id=update_id and (u.status='published' or public.account_staff())));
create policy published_schedule on public.scheduled_elections for select to anon,authenticated using(approved);
create policy notification_read on public.notifications for select to authenticated using(user_id=auth.uid() and public.active_account() and deliver_after<=now());
create policy notification_update on public.notifications for update to authenticated using(user_id=auth.uid() and public.active_account() and deliver_after<=now()) with check(user_id=auth.uid() and public.active_account());
create policy audit_read on public.security_audit_events for select to authenticated using(user_id=auth.uid() and public.active_account());
create policy role_read on public.staff_roles for select to authenticated using(user_id=auth.uid() and public.active_account());
create policy sources_staff_read on public.update_sources for select to authenticated using(public.account_staff());
-- No client policies exist for rate limits or delivery writes.
revoke all on public.followable_entities,public.entity_aliases,public.profiles,public.account_sessions,public.user_follows,public.notification_preferences,public.update_sources,public.updates,public.update_entities,public.scheduled_elections,public.notifications,public.notification_deliveries,public.push_subscriptions,public.saved_searches,public.bookmarks,public.hidden_updates,public.security_audit_events,public.staff_roles,public.account_rate_limits from anon,authenticated;
grant select on public.followable_entities,public.entity_aliases,public.updates,public.update_entities,public.scheduled_elections to anon,authenticated;
grant select on public.profiles,public.account_sessions,public.notifications,public.security_audit_events,public.staff_roles,public.update_sources to authenticated;
grant update(display_name,avatar_url,preferred_state,preferred_constituency,language,theme) on public.profiles to authenticated;
grant update(read_at,archived_at) on public.notifications to authenticated;
grant select,insert,update,delete on public.user_follows,public.notification_preferences,public.push_subscriptions,public.saved_searches,public.bookmarks,public.hidden_updates to authenticated;
grant all on public.followable_entities,public.entity_aliases,public.profiles,public.account_sessions,public.user_follows,public.notification_preferences,public.update_sources,public.updates,public.update_entities,public.scheduled_elections,public.notifications,public.notification_deliveries,public.push_subscriptions,public.saved_searches,public.bookmarks,public.hidden_updates,public.security_audit_events,public.staff_roles,public.account_rate_limits to service_role;
grant usage,select on sequence public.security_audit_events_id_seq to service_role;

create function public.register_account_session(p_user uuid,p_session uuid,p_browser text) returns boolean language plpgsql security definer set search_path='' as $$
declare ok boolean; begin
 insert into public.account_sessions(id,user_id,browser) values(p_session,p_user,left(p_browser,160)) on conflict(id) do update set last_seen_at=now() where public.account_sessions.user_id=p_user;
 select revoked_at is null into ok from public.account_sessions where id=p_session and user_id=p_user;
 return coalesce(ok,false);
end $$;
create function public.revoke_account_sessions(p_all boolean default false,p_session uuid default null) returns void language plpgsql security definer set search_path='' as $$
begin
 if not public.active_account() then raise exception 'not authorized'; end if;
 update public.account_sessions set revoked_at=now() where user_id=auth.uid() and (p_all or id=coalesce(p_session,(auth.jwt()->>'session_id')::uuid));
end $$;
create function public.consume_account_rate(p_key text,p_limit integer,p_seconds integer) returns boolean language plpgsql security definer set search_path='' as $$
declare n integer;b timestamptz;begin
 if p_limit<1 or p_seconds<1 then return false;end if;
 b=to_timestamp(floor(extract(epoch from now())/p_seconds)*p_seconds);
 insert into public.account_rate_limits(key,bucket,attempts) values(p_key,b,1) on conflict(key,bucket) do update set attempts=public.account_rate_limits.attempts+1 returning attempts into n;
 return n<=p_limit;
end $$;
create function public.account_feed(p_category text default null,p_offset integer default 0,p_limit integer default 20) returns jsonb language sql stable security invoker set search_path='' as $$
 select coalesce(jsonb_agg(to_jsonb(r)),'[]'::jsonb) from (
  select u.*,exists(select 1 from public.bookmarks b where b.user_id=auth.uid() and b.update_id=u.id) as bookmarked
  from public.updates u where public.active_account() and u.status='published' and (p_category is null or u.category=p_category)
  and not exists(select 1 from public.hidden_updates h where h.user_id=auth.uid() and h.update_id=u.id)
  and exists(select 1 from public.update_entities ue join public.user_follows f on f.entity_id=ue.entity_id where ue.update_id=u.id and ue.approved and f.user_id=auth.uid() and not f.muted)
  order by u.published_at desc,u.id limit least(greatest(p_limit,1),50) offset greatest(p_offset,0)
 ) r
$$;
create function public.account_summary() returns jsonb language sql stable security invoker set search_path='' as $$
 select jsonb_build_object(
 'total_follows',(select count(*) from public.user_follows where user_id=auth.uid()),
 'people',(select count(*) from public.user_follows f join public.followable_entities e on e.id=f.entity_id where f.user_id=auth.uid() and e.kind='person'),
 'constituencies',(select count(*) from public.user_follows f join public.followable_entities e on e.id=f.entity_id where f.user_id=auth.uid() and e.kind='constituency'),
 'unread',(select count(*) from public.notifications where user_id=auth.uid() and read_at is null and archived_at is null and deliver_after<=now()),
 'new_updates',(select count(*) from public.updates u where u.status='published' and u.published_at>=now()-interval '7 days' and not exists(select 1 from public.hidden_updates h where h.user_id=auth.uid() and h.update_id=u.id) and exists(select 1 from public.update_entities ue join public.user_follows f on f.entity_id=ue.entity_id where ue.update_id=u.id and ue.approved and f.user_id=auth.uid() and not f.muted)),
 'upcoming',(select count(*) from public.scheduled_elections s where s.approved and s.event_at>now() and exists(select 1 from public.user_follows f where f.entity_id=s.entity_id and f.user_id=auth.uid()))) where public.active_account()
$$;
create function public.generate_update_notifications(p_update uuid) returns integer language plpgsql security definer set search_path='' as $$
declare n integer;begin
 insert into public.notifications(user_id,update_id,category,title,url,dedupe_key,deliver_after)
 select distinct f.user_id,u.id,u.category,u.title,u.canonical_url,'update:'||u.id,
 case coalesce(p.frequency,'important') when 'daily' then ((date_trunc('day',now() at time zone coalesce(p.timezone,'Asia/Kolkata'))+interval '1 day 9 hours') at time zone coalesce(p.timezone,'Asia/Kolkata')) when 'weekly' then ((date_trunc('week',now() at time zone coalesce(p.timezone,'Asia/Kolkata'))+interval '7 days 9 hours') at time zone coalesce(p.timezone,'Asia/Kolkata')) else now() end
 from public.updates u join public.update_entities ue on ue.update_id=u.id and ue.approved join public.user_follows f on f.entity_id=ue.entity_id left join public.notification_preferences p on p.user_id=f.user_id
 where u.id=p_update and u.status='published' and not f.muted and u.category=any(f.alert_types) and coalesce(p.in_app,true) and u.category=any(coalesce(p.categories,array['elections','representatives','government','news'])) and coalesce(p.frequency,'important')<>'off' and (coalesce(p.frequency,'important')<>'important' or u.important)
 on conflict(user_id,dedupe_key) do nothing;
 get diagnostics n=row_count;
 insert into public.notification_deliveries(notification_id,channel,next_attempt_at)
 select n.id,'email',n.deliver_after from public.notifications n join public.notification_preferences p on p.user_id=n.user_id where n.update_id=p_update and p.email and p.consented_at is not null on conflict(notification_id,channel) do nothing;
 return n;
end $$;
create function public.record_account_security(p_user uuid,p_event text,p_success boolean) returns void language plpgsql security definer set search_path='' as $$
begin
 insert into public.security_audit_events(user_id,event_type,success) values(p_user,left(p_event,100),p_success);
 if p_user is not null and p_success then
 insert into public.notifications(user_id,category,title,url,dedupe_key) values(p_user,'security',left(replace(p_event,'_',' '),300),'/account/security/','security:'||gen_random_uuid());
 end if;
end $$;
create function public.account_admin_health() returns jsonb language plpgsql stable security definer set search_path='' as $$
begin
 if not public.account_staff() then raise exception 'not authorized'; end if;
 return jsonb_build_object('users',(select count(*) from public.profiles),'pending_updates',(select count(*) from public.updates where status='pending'),'failed_deliveries',(select count(*) from public.notification_deliveries where status in ('failed','blocked')),'enabled_sources',(select count(*) from public.update_sources where enabled),'security_events_24h',(select count(*) from public.security_audit_events where created_at>now()-interval '1 day'));
end $$;

-- Default EXECUTE is PUBLIC in PostgreSQL: revoke it explicitly for every RPC.
revoke all on function public.create_profile() from public,anon,authenticated;
revoke all on function public.register_account_session(uuid,uuid,text),public.consume_account_rate(text,integer,integer),public.generate_update_notifications(uuid),public.record_account_security(uuid,text,boolean) from public,anon,authenticated;
grant execute on function public.register_account_session(uuid,uuid,text),public.consume_account_rate(text,integer,integer),public.generate_update_notifications(uuid),public.record_account_security(uuid,text,boolean) to service_role;
revoke all on function public.active_account(),public.account_staff(),public.revoke_account_sessions(boolean,uuid),public.account_feed(text,integer,integer),public.account_summary(),public.account_admin_health() from public,anon;
grant execute on function public.active_account(),public.account_staff() to anon,authenticated;
grant execute on function public.revoke_account_sessions(boolean,uuid),public.account_feed(text,integer,integer),public.account_summary(),public.account_admin_health() to authenticated;
commit;
