-- Re-runnable registry import from existing public website snapshots. No source records are deleted.
with people as (
 select r.value r, '/data/people-directory.json'::text path from website_datasets d cross join lateral jsonb_array_elements(d.content->'rows')r where d.path='/data/people-directory.json'
), entries as (
 select 'representative'||chr(31)||(r->>'key') source_key,r,path from people
)
insert into public.candidate_identity_registry(record_uid,source_key,record_kind,display_name,election_level,state,body_id,election_year,seat_key,party,source_path,source_url,legacy_key)
select md5('electrol-identity-v1'||chr(31)||source_key)::uuid,source_key,'representative',r->>'name',case r->>'kind' when 'mp' then 'lok' when 'mla' then 'assembly' when 'local' then coalesce(r->>'body_kind','local') else 'reference' end,r->>'state',r->>'body',nullif(r->>'year','')::integer,r->>'seat',r->>'party',path,r->>'source',r->>'key' from entries
on conflict(source_key) do update set display_name=excluded.display_name,election_level=excluded.election_level,state=excluded.state,body_id=excluded.body_id,election_year=excluded.election_year,seat_key=excluded.seat_key,party=excluded.party,source_url=excluded.source_url,legacy_key=excluded.legacy_key,updated_at=now();
with docs as materialized (select d.path,j.* from website_datasets d cross join lateral jsonb_to_record(d.content) j(level text,state text,year text,source text,seats jsonb,parties jsonb) where d.path like '/data/results/%'), raw as (
 select d.path,d.level,d.state edition_state,d.year edition_year,d.source source_url,s.value->>'url' seat_url,s.value->>'state' seat_state,c.value->>0 candidate_name,c.ordinality ord,d.parties->((c.value->>1)::integer)->>'short' party
 from docs d cross join lateral jsonb_array_elements(d.seats)s cross join lateral jsonb_array_elements(s.value->'c') with ordinality c(value,ordinality)
), numbered as (
 select *,row_number()over(partition by path,seat_url,candidate_name,party order by ord) occurrence from raw where party<>'NOTA'
), entries as (
 select *,concat_ws(chr(31),'result',level||'|'||edition_state||'|'||edition_year,seat_state,seat_url,candidate_name,party,occurrence::text) source_key from numbered
)
insert into public.candidate_identity_registry(record_uid,source_key,record_kind,display_name,election_level,state,election_year,seat_key,party,source_path,source_url)
select md5('electrol-identity-v1'||chr(31)||source_key)::uuid,source_key,'result',candidate_name,level,seat_state,edition_year::integer,seat_url,party,path,source_url from entries
on conflict(source_key) do update set display_name=excluded.display_name,election_level=excluded.election_level,state=excluded.state,election_year=excluded.election_year,seat_key=excluded.seat_key,party=excluded.party,updated_at=now();
with docs as materialized (select d.path,j.* from website_datasets d cross join lateral jsonb_to_record(d.content) j(id text,kind text,state text,source text,snapshots jsonb) where d.path like '/data/local-results/%'), raw as (
 select d.path,d.id body_id,d.kind body_kind,d.state state_name,d.source source_url,y.key as election_year_text,coalesce(r.value->>'ward','')||coalesce(r.value->>'seat','') local_seat,c.value->>0 candidate_name,c.value->>1 candidate_party,c.ordinality ord
 from docs d cross join lateral jsonb_each(d.snapshots)y cross join lateral jsonb_array_elements(y.value->'rows')r
 cross join lateral jsonb_array_elements(case when jsonb_array_length(coalesce(r.value->'cands','[]'::jsonb))>0 then r.value->'cands' else jsonb_build_array(jsonb_build_array(coalesce(r.value->>'name',r.value->>'candidate'),r.value->>'party',r.value->'votes')) end) with ordinality c(value,ordinality)
 where not coalesce((r.value->>'review')::boolean,false)
), numbered as (
 select *,row_number()over(partition by path,election_year_text,local_seat,candidate_name,candidate_party order by ord) occurrence from raw where candidate_party<>'NOTA'
), entries as (
 select *,concat_ws(chr(31),'local',body_id,election_year_text,local_seat,candidate_name,candidate_party,occurrence::text) source_key from numbered
)
insert into public.candidate_identity_registry(record_uid,source_key,record_kind,display_name,election_level,state,body_id,election_year,seat_key,party,source_path,source_url)
select md5('electrol-identity-v1'||chr(31)||source_key)::uuid,source_key,'local',candidate_name,body_kind,state_name,body_id,election_year_text::integer,local_seat,candidate_party,path,source_url from entries
on conflict(source_key) do update set display_name=excluded.display_name,election_level=excluded.election_level,state=excluded.state,body_id=excluded.body_id,election_year=excluded.election_year,seat_key=excluded.seat_key,party=excluded.party,updated_at=now();
with docs as materialized (select d.path,j.* from website_datasets d cross join lateral jsonb_to_record(d.content) j(id text,kind text,state text,source text,snapshots jsonb) where d.path like '/data/local-results/%'), entries as (
select d.path,d.id,d.kind,d.state,d.source,y.key as election_year_text,y.value->'president' head,
concat_ws(chr(31),'local-head',d.id,y.key,y.value->'president'->>'candidate',y.value->'president'->>'party') source_key
from docs d cross join lateral jsonb_each(d.snapshots)y where y.value->'president'->>'candidate' is not null)
insert into public.candidate_identity_registry(record_uid,source_key,record_kind,display_name,election_level,state,body_id,election_year,seat_key,party,source_path,source_url)
select md5('electrol-identity-v1'||chr(31)||source_key)::uuid,source_key,'local',head->>'candidate',kind,state,id,election_year_text::integer,'head',head->>'party',path,source from entries
on conflict(source_key) do update set display_name=excluded.display_name,party=excluded.party,updated_at=now();
