"""Read public channel claims for the existing politician directory; no diagnostic uploads."""
import json,pathlib,urllib.parse,urllib.request,concurrent.futures,re,sys,time,xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')
here=pathlib.Path(__file__).resolve().parent
people=json.loads((here/'representatives.json').read_text(encoding='utf-8'))
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'ElectrolIndia-Prototype/1.0 (public channel directory)'})
 with urllib.request.urlopen(req,timeout=10) as res:return json.loads(res.read())
def lookup(p):
 try:
  name=re.sub(r'^(Ms\.?|Dr\.?|Shri|Smt\.?)\s+','',p['name'],flags=re.I)
  j=get('https://www.wikidata.org/w/api.php?'+urllib.parse.urlencode({'action':'wbsearchentities','search':name,'language':'en','format':'json','limit':3}))
  candidates=j.get('search',[])
  exact=lambda s:re.sub('[^a-z]','',s.lower())
  hit=next((x for x in candidates if exact(x['label'])==exact(name)),None)
  if not hit:return {'id':p['id'],'status':'No exact directory match'}
  j=get('https://www.wikidata.org/w/api.php?'+urllib.parse.urlencode({'action':'wbgetentities','ids':hit['id'],'props':'claims','format':'json'}))
  claims=j['entities'][hit['id']].get('claims',{})
  channel=next((x['mainsnak'].get('datavalue',{}).get('value') for x in claims.get('P2397',[]) if x['mainsnak'].get('datavalue')),None)
  return {'id':p['id'],'name':name,'channelId':channel,'source':'https://www.wikidata.org/wiki/'+hit['id'],'status':'Directory claim' if channel else 'No YouTube channel recorded'}
 except Exception as e:return {'id':p['id'],'status':str(e)}
if __name__=='__main__':
 out=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for row in pool.map(lookup,people):
   out.append(row)
   (here/'youtube-lookups.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
 print(json.dumps({'checked':len(out),'channels':sum(bool(x.get('channelId')) for x in out)}))
