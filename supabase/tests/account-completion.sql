begin;
select set_config('test.account_a',gen_random_uuid()::text,true),set_config('test.account_b',gen_random_uuid()::text,true),set_config('test.account_session',gen_random_uuid()::text,true);
insert into auth.users(id,email,aud,role) values
(current_setting('test.account_a')::uuid,current_setting('test.account_a')||'@example.invalid','authenticated','authenticated'),
(current_setting('test.account_b')::uuid,current_setting('test.account_b')||'@example.invalid','authenticated','authenticated');
insert into public.account_sessions(id,user_id) values(current_setting('test.account_session')::uuid,current_setting('test.account_a')::uuid);
set local role authenticated;
select set_config('request.jwt.claims',jsonb_build_object('sub',current_setting('test.account_a'),'session_id',current_setting('test.account_session'),'aal','aal1','role','authenticated')::text,true);
do $test$
declare entity text; n integer;
begin
 update public.profiles set interest_topics=array['assembly'],interest_content_types=array['analysis'],interest_entities=array['country:IN'],social_links='{"x":"https://x.com/example"}' where id=auth.uid();
 if (select interest_topics from public.profiles where id=auth.uid())<>array['assembly'] then raise exception 'Interests did not persist';end if;
 update public.profiles set interest_topics=array['general'] where id=current_setting('test.account_b')::uuid;
 get diagnostics n=row_count;if n<>0 then raise exception 'Cross-user interests allowed';end if;
 insert into public.notification_preferences(user_id,quiet_enabled,quiet_start,quiet_end,quiet_days,timezone,date_format,time_format)
 values(auth.uid(),true,'22:00','07:00',array[1],'UTC','YYYY-MM-DD','24')
 on conflict(user_id) do update set quiet_enabled=true,quiet_start='22:00',quiet_end='07:00',quiet_days=array[1],timezone='UTC',date_format='YYYY-MM-DD',time_format='24';
 if public.account_delivery_time('2026-10-19 23:00Z',auth.uid())<>'2026-10-20 07:00Z'::timestamptz then raise exception 'Monday overnight quiet hours failed';end if;
 if public.account_delivery_time('2026-10-20 06:00Z',auth.uid())<>'2026-10-20 07:00Z'::timestamptz then raise exception 'Overnight previous-day quiet hours failed';end if;
 if public.account_delivery_time('2026-10-20 23:00Z',auth.uid())<>'2026-10-20 23:00Z'::timestamptz then raise exception 'Unselected quiet day delayed';end if;
 update public.notification_preferences set quiet_start='09:00',quiet_end='17:00' where user_id=auth.uid();
 if public.account_delivery_time('2026-10-19 10:00Z',auth.uid())<>'2026-10-19 17:00Z'::timestamptz then raise exception 'Same-day quiet hours failed';end if;
 select id into entity from public.followable_entities where kind='person' and active limit 1;
 if entity is null then raise exception 'Missing representative catalog';end if;
 insert into public.saved_profiles(user_id,entity_id) values(auth.uid(),entity);
 if jsonb_array_length(public.account_saved_content())<>1 then raise exception 'All saved content omitted saved profile';end if;
 if jsonb_array_length(public.account_saved_content('profiles'))<>1 then raise exception 'Saved profile filter failed';end if;
 if jsonb_array_length(public.account_saved_content('news'))<>0 then raise exception 'Saved type isolation failed';end if;
 begin
  insert into public.saved_profiles(user_id,entity_id) values(current_setting('test.account_b')::uuid,entity);
  raise exception 'Cross-user saved profile allowed';
 exception when insufficient_privilege then null;end;
 if jsonb_typeof(public.account_elections()->'rows')<>'array' then raise exception 'Election listing shape invalid';end if;
 if public.account_feed()<>'[]'::jsonb then raise exception 'Unrelated updates appeared in empty account';end if;
end $test$;
reset role;
update public.account_sessions set revoked_at=now() where id=current_setting('test.account_session')::uuid;
set local role authenticated;
do $test$ begin
 if exists(select 1 from public.saved_profiles) then raise exception 'Revoked session saved profiles exposed';end if;
 if public.account_saved_content()<>'[]'::jsonb then raise exception 'Revoked saved content exposed';end if;
end $test$;
reset role;
rollback;
select 'PASS: interests and preferences persist; saved All/filter ownership; two-user isolation; quiet-hour same-day/overnight boundaries; empty personalized feed; revoked-session denial. All records rolled back.' as result;
