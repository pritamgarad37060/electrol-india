begin;
select set_config('test.a',gen_random_uuid()::text,true), set_config('test.b',gen_random_uuid()::text,true), set_config('test.sa',gen_random_uuid()::text,true), set_config('test.sb',gen_random_uuid()::text,true);
insert into auth.users(id,email,aud,role) values
(current_setting('test.a')::uuid,current_setting('test.a')||'@example.invalid','authenticated','authenticated'),
(current_setting('test.b')::uuid,current_setting('test.b')||'@example.invalid','authenticated','authenticated');
insert into public.account_sessions(id,user_id) values
(current_setting('test.sa')::uuid,current_setting('test.a')::uuid),
(current_setting('test.sb')::uuid,current_setting('test.b')::uuid);
insert into public.user_follows(user_id,entity_id) values
(current_setting('test.a')::uuid,'country:IN'),(current_setting('test.b')::uuid,'country:IN');
set local role authenticated;
select set_config('request.jwt.claims',jsonb_build_object('sub',current_setting('test.a'),'session_id',current_setting('test.sa'),'aal','aal1','role','authenticated')::text,true);
do $test$
declare n integer;
begin
 if (select count(*) from public.profiles)<>1 then raise exception 'profile isolation failed'; end if;
 if (select count(*) from public.user_follows)<>1 then raise exception 'follow isolation failed'; end if;
 update public.profiles set display_name='Isolation test' where id=current_setting('test.b')::uuid;
 get diagnostics n=row_count;
 if n<>0 then raise exception 'cross user update allowed'; end if;
 begin
  insert into public.user_follows(user_id,entity_id) values(current_setting('test.b')::uuid,'body:parliament');
  raise exception 'cross user insert allowed';
 exception when insufficient_privilege then null;
 end;
 begin
  perform public.account_admin_health();
  raise exception 'ordinary user accessed admin health';
 exception when raise_exception then
  if sqlerrm<>'not authorized' then raise; end if;
 end;
 begin
  insert into public.user_follows(user_id,entity_id) values(current_setting('test.a')::uuid,'country:IN');
  raise exception 'duplicate follow allowed';
 exception when unique_violation then null;
 end;
end $test$;
reset role;
update public.account_sessions set revoked_at=now() where id=current_setting('test.sa')::uuid;
set local role authenticated;
do $test$
begin
 if exists(select 1 from public.profiles) or exists(select 1 from public.user_follows) then raise exception 'revoked session still authorized'; end if;
end $test$;
reset role;
do $test$
begin
 if has_table_privilege('anon','public.profiles','select') then raise exception 'guest private profile grant'; end if;
 if has_table_privilege('anon','public.user_follows','select') then raise exception 'guest private follow grant'; end if;
 if has_function_privilege('authenticated','public.manage_account_staff(uuid,uuid,text)','execute') then raise exception 'staff role RPC exposed'; end if;
 if has_function_privilege('authenticated','public.claim_account_deliveries(uuid)','execute') then raise exception 'delivery RPC exposed'; end if;
end $test$;
rollback;
select 'PASS: two-user profile and follow isolation, cross-user mutations, duplicate follows, ordinary-user admin denial, revoked-session denial, guest grants and server-only RPC grants. Test records rolled back.' as result;
