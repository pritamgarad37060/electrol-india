begin;
-- Keep public published content readable without exposing account helper RPCs.
drop policy published_updates on public.updates;
create policy published_updates_guest on public.updates for select to anon using(status='published');
create policy published_updates_member on public.updates for select to authenticated using(status='published' or public.account_staff());
drop policy published_matches on public.update_entities;
create policy published_matches_guest on public.update_entities for select to anon using(exists(select 1 from public.updates u where u.id=update_id and u.status='published'));
create policy published_matches_member on public.update_entities for select to authenticated using(exists(select 1 from public.updates u where u.id=update_id and (u.status='published' or public.account_staff())));
revoke execute on function public.account_staff(),public.active_account() from anon;
commit;
