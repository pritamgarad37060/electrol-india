/* Shared rules for imported results. An uncontested seat has no poll, not zero votes. */
(()=>{
 'use strict';
 const hasVote=c=>typeof c[2]==='number'&&Number.isFinite(c[2])&&c[2]>=0;
 function pollingCoverage(rows){
  const unopposed=rows.filter(s=>s.status==='unopposed');
  const polled=rows.filter(s=>s.status!=='unopposed');
  const complete=polled.length>0&&polled.every(s=>s.rosterComplete===true&&s.c?.length>0&&s.c.every(hasVote));
  const turnoutAvailable=polled.length>0&&polled.every(s=>typeof s.ballots==='number'&&Number.isFinite(s.ballots)&&s.ballots>=0&&typeof s.electors==='number'&&Number.isFinite(s.electors)&&s.electors>0&&s.ballots<=s.electors);
  const ballots=turnoutAvailable?polled.reduce((n,s)=>n+s.ballots,0):NaN;
  const electors=turnoutAvailable?polled.reduce((n,s)=>n+s.electors,0):NaN;
  return {complete,unopposed:unopposed.length,polled:polled.length,ballots,electors,turnout:turnoutAvailable?100*ballots/electors:NaN};
 }
 globalThis.ElectrolResultMath=Object.freeze({pollingCoverage});
})();
