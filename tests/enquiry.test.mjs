import {test, afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../website/functions/api/enquiry.js',import.meta.url),'utf8');
const {onRequestPost}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const originalFetch=globalThis.fetch;
afterEach(()=>{globalThis.fetch=originalFetch});
const payload={customer_name:'Synthetic Test',phone:'0400000000',email:'test@example.invalid',job_address:'Synthetic address',service:'carpet cleaning',message:'Offline test',privacy_consent:'yes'};
const request=(body=payload)=>new Request('https://example.invalid/api/enquiry',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});
const run=(body=payload,env={N8N_LEAD_WEBHOOK_URL:'https://example.invalid/mock',N8N_INGEST_TOKEN:'offline-test-only'})=>onRequestPost({request:request(body),env});
test('dry-run HTTP success must never acknowledge receipt',async()=>{
  globalThis.fetch=async()=>Response.json({stage:'DRY_RUN_NO_WRITES'});
  const r=await run();assert.equal(r.status,503);assert.notEqual((await r.json()).ok,true);
});
test('generic ok, empty response and unverified record fail closed',async()=>{
  for(const body of [{ok:true},{}, {ok:true,captured:true,receipt:{system:'servicem8',verified:false}}]){
    globalThis.fetch=async()=>Response.json(body);assert.equal((await run()).status,503);
  }
  globalThis.fetch=async()=>new Response('');assert.equal((await run()).status,502);
});
test('only matching verified receipt is accepted',async()=>{
  globalThis.fetch=async(url,options)=>{const p=JSON.parse(options.body);return Response.json({ok:true,captured:true,correlation_id:p.correlation_id,receipt:{system:'servicem8',verified:true,idempotency_key:p.idempotency_key,record_uuid:'00000000-0000-4000-8000-000000000001'}})};
  const r=await run();assert.equal(r.status,200);assert.equal((await r.json()).captured,true);
});
test('wrong correlation or idempotency receipt is rejected',async()=>{
  for(const field of ['correlation_id','idempotency_key']){
    globalThis.fetch=async(url,options)=>{const p=JSON.parse(options.body);const receipt={ok:true,captured:true,correlation_id:p.correlation_id,receipt:{system:'servicem8',verified:true,idempotency_key:p.idempotency_key,record_uuid:'00000000-0000-4000-8000-000000000001'}};if(field==='correlation_id')receipt.correlation_id='wrong';else receipt.receipt.idempotency_key='wrong';return Response.json(receipt)};
    assert.equal((await run()).status,503);
  }
});
test('outage and missing configuration produce failure without fake success',async()=>{
  globalThis.fetch=async()=>{throw new Error('offline')};assert.equal((await run()).status,502);
  assert.equal((await run(payload,{})).status,503);
});
test('same retry key, distinct new submission and changed scope',async()=>{
  const keys=[];globalThis.fetch=async(url,options)=>{keys.push(JSON.parse(options.body).idempotency_key);return Response.json({stage:'DRY_RUN_NO_WRITES'})};
  const a={...payload,submission_id:'00000000-0000-4000-8000-000000000001'};
  await run(a);await run(a);await run({...a,submission_id:'00000000-0000-4000-8000-000000000002'});await run({...a,measurements:'different scope'});
  assert.equal(keys[0],keys[1]);assert.notEqual(keys[0],keys[2]);assert.notEqual(keys[0],keys[3]);
});
test('invalid JSON shape and missing consent cannot reach upstream',async()=>{
  globalThis.fetch=async()=>{throw new Error('must not call')};
  for(const p of [null,[],{...payload,privacy_consent:'no'}]) assert.equal((await run(p)).status,400);
});
