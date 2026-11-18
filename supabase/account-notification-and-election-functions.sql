create function public.account_elections(p_status text default null,p_query text default '',p_offset integer default 0) returns jsonb language sql stable security invoker set search_path='' as $$
with entries as (
 select f.entity_id,f.muted,f.alert_types,f.followed_at,to_jsonb(e) entity,
 case when e.metadata->>'status' in ('upcoming','ongoing','completed') then e.metadata->>'status'
 when ev.first_event>now() then 'upcoming'
 when ev.last_event>=now() and ev.first_event<=now() then 'ongoing'
 when ev.result_event<now() or coalesce(e.subtitle,'') ilike '%snapshot%' then 'completed'
 else 'unknown' end status,ev.first_event,ev.last_event
 from public.user_follows f join public.followable_entities e on e.id=f.entity_id
 left join lateral(select min(event_at) first_event,max(event_at) last_event,max(event_at) filter(where event_type='results') result_event from public.scheduled_elections where entity_id=e.id and approved) ev on true
 where f.user_id=(select auth.uid()) and public.active_account() and e.kind='election'),
 filtered as(select * from entries where (p_status is null or status=p_status) and (p_query='' or entity->>'name' ilike '%'||p_query||'%')),
 result_rows as(select * from filtered order by first_event asc nulls last,followed_at desc,entity_id limit 21 offset greatest(p_offset,0))
select jsonb_build_object('rows',coalesce((select jsonb_agg(to_jsonb(r)) from result_rows r),'[]'::jsonb),'counts',coalesce((select jsonb_object_agg(status,n) from(select status,count(*) n from entries group by status)c),'{}'::jsonb))
$$;
revoke all on function public.account_elections(text,text,integer) from public,anon;
grant execute on function public.account_elections(text,text,integer) to authenticated;

CREATE OR REPLACE FUNCTION public.generate_update_notifications(p_update uuid)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
declare n integer;begin
 insert into public.notifications(user_id,update_id,category,title,url,dedupe_key,deliver_after)
 select distinct f.user_id,u.id,u.category,u.title,u.canonical_url,'update:'||u.id,
 case when u.important then case coalesce(p.frequency,'important') when 'daily' then ((date_trunc('day',now() at time zone coalesce(p.timezone,'Asia/Kolkata'))+interval '1 day 9 hours') at time zone coalesce(p.timezone,'Asia/Kolkata')) when 'weekly' then ((date_trunc('week',now() at time zone coalesce(p.timezone,'Asia/Kolkata'))+interval '7 days 9 hours') at time zone coalesce(p.timezone,'Asia/Kolkata')) else now() end else public.account_delivery_time(case coalesce(p.frequency,'important') when 'daily' then ((date_trunc('day',now() at time zone coalesce(p.timezone,'Asia/Kolkata'))+interval '1 day 9 hours') at time zone coalesce(p.timezone,'Asia/Kolkata')) when 'weekly' then ((date_trunc('week',now() at time zone coalesce(p.timezone,'Asia/Kolkata'))+interval '7 days 9 hours') at time zone coalesce(p.timezone,'Asia/Kolkata')) else now() end,f.user_id) end
 from public.updates u join public.update_entities ue on ue.update_id=u.id and ue.approved join public.user_follows f on f.entity_id=ue.entity_id left join public.notification_preferences p on p.user_id=f.user_id
 where u.id=p_update and u.status='published' and not f.muted and u.category=any(f.alert_types) and coalesce(p.in_app,true) and u.category=any(coalesce(p.categories,array['elections','representatives','government','news'])) and coalesce(p.frequency,'important')<>'off' and (coalesce(p.frequency,'important')<>'important' or u.important)
 on conflict(user_id,dedupe_key) do nothing;
 get diagnostics n=row_count;
 insert into public.notification_deliveries(notification_id,channel,next_attempt_at)
 select n.id,'email',n.deliver_after from public.notifications n join public.notification_preferences p on p.user_id=n.user_id where n.update_id=p_update and p.email and p.consented_at is not null on conflict(notification_id,channel) do nothing;
 return n;
end $function$


create index if not exists account_entity_parent on public.followable_entities(parent_id);
create index if not exists account_update_content on public.updates(content_type,published_at desc) where status='published';
create or replace function public.account_feed(p_category text default null,p_offset integer default 0,p_limit integer default 20) returns jsonb language sql stable security invoker set search_path='' as $$
 with recursive interest_locations(id) as (select e.id from public.followable_entities e join public.profiles p on p.id=(select auth.uid()) where e.id=any(p.interest_entities) union select e.id from public.followable_entities e join interest_locations l on e.parent_id=l.id)
 select coalesce(jsonb_agg(to_jsonb(r)),'[]'::jsonb) from (
 select u.*,exists(select 1 from public.bookmarks b where b.user_id=auth.uid() and b.update_id=u.id) as bookmarked
 from public.updates u join public.profiles p on p.id=(select auth.uid())
 where public.active_account() and u.status='published' and (p_category is null or u.category=p_category)
 and (cardinality(p.interest_content_types)=0 or u.content_type=any(p.interest_content_types))
 and not exists(select 1 from public.hidden_updates h where h.user_id=auth.uid() and h.update_id=u.id)
 and exists(select 1 from public.update_entities ue join public.followable_entities e on e.id=ue.entity_id
 where ue.update_id=u.id and ue.approved and
 (exists(select 1 from public.user_follows f where f.entity_id=e.id and f.user_id=auth.uid() and not f.muted)
 or e.id in (select id from interest_locations))
 and (cardinality(p.interest_topics)=0 or
 ('general'=any(p.interest_topics) and e.id like 'election:ls:%') or
 ('assembly'=any(p.interest_topics) and e.id like 'election:assembly:%') or
 ('mlc'=any(p.interest_topics) and (e.id like 'election:mlc:%' or e.name ilike '%MLC%')) or
 ('local'=any(p.interest_topics) and e.kind in ('body','ward','city','district')) or
 ('municipal'=any(p.interest_topics) and e.id like 'body:%corp%') or
 ('panchayat'=any(p.interest_topics) and (e.id like '%panchayat%' or e.id like '%zilla%'))))
 order by u.published_at desc,u.id limit least(greatest(p_limit,1),50) offset greatest(p_offset,0))r
$$;
