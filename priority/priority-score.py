import json,re,collections as C
db=json.load(open('/tmp/db.json'));cp=json.load(open('/tmp/camp.json'))
def h(u):
  m=re.search(r'linkedin\.com/in/([^/?#]+)',(u or '').lower()); return m.group(1) if m else ''
D={h(x['linkedin_url']):x for x in db if h(x['linkedin_url'])}
def has(rx,t): return re.search(rx,t,re.I)
EXIT=r'\b(post[- ]?exit|exited|exits?\b|acquired|acquisition|sold (my|our|the|to)|successful exit|serial (entrepreneur|founder)|ipo\b)'
FOUNDER=r'\b(co-?founder|cofounder|founder|founding|ceo|chief executive|owner|president)\b'
SENIOR=r'\b(chief|cto|cfo|coo|cmo|cpo|cro|vp|vice president|head of|managing director|chair(man|woman|person)?|board)\b'
INVEST=r'\b(investor|angel|venture|vc\b|general partner|limited partner|\bgp\b|\blp\b|fund|capital|family office)\b'
HUB=r'(new york|nyc|brooklyn|manhattan|san francisco|bay area|palo alto|menlo park|silicon valley|mountain view|los angeles|santa monica|austin|miami|boston|cambridge|seattle|chicago|denver|boulder)'
US=r'(united states|, (ca|ny|tx|fl|ma|wa|il|co|ga|nc|va|nj|pa|az|ut|tn|or|mn|oh|mi|md|ct|dc)\b|california|texas|florida|atlanta|dallas|houston|san diego|washington|philadelphia|nashville|phoenix|salt lake|portland|minneapolis|raleigh|charlotte|detroit|pittsburgh|baltimore|orlando|tampa|las vegas|san jose|oakland|greater )'
NONUS=r'(london|united kingdom|israel|tel aviv|canada|toronto|vancouver|india|germany|berlin|paris|france|australia|sydney|singapore|dubai|netherlands|amsterdam|spain|mexico|brazil|ireland|switzerland|sweden)'
photos=set(re.findall(r'"([a-z0-9%_.-]+)":\{', open('/tmp/idx.js').read()))  # coarse, refined below
cp=[p for p in cp if h(p['url'])!='bstamos']  # Barry Stamos is the Supernova sender, not a lead
cp=[p for p in cp if p['name'] not in ('testeoJose','testLeo Supernova')]  # test records, not leads
# Same name + same company as a Barry connection under another handle: keep, but rank last (P3)
ALREADY={'nebilbenaissa','adam-ezra-766a3a54','raelcline','maikokojima','craig-bolz-2b3b5418','alanrihm','craig-s-storch-a94114','kartik-c-85bb5487','eli-broverman-41035722','felix-van-de-sand-36885b4','gareth-hermann','john-murr-77b0961','jordan-sanial-5887021','mdelaney7','ned-macpherson-3029a120','noam-maital-469a9912','noy-cohen-633b914','pamatthe','rachel-ten-brink-a08151','rafis','courageousideas','shlomi-beer-1b847b1','mike-rahimzadeh-4465154','tj-grewal-9a536','tomasgutierrezmeoz','justinbean','zack-zigdon-083a2'}
# Supernova row carries another person's LinkedIn URL
WRONG={'raelcline','maikokojima','kartik-c-85bb5487','mike-rahimzadeh-4465154','justinbean','alanrihm','mark-ramadan','wdinkel'}
out=[]
for p in cp:
  d=D.get(h(p['url']),{})
  text=' | '.join(filter(None,[d.get('headline',''),p['role'],d.get('job_title','')]))
  extra=' '.join(filter(None,[d.get('areas_of_expertise',''),d.get('expertise_tags','')]))
  loc=p['location'] or d.get('location_raw','') or ''
  s=0;why=[]
  m=has(EXIT,text)
  if m: s+=35; why.append(f'exit word in headline/title ("{m.group(0).strip()}")')
  elif has(EXIT,extra): s+=20; why.append(f'exit word in expertise ("{has(EXIT,extra).group(0).strip()}")')
  if has(FOUNDER,text): s+=25; why.append('founder/CEO title')
  elif has(SENIOR,text): s+=15; why.append('senior exec title')
  if has(INVEST,text): s+=15; why.append('investor/fund words in title')
  if has(HUB,loc): s+=10; why.append(f'US hub: {loc}')
  elif has(US,loc) and not has(NONUS,loc): s+=6; why.append(f'US: {loc}')
  elif loc: s+=3; why.append(f'location: {loc}')
  else: why.append('no location')
  st=p['step']
  if st=='Ready for profile check': s+=10; why.append('profile ready')
  elif st=='Check identity': s+=4; why.append('identity to check')
  elif st=='Already connected? Check': why.append('same name and company as a Barry connection; already connected? check')
  else: why.append('profile URL missing')
  if d.get('headline') or extra: s+=5
  ev=len(re.findall(EXIT,text,re.I))+len(re.findall(EXIT,extra,re.I))
  if h(p['url']) in WRONG: why.append('LinkedIn link may be wrong')
  out.append(dict(ev=ev,al=h(p['url']) in ALREADY,handle=h(p['url']),name=p['name'],role=p['role'],location=loc,url=p['url'],score=min(s,100),why='; '.join(why)))
out.sort(key=lambda x:(x['al'],-x['score'],-x['ev'],x['name'].lower()))
for x in out: x.pop('ev'); x.pop('al')
for i,x in enumerate(out):
  x['rank']=i+1; x['tier']='P1' if i<100 else 'P2' if i<400 else 'P3'
json.dump(out,open('priority.json','w'),ensure_ascii=False)
print(C.Counter(x['tier'] for x in out)); print(C.Counter(x['score'] for x in out).most_common())
for t in ['P1','P2','P3']:
  sc=[x['score'] for x in out if x['tier']==t]; print(t,max(sc),min(sc))
for x in out[:25]: print(x['rank'],x['score'],x['name'],'|',x['role'],'|',x['why'])
