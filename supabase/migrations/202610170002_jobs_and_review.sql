begin;
-- Enforce MFA in the database as well as the account API when a verified
-- Supabase factor exists. Supabase's managed auth.mfa_factors is read only.
create or replace function public.active_account() returns boolean language sql stable security definer set search_path='' as $$
 select auth.uid() is not null
 and exists(select 1 from public.account_sessions s where s.id=(auth.jwt()->>'session_id')::uuid and s.user_id=auth.uid() and s.revoked_at is null)
 and (auth.jwt()->>'aal'='aal2' or not exists(select 1 from auth.mfa_factors f where f.user_id=auth.uid() and f.status='verified'))
$$;
alter table public.notification_deliveries add column lease_id uuid;
create function public.claim_account_deliveries(p_lease uuid) returns setof public.notification_deliveries language sql security definer set search_path='' as $$
 update public.notification_deliveries set status='processing',lease_id=p_lease,lease_until=now()+interval '5 minutes',attempts=attempts+1
 where id in(select id from public.notification_deliveries where next_attempt_at<=now() and attempts<8 and (status in ('pending','failed','blocked') or (status='processing' and lease_until<now())) order by next_attempt_at limit 25 for update skip locked) returning *
$$;
create function public.review_account_update(p_update uuid,p_entities text[],p_important boolean,p_reject boolean default false) returns void language plpgsql security definer set search_path='' as $$
declare r public.updates;begin
 if not public.account_staff() or not exists(select 1 from public.staff_roles where user_id=auth.uid() and role in ('reviewer','admin','owner')) then raise exception 'not authorized';end if;
 if cardinality(p_entities)>30 or (not p_reject and cardinality(p_entities)=0) then raise exception 'entities required';end if;
 select * into r from public.updates where id=p_update and status='pending' for update;
 if not found or r.published_at>now()+interval '5 minutes' then raise exception 'update unavailable';end if;
 delete from public.update_entities where update_id=p_update;
 insert into public.update_entities(update_id,entity_id,approved) select p_update,unnest(p_entities),true;
 update public.updates set status=case when p_reject then 'rejected' else 'published' end,important=p_important,reviewed_by=auth.uid(),reviewed_at=now() where id=p_update;
 if not p_reject then perform public.generate_update_notifications(p_update);end if;
 insert into public.security_audit_events(user_id,event_type,success) values(auth.uid(),'admin_update_reviewed',true);
end $$;
create function public.manage_account_staff(p_actor uuid,p_target uuid,p_role text) returns void language plpgsql security definer set search_path='' as $$
begin
 perform pg_advisory_xact_lock(81472026);
 if not exists(select 1 from public.staff_roles where user_id=p_actor and role='owner') then raise exception 'not authorized';end if;
 if p_role not in ('reviewer','operator','admin','owner','remove') then raise exception 'invalid role';end if;
 if exists(select 1 from public.staff_roles where user_id=p_target and role='owner') and p_role<>'owner' and (select count(*) from public.staff_roles where role='owner')<=1 then raise exception 'last owner';end if;
 if p_role='remove' then delete from public.staff_roles where user_id=p_target;else insert into public.staff_roles(user_id,role) values(p_target,p_role) on conflict(user_id) do update set role=excluded.role;end if;
 insert into public.security_audit_events(user_id,event_type,success) values(p_actor,'administrative_role_changed',true);
end $$;
revoke all on function public.claim_account_deliveries(uuid),public.manage_account_staff(uuid,uuid,text) from public,anon,authenticated;
grant execute on function public.claim_account_deliveries(uuid),public.manage_account_staff(uuid,uuid,text) to service_role;
revoke all on function public.review_account_update(uuid,text[],boolean,boolean) from public,anon;
grant execute on function public.review_account_update(uuid,text[],boolean,boolean) to authenticated;
commit;
