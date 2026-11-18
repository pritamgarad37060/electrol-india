-- Additive account profile/media support. Election tables and account RLS stay intact.
alter table public.profiles
 add column bio text not null default '' check (length(bio)<=500),
 add column location text not null default '' check (length(location)<=120),
 add column website text not null default '' check (website='' or (length(website)<=2048 and website ~ '^https://')),
 add column avatar_path text check (avatar_path is null or (split_part(avatar_path,'/',1)=id::text and split_part(avatar_path,'/',2) ~ '^avatar-[a-f0-9-]{36}\.webp$' and array_length(string_to_array(avatar_path,'/'),1)=2)),
 add column cover_path text check (cover_path is null or (split_part(cover_path,'/',1)=id::text and split_part(cover_path,'/',2) ~ '^cover-[a-f0-9-]{36}\.webp$' and array_length(string_to_array(cover_path,'/'),1)=2));
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
 values ('account-profile-media','account-profile-media',false,1048576,array['image/webp']);
create policy account_media_read on storage.objects for select to authenticated
 using(bucket_id='account-profile-media' and (storage.foldername(name))[1]=(select auth.uid())::text and public.active_account());
create policy account_media_insert on storage.objects for insert to authenticated
 with check(bucket_id='account-profile-media' and (storage.foldername(name))[1]=(select auth.uid())::text and public.active_account());
create policy account_media_update on storage.objects for update to authenticated
 using(bucket_id='account-profile-media' and (storage.foldername(name))[1]=(select auth.uid())::text and public.active_account())
 with check(bucket_id='account-profile-media' and (storage.foldername(name))[1]=(select auth.uid())::text and public.active_account());
create policy account_media_delete on storage.objects for delete to authenticated
 using(bucket_id='account-profile-media' and (storage.foldername(name))[1]=(select auth.uid())::text and public.active_account());
create function public.account_follow_counts() returns jsonb language sql stable security invoker set search_path='' as $$
 select coalesce(jsonb_object_agg(kind,n),'{}'::jsonb) from
 (select e.kind,count(*) n from public.user_follows f join public.followable_entities e on e.id=f.entity_id
 where f.user_id=(select auth.uid()) and public.active_account() group by e.kind) counts
$$;
revoke all on function public.account_follow_counts() from public,anon;
grant execute on function public.account_follow_counts() to authenticated;
-- Profiles intentionally grant updates by column; include the new editable fields.
grant update(bio,location,website,avatar_path,cover_path) on public.profiles to authenticated;
