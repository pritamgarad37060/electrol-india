alter table public.profiles
 add column interest_topics text[] not null default '{}',
 add column interest_content_types text[] not null default '{}',
 add column interest_entities text[] not null default '{}',
 add column social_links jsonb not null default '{}';
grant update(interest_topics,interest_content_types,interest_entities,social_links) on public.profiles to authenticated;
alter table public.notification_preferences
 add column quiet_enabled boolean not null default false,
 add column quiet_start time not null default '22:00',
 add column quiet_end time not null default '07:00',
 add column quiet_days integer[] not null default array[0,1,2,3,4,5,6],
 add column date_format text not null default 'DD MMM YYYY' check(date_format in ('DD MMM YYYY','DD/MM/YYYY','MM/DD/YYYY','YYYY-MM-DD')),
 add column time_format text not null default '12' check(time_format in ('12','24'));
alter table public.notification_preferences add constraint quiet_days_valid check(quiet_days <@ array[0,1,2,3,4,5,6]::integer[]);
alter table public.updates add column content_type text not null default 'news' check(content_type in ('news','analysis','profiles','results','policies','interviews')),
 add column image_url text check(image_url is null or (length(image_url)<=2048 and image_url ~ '^https://'));
create table public.saved_profiles(
 user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
 entity_id text not null references public.followable_entities(id),created_at timestamptz not null default now(),
 primary key(user_id,entity_id));
alter table public.saved_profiles enable row level security;
grant select,insert,delete on public.saved_profiles to authenticated;
create policy saved_profile_read on public.saved_profiles for select to authenticated using(user_id=(select auth.uid()) and public.active_account());
create policy saved_profile_insert on public.saved_profiles for insert to authenticated with check(user_id=(select auth.uid()) and public.active_account());
create policy saved_profile_delete on public.saved_profiles for delete to authenticated using(user_id=(select auth.uid()) and public.active_account());
create function public.account_delivery_time(p_when timestamptz,p_user uuid) returns timestamptz language plpgsql stable security invoker set search_path='' as $$
declare p public.notification_preferences; local_time timestamp; day_no integer; t time;
begin
 select * into p from public.notification_preferences where user_id=p_user;
 if not found or not p.quiet_enabled or p.quiet_start=p.quiet_end then return p_when;end if;
 local_time:=p_when at time zone p.timezone; day_no:=extract(dow from local_time)::integer;t:=local_time::time;
 if p.quiet_start<p.quiet_end then
  if day_no=any(p.quiet_days) and t>=p.quiet_start and t<p.quiet_end then return (local_time::date+p.quiet_end) at time zone p.timezone;end if;
 else
  if day_no=any(p.quiet_days) and t>=p.quiet_start then return (local_time::date+1+p.quiet_end) at time zone p.timezone;end if;
  if ((day_no+6)%7)=any(p.quiet_days) and t<p.quiet_end then return (local_time::date+p.quiet_end) at time zone p.timezone;end if;
 end if;return p_when;
end $$;
revoke all on function public.account_delivery_time(timestamptz,uuid) from public,anon;
grant execute on function public.account_delivery_time(timestamptz,uuid) to authenticated,service_role;
create or replace function public.account_feed(p_category text default null,p_offset integer default 0,p_limit integer default 20) returns jsonb language sql stable security invoker set search_path='' as $$
 select coalesce(jsonb_agg(to_jsonb(r)),'[]'::jsonb) from (
 select u.*,exists(select 1 from public.bookmarks b where b.user_id=auth.uid() and b.update_id=u.id) as bookmarked
 from public.updates u join public.profiles p on p.id=(select auth.uid())
 where public.active_account() and u.status='published' and (p_category is null or u.category=p_category)
 and (cardinality(p.interest_content_types)=0 or u.content_type=any(p.interest_content_types))
 and not exists(select 1 from public.hidden_updates h where h.user_id=auth.uid() and h.update_id=u.id)
 and exists(select 1 from public.update_entities ue join public.followable_entities e on e.id=ue.entity_id
 where ue.update_id=u.id and ue.approved and
 (exists(select 1 from public.user_follows f where f.entity_id=e.id and f.user_id=auth.uid() and not f.muted)
 or e.id=any(p.interest_entities) or e.parent_id=any(p.interest_entities))
 and (cardinality(p.interest_topics)=0 or
 ('general'=any(p.interest_topics) and e.id like 'election:ls:%') or
 ('assembly'=any(p.interest_topics) and e.id like 'election:assembly:%') or
 ('mlc'=any(p.interest_topics) and (e.id like 'election:mlc:%' or e.name ilike '%MLC%')) or
 ('local'=any(p.interest_topics) and e.kind in ('body','ward','city','district')) or
 ('municipal'=any(p.interest_topics) and e.id like 'body:%corp%') or
 ('panchayat'=any(p.interest_topics) and (e.id like '%panchayat%' or e.id like '%zilla%'))))
 order by u.published_at desc,u.id limit least(greatest(p_limit,1),50) offset greatest(p_offset,0))r
$$;
