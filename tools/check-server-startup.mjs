import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {listenWithRecovery} from './server.mjs';
class PreviewServer extends EventEmitter{
 constructor(occupied=[],failure){super();this.occupied=new Set(occupied);this.failure=failure;this.ports=[];}
 listen(port,host){assert.equal(host,'127.0.0.1');this.ports.push(port);queueMicrotask(()=>{if(this.failure)this.emit('error',Object.assign(Error('Access denied'),{code:this.failure}));else if(this.occupied.has(port))this.emit('error',Object.assign(Error('Occupied'),{code:'EADDRINUSE'}));else this.emit('listening');});}
}
const quiet=()=>{};
let server=new PreviewServer(),origins=[];
assert.deepEqual(await listenWithRecovery(server,{log:quiet,onPort:p=>origins.push(p)}),{port:8100,reused:false});assert.deepEqual(origins,[8100]);
server=new PreviewServer([8100]);let probed;
assert.deepEqual(await listenWithRecovery(server,{identity:'this-project',log:quiet,probe:async(p,id)=>{probed=[p,id];return true;}}),{port:8100,reused:true});assert.deepEqual(server.ports,[8100]);assert.deepEqual(probed,[8100,'this-project']);
server=new PreviewServer([8100,8101]);origins=[];
assert.deepEqual(await listenWithRecovery(server,{log:quiet,probe:async()=>false,onPort:p=>origins.push(`http://127.0.0.1:${p}`)}),{port:8102,reused:false});assert.deepEqual(origins,['http://127.0.0.1:8100','http://127.0.0.1:8101','http://127.0.0.1:8102']);
server=new PreviewServer([8100]);assert.equal((await listenWithRecovery(server,{log:quiet,probe:async()=>{throw Error('Network restricted')}})).port,8101);
server=new PreviewServer([8100,8101]);await assert.rejects(listenWithRecovery(server,{log:quiet,probe:async()=>false,maxAttempts:2}),/No available/);
server=new PreviewServer([],'EACCES');await assert.rejects(listenWithRecovery(server,{log:quiet}),/Access denied/);assert.deepEqual(server.ports,[8100]);
server=new PreviewServer();await assert.rejects(listenWithRecovery(server,{port:NaN,log:quiet}),/PORT must/);assert.deepEqual(server.ports,[]);
console.log('Passed: normal start, duplicate project, different project, occupied ports, blocked probe, retry limit, denied socket and invalid port.');
