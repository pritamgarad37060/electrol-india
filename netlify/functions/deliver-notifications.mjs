import {deliverEmail} from '../lib/update-jobs.mjs';
export default async (_request,context)=>{if(!context?.server?.region)return new Response('Scheduled invocation required',{status:403});try{return Response.json(await deliverEmail());}catch{return Response.json({error:'notification_delivery_not_ready'},{status:503});}};
export const config={schedule:'*/5 * * * *'};
