begin;
select set_config('test.profile_a',gen_random_uuid()::text,true),set_config('test.profile_b',gen_random_uuid()::text,true),set_config('test.profile_sa',gen_random_uuid()::text,true),set_config('test.profile_sb',gen_random_uuid()::text,true);
insert into auth.users(id,email,aud,role) values
(current_setting('test.profile_a')::uuid,current_setting('test.profile_a')||'@example.invalid','authenticated','authenticated'),
(current_setting('test.profile_b')::uuid,current_setting('test.profile_b')||'@example.invalid','authenticated','authenticated');
insert into public.account_sessions(id,user_id) values
(current_setting('test.profile_sa')::uuid,current_setting('test.profile_a')::uuid),
(current_setting('test.profile_sb')::uuid,current_setting('test.profile_b')::uuid);
insert into public.user_follows(user_id,entity_id,alert_types) values
(current_setting('test.profile_a')::uuid,'country:IN',array['news']),
(current_setting('test.profile_b')::uuid,'country:IN',array['elections']);
set local role authenticated;
select set_config('request.jwt.claims',jsonb_build_object('sub',current_setting('test.profile_a'),'session_id',current_setting('test.profile_sa'),'aal','aal1','role','authenticated')::text,true);
do $test$
declare n integer;
begin
 update public.profiles set bio='Private test bio',location='Test location',website='https://example.invalid/' where id=auth.uid();
 if (select count(*) from public.profiles)<>1 then raise exception 'Private profile isolation failed'; end if;
 if (select bio from public.profiles where id=auth.uid())<>'Private test bio' then raise exception 'Profile fields did not save'; end if;
 update public.profiles set bio='Not allowed' where id=current_setting('test.profile_b')::uuid;
 get diagnostics n=row_count;if n<>0 then raise exception 'Cross-user profile update allowed';end if;
 if public.account_follow_counts()->>'country'<>'1' then raise exception 'Follow counts leaked another user';end if;
 update public.user_follows set muted=true where user_id=auth.uid() and entity_id='country:IN';
 if (select alert_types from public.user_follows where user_id=auth.uid() and entity_id='country:IN')<>array['news']::text[] then raise exception 'Mute changed alert categories';end if;
 begin
  update public.profiles set avatar_path=current_setting('test.profile_b')||'/avatar-'||gen_random_uuid()||'.webp' where id=auth.uid();
  raise exception 'Cross-user image path allowed';
 exception when check_violation then null;end;
end $test$;
reset role;
update public.account_sessions set revoked_at=now() where id=current_setting('test.profile_sa')::uuid;
set local role authenticated;
do $test$
begin
 if public.account_follow_counts()<>'{}'::jsonb then raise exception 'Revoked session counts exposed';end if;
 if exists(select 1 from public.profiles) then raise exception 'Revoked session profile exposed';end if;
end $test$;
reset role;
do $test$
begin
 if (select public from storage.buckets where id='account-profile-media') then raise exception 'Profile media bucket is public';end if;
 if (select count(*) from pg_policies where schemaname='storage' and policyname like 'account_media_%')<>4 then raise exception 'Missing private media policies';end if;
 if has_function_privilege('anon','public.account_follow_counts()','execute') then raise exception 'Guest follow counts exposed';end if;
end $test$;
rollback;
select 'PASS: private profile fields, two-user isolation, exact private follow counts, mute category preservation, cross-owner image constraint, revoked-session denial and private bucket policies. All test records rolled back.' as result;
