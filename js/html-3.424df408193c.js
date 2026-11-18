
(function(){function upd(){document.querySelectorAll('.home-options').forEach(function(n){n.dataset.atEnd=(n.scrollWidth<=n.clientWidth+2||n.scrollLeft+n.clientWidth>=n.scrollWidth-2)?'true':'false'})}
var q=0;function sch(){if(q)return;q=requestAnimationFrame(function(){q=0;upd()})}
document.addEventListener('scroll',sch,true);addEventListener('resize',sch);
new MutationObserver(sch).observe(document.body,{childList:true,subtree:true});sch()})();
