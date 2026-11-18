/* Same-document navigation journal. View snapshots stay in memory only;
   browser history contains routing identifiers, never account or form data. */
(()=>{
 'use strict';
 const session=crypto.randomUUID(),key='electrolNavigation',entries=new Map();
 const replace=history.replaceState.bind(history),push=history.pushState.bind(history);
 const bindings={
  siteDestination:[()=>siteDestination,value=>{siteDestination=value}],
  lastPrimary:[()=>lastPrimary,value=>{lastPrimary=value}],
  navKind:[()=>navKind,value=>{navKind=value}],
  navTab:[()=>navTab,value=>{navTab=value}],
  profileTab:[()=>profileTab,value=>{profileTab=value}],
  profilePage:[()=>profilePage,value=>{profilePage=value}],
  profileSavedTab:[()=>profileSavedTab,value=>{profileSavedTab=value}],
  profileStack:[()=>profileStack,value=>{profileStack=value}],
  followView:[()=>followView,value=>{followView=value}],
  followCategory:[()=>followCategory,value=>{followCategory=value}],
  followQuery:[()=>followQuery,value=>{followQuery=value}],
  followSort:[()=>followSort,value=>{followSort=value}],
  followLocation:[()=>followLocation,value=>{followLocation=value}],
  followAlertFilter:[()=>followAlertFilter,value=>{followAlertFilter=value}],
  activeFollowId:[()=>activeFollowId,value=>{activeFollowId=value}],
  followDetailTab:[()=>followDetailTab,value=>{followDetailTab=value}],
  followReturnPage:[()=>followReturnPage,value=>{followReturnPage=value}],
  followVisibleLimit:[()=>followVisibleLimit,value=>{followVisibleLimit=value}],
  followResultKey:[()=>followResultKey,value=>{followResultKey=value}],
  homeOption:[()=>homeOption,value=>{homeOption=value}],
  homeFeatureIndex:[()=>homeFeatureIndex,value=>{homeFeatureIndex=value}],
  homeResultLevel:[()=>homeResultLevel,value=>{homeResultLevel=value}],
  homeFinder:[()=>homeFinder,value=>{homeFinder=value}],
  searchQuery:[()=>searchQuery,value=>{searchQuery=value}],
  searchFilters:[()=>searchFilters,value=>{searchFilters=value}],
  searchReturn:[()=>searchReturn,value=>{searchReturn=value}],
  newsScope:[()=>newsScope,value=>{newsScope=value}],
  newsCategory:[()=>newsCategory,value=>{newsCategory=value}],
  newsSort:[()=>newsSort,value=>{newsSort=value}],
  activeNewsArticle:[()=>activeNewsArticle,value=>{activeNewsArticle=value}],
  discovery:[()=>discovery,value=>{discovery=value}],
  discoveryDetailTab:[()=>discoveryDetailTab,value=>{discoveryDetailTab=value}],
  activeDiscoveryDetail:[()=>activeDiscoveryDetail,value=>{activeDiscoveryDetail=value}],
  seatDetailYear:[()=>seatDetailYear,value=>{seatDetailYear=value}],
  seatContestIndex:[()=>seatContestIndex,value=>{seatContestIndex=value}],
  seatMapMode:[()=>seatMapMode,value=>{seatMapMode=value}],
  seatMapParty:[()=>seatMapParty,value=>{seatMapParty=value}],
  partyContext:[()=>partyContext,value=>{partyContext=value}],
  current:[()=>current,value=>{current=value}],
  draft:[()=>draft,value=>{draft=value}],
  tab:[()=>tab,value=>{tab=value}],
  measure:[()=>measure,value=>{measure=value}],
  seatSide:[()=>seatSide,value=>{seatSide=value}],
  seatQuery:[()=>seatQuery,value=>{seatQuery=value}],
  mapLayout:[()=>mapLayout,value=>{mapLayout=value}],
  mapSeat:[()=>mapSeat,value=>{mapSeat=value}],
  mapRecordSide:[()=>mapRecordSide,value=>{mapRecordSide=value}],
  electionHub:[()=>electionHub,value=>{electionHub=value}],
  electionEdition:[()=>electionEdition,value=>{electionEdition=value}],
  electionDashboardTab:[()=>electionDashboardTab,value=>{electionDashboardTab=value}],
  electionResultQuery:[()=>electionResultQuery,value=>{electionResultQuery=value}],
  fullScope:[()=>fullScope,value=>{fullScope=value}],
  fullScopePreferences:[()=>fullScopePreferences,value=>{fullScopePreferences=value}],
  fullSeatQuery:[()=>fullSeatQuery,value=>{fullSeatQuery=value}],
  fullPartyFilter:[()=>fullPartyFilter,value=>{fullPartyFilter=value}],
  fullSort:[()=>fullSort,value=>{fullSort=value}],
  geoCamera:[()=>geoCamera,value=>{geoCamera=value}],
  geoSelected:[()=>geoSelected,value=>{geoSelected=value}],
  representativeId:[()=>representativeId,value=>{representativeId=value}],
  representativeTab:[()=>representativeTab,value=>{representativeTab=value}],
  representativePersonalTab:[()=>representativePersonalTab,value=>{representativePersonalTab=value}],
  representativeElectionFilter:[()=>representativeElectionFilter,value=>{representativeElectionFilter=value}],
  representativePositionView:[()=>representativePositionView,value=>{representativePositionView=value}],
  representativeReturn:[()=>representativeReturn,value=>{representativeReturn=value}],
  peopleQuery:[()=>peopleQuery,value=>{peopleQuery=value}],
  peopleState:[()=>peopleState,value=>{peopleState=value}],
  peopleLevel:[()=>peopleLevel,value=>{peopleLevel=value}],
  peopleSort:[()=>peopleSort,value=>{peopleSort=value}],
  peoplePage:[()=>peoplePage,value=>{peoplePage=value}],
  mcCurrent:[()=>mcCurrent,value=>{mcCurrent=value}],
  mcOrigin:[()=>mcOrigin,value=>{mcOrigin=value}],
  mcTab:[()=>mcTab,value=>{mcTab=value}],
  mcQuery:[()=>mcQuery,value=>{mcQuery=value}],
  mcState:[()=>mcState,value=>{mcState=value}],
  mcCoverage:[()=>mcCoverage,value=>{mcCoverage=value}],
  mcWardQuery:[()=>mcWardQuery,value=>{mcWardQuery=value}],
  mcParty:[()=>mcParty,value=>{mcParty=value}],
  mcWardSort:[()=>mcWardSort,value=>{mcWardSort=value}],
  mcWardPage:[()=>mcWardPage,value=>{mcWardPage=value}],
  mcWardKey:[()=>mcWardKey,value=>{mcWardKey=value}],
  mcWardTab:[()=>mcWardTab,value=>{mcWardTab=value}],
  mcWardView:[()=>mcWardView,value=>{mcWardView=value}],
  localBodyType:[()=>localBodyType,value=>{localBodyType=value}],
  localBodyCurrent:[()=>localBodyCurrent,value=>{localBodyCurrent=value}],
  localBodyTab:[()=>localBodyTab,value=>{localBodyTab=value}],
  localBodyQuery:[()=>localBodyQuery,value=>{localBodyQuery=value}],
  mlcQuery:[()=>mlcQuery,value=>{mlcQuery=value}],
  mlcState:[()=>mlcState,value=>{mlcState=value}],
  resultDepthTarget:[()=>resultDepthTarget,value=>{resultDepthTarget=value}],
  resultDepthOrigin:[()=>resultDepthOrigin,value=>{resultDepthOrigin=value}],
  resultDepthTab:[()=>resultDepthTab,value=>{resultDepthTab=value}],
  morePage:[()=>morePage,value=>{morePage=value}],
  moreReturnContext:[()=>moreReturnContext,value=>{moreReturnContext=value}]
 };
 const roots=['destination-view','comparison-content','navigation-body','dialog-body','election-more-body','news-actions-body','seat-tools-body'];
 const labels=['dialog-title','navigation-title','nav-kicker','nav-footer','election-more-title','news-actions-title','seat-tools-title'];
 let restorationEpoch=0;
 let entryId=0,sequence=0,restoring=false,scheduled=false,booting=true,interacted=false;
 const owner=()=>window.ElectrolBackend?.user?.id||'guest';
 const incoming=history.state?.[key];
 function route(){
  const result={page:siteDestination};
  if(siteDestination==='representative-profile')result.person=representativeId;
  if(siteDestination==='election-dashboard')result.edition=electionEdition?.id;
  if(siteDestination==='compare')result.comparison=structuredClone(current);
  if(siteDestination==='mlc-council')result.council=document.querySelector('.mc-profile-heading h1')?.textContent.replace(/ Legislative Council$/,'');
  if(siteDestination==='detailed-result')result.target=structuredClone(resultDepthTarget);
  if(document.getElementById('navigation-panel').open)result.panel={kind:navKind,page:profilePage,view:followView};
  return result;
 }
 const marker=(id,snapshot=entries.get(id))=>({session,id,route:snapshot?.route||route()});
 const signature=()=>JSON.stringify([route(),...Array.from(document.querySelectorAll('dialog[open]')).map(d=>[d.id,d.id==='navigation-panel'?[navKind,profilePage,profilePage==='follows'?followView:'',activeFollowId]:d.id==='auth-panel'?authState.step:d.querySelector('h2,h3')?.textContent])]);
 function capture(){
  const state={};for(const [name,[read]]of Object.entries(bindings))try{state[name]=structuredClone(read())}catch{}
  const views={};for(const id of roots){const node=document.getElementById(id);if(!node)continue;views[id]={html:node.innerHTML,className:node.className,scroll:node.scrollTop,inputs:Array.from(node.querySelectorAll('input[type=search],select')).map(n=>n.value)};}
  return {route:route(),parent:entries.get(entryId)?.parent??null,state,views,owner:owner(),signature:signature(),url:location.pathname+location.search+location.hash,title:document.title,scroll:window.scrollY,crumb:document.querySelector('.crumb')?.innerHTML,labels:Object.fromEntries(labels.map(id=>[id,document.getElementById(id)?.textContent])),dialogs:Array.from(document.querySelectorAll('dialog[open]')).map(d=>({id:d.id,kind:d.dataset.kind,page:d.dataset.page,scroll:d.scrollTop})),authStep:authState.step,navBack:document.getElementById('nav-back').className};
 }
 function save(){entries.set(entryId,capture());}
 // Older renderers use replaceState(null) for representative hashes. Retain
 // this entry's marker so those updates do not erase the navigation journal.
 history.replaceState=function(state,title,url){return replace({...state,[key]:marker(entryId)},title,url)};
 replace({...history.state,[key]:marker(entryId)},'',location.href);save();
 function commit(){
  scheduled=false;if(restoring)return;
  const next=capture(),previous=entries.get(entryId);
  if(next.owner!==previous?.owner){entries.clear();entries.set(entryId,next);return;}
  if((booting&&!interacted)||next.signature===previous?.signature){entries.set(entryId,next);return;}
  const parent=entries.get(previous?.parent);
  if(previous?.dialogs.length&&next.state.siteDestination===previous.state.siteDestination&&next.dialogs.length<previous.dialogs.length&&parent&&next.signature===parent.signature){
   // Applying a filter changes the page beneath the closing sheet. Consume
   // the sheet's entry while retaining those changes on its parent page.
   entries.set(previous.parent,{...next,parent:parent.parent});
   history.back();return;
  }
  // A renderer may already have replaced the URL. Put the previous URL back
  // on its own entry before pushing the destination's URL.
  if(previous)replace({...history.state,[key]:marker(entryId)},'',previous.url);
  next.parent=entryId;entryId=++sequence;push({[key]:marker(entryId,next)},'',next.url);entries.set(entryId,next);
  while(entries.size>32)entries.delete(entries.keys().next().value);
 }
 function schedule(){if(restoring||scheduled)return;scheduled=true;requestAnimationFrame(commit);}
 new MutationObserver(schedule).observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['open']});
 for(const type of ['pointerdown','keydown'])window.addEventListener(type,()=>{if(restoring)return;interacted=true;save();},true);
 window.addEventListener('click',event=>{
  const back=event.target.closest('.explore-return,.primary-back,[data-search-back],[data-depth-back],[data-rep-back],#nav-back');
  if(!back||!entries.has(entries.get(entryId)?.parent))return;
  event.preventDefault();event.stopImmediatePropagation();history.back();
 },true);
 function writeState(state){for(const [name,value]of Object.entries(state)){
  const pair=bindings[name];if(!pair)continue;const copy=structuredClone(value);
  try{pair[1](copy)}catch{try{const live=pair[0]();if(live instanceof Map){live.clear();for(const [k,v]of copy)live.set(k,v)}else if(Array.isArray(live))live.splice(0,live.length,...copy);else if(live&&typeof live==='object')Object.assign(live,copy);}catch{}}
 }}
 async function restore(snapshot){
  const epoch=++restorationEpoch,entry=entryId;restoring=true;
  try{
   document.querySelectorAll('dialog[open]').forEach(d=>d.close());
   if(snapshot.owner!==owner()){showPrimary('home');return;}
   writeState(snapshot.state);
   for(const [id,view]of Object.entries(snapshot.views)){
    const node=document.getElementById(id);if(!node)continue;node.innerHTML=view.html;node.className=view.className;
    node.querySelectorAll('input[type=search],select').forEach((input,index)=>{if(view.inputs[index]!==undefined)input.value=view.inputs[index]});node.scrollTop=view.scroll;
   }
   for(const [id,text]of Object.entries(snapshot.labels)){const node=document.getElementById(id);if(node&&text!==undefined)node.textContent=text;}
   document.getElementById('nav-back').className=snapshot.navBack;
   if(document.querySelector('.crumb'))document.querySelector('.crumb').innerHTML=snapshot.crumb||'';
   document.title=snapshot.title;setPrimaryActive(lastPrimary);
   for(const dialog of snapshot.dialogs){const node=document.getElementById(dialog.id);if(!node||dialog.id==='rep-video-dialog')continue;
    if(dialog.id==='auth-panel'){openAuth(['login','signup','forgot','providers'].includes(snapshot.authStep)?snapshot.authStep:'login');continue;}
    if(dialog.kind)node.dataset.kind=dialog.kind;if(dialog.page)node.dataset.page=dialog.page;
    if(!node.open)node.showModal();node.scrollTop=dialog.scroll;
   }
   // Refresh authenticated controls against current account state, rather than
   // rolling back follows, saved data, credentials or account preferences.
   if(document.getElementById('navigation-panel').open&&navKind==='profile'){renderNavigation();document.querySelectorAll('.bottom-nav button').forEach(button=>button.classList.toggle('active',button.dataset.openPanel==='profile'));}
   for(const [id,view]of Object.entries(snapshot.views)){const node=document.getElementById(id);if(node)node.scrollTop=view.scroll;}
   window.scrollTo({top:snapshot.scroll,behavior:'instant'});
  }finally{requestAnimationFrame(()=>{if(epoch!==restorationEpoch||entry!==entryId)return;for(const [id,view]of Object.entries(snapshot.views)){const node=document.getElementById(id);if(node)node.scrollTop=view.scroll;}window.scrollTo({top:snapshot.scroll,behavior:'instant'});restoring=false;save()});}
 }
 async function restoreRoute(target){
  const epoch=++restorationEpoch,entry=entryId;restoring=true;
  try{
   await Promise.allSettled([window.ElectrolBackend?.ready,window.ElectrolHTMLData?.ready]);
   if(epoch!==restorationEpoch||entry!==entryId)return;
   document.querySelectorAll('dialog[open]').forEach(d=>d.close());
   const page=target?.page||'home';
   if(['home','explore','news'].includes(page))showPrimary(page);
   else if(page.startsWith('article:'))readArticle(page.slice(8));
   else if(page==='search')openUniversal();
   else if(page==='inbox')showInbox();
   else if(page==='compare'&&target.comparison){await loadConfig(target.comparison);}
   else if(page==='election-dashboard'&&target.edition)await openElectionEdition(target.edition);
   else if(page==='lok-sabha'||page==='vidhan-sabha')openElectionHub(page==='lok-sabha'?'lok':'assembly');
   else if(page==='representative-profile'&&target.person)await openRepresentative(target.person);
   else if(page==='representatives')await openPeopleDirectory();
   else if(['parties','constituencies','past','upcoming'].includes(page))await openDiscovery(page);
   else if(/^(party|seat|archive|schedule)-detail:/.test(page)){const i=page.indexOf(':');await openDiscoveryDetail(page.slice(0,i).replace('-detail',''),page.slice(i+1));}
   else if(page==='municipal-directory')await openMunicipalDirectory();
   else if(page.startsWith('municipal:'))await openMunicipalProfile(page.slice(10));
   else if(page.startsWith('municipal-ward:')){const [body,...ward]=page.slice(15).split(':');await openMunicipalProfile(body);await openMunicipalWard(ward.join(':'));}
   else if(page.startsWith('local-directory:'))openLocalBodyDirectory(page.slice(16));
   else if(page.startsWith('local-body:'))await openLocalBodyProfile(page.slice(11));
   else if(page==='mlc-directory')openMLCDirectory();
   else if(page==='mlc-council'&&target.council)openMLCCouncil(target.council);
   else if(page==='detailed-result'&&target.target){await ElectrolHTMLData.edition(target.target.edition);resultDepthTarget=target.target;renderResultDepth();}
   else showDestination(page);
   if(target?.panel){navKind=target.panel.kind;followView=target.panel.view||'following';openNavigation(navKind);if(navKind==='profile')showProfilePage(target.panel.page);}
  }catch{if(epoch===restorationEpoch)showPrimary('home');}finally{if(epoch===restorationEpoch&&entry===entryId){restoring=false;save();replace({...history.state,[key]:marker(entryId)},'',location.href);}}
 }
 window.addEventListener('popstate',event=>{
  const target=event.state?.[key];if(!target)return;
  if(target.session!==session){entryId=++sequence;void restoreRoute(target.route);return;}
  entryId=target.id;const snapshot=entries.get(entryId);
  if(snapshot)void restore(snapshot);else void restoreRoute(target.route);
 });
 const ready=Promise.allSettled([window.ElectrolBackend?.ready,window.ElectrolHTMLData?.ready]).then(async()=>{booting=false;if(!interacted){if(incoming?.route)await restoreRoute(incoming.route);else save();}});
 window.ElectrolNavigation={ready,get current(){return {id:entryId,signature:signature()}},get restoring(){return restoring},flush:commit};
})();
