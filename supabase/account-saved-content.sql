-- Private, globally ordered saved articles and representative profiles.
create or replace function public.account_saved_content(p_type text default null,p_query text default '',p_oldest boolean default false,p_offset integer default 0)
returns jsonb language sql stable security invoker set search_path='' as $$
select coalesce(jsonb_agg(to_jsonb(r)),'[]'::jsonb) from (
 select * from (
  select b.created_at,b.update_id,null::text as entity_id,to_jsonb(u) as item
  from public.bookmarks b join public.updates u on u.id=b.update_id
  where b.user_id=(select auth.uid()) and public.active_account()
  and (p_type is null or u.content_type=p_type)
  and (coalesce(p_query,'')='' or u.title ilike '%'||p_query||'%')
  union all
  select s.created_at,null::uuid,s.entity_id,to_jsonb(e) from public.saved_profiles s
  join public.followable_entities e on e.id=s.entity_id
  where s.user_id=(select auth.uid()) and public.active_account()
  and (p_type is null or p_type='profiles')
  and (coalesce(p_query,'')='' or e.name ilike '%'||p_query||'%')
 ) saved
 order by case when p_oldest then created_at end asc,case when not p_oldest then created_at end desc,coalesce(update_id::text,entity_id)
 limit 21 offset greatest(p_offset,0)
)r
$$;
revoke all on function public.account_saved_content(text,text,boolean,integer) from public,anon;
grant execute on function public.account_saved_content(text,text,boolean,integer) to authenticated;
