"""Bounded VFC run via EGI's registered n8n/ServiceM8 adapter.

Run in the existing EGI GitHub Actions secret context. No credentials in outputs.
Test creates one synthetic draft, replays it, verifies it, then closes it.
Promote additionally updates only the known VFC workflow and Pages environment.
"""
import copy, json, os, secrets, sys, time, uuid, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0,os.environ.get('EGI_ROOT',str(Path.cwd())))
from automation.providers.servicem8.n8n_bridge import ServiceM8ViaN8n, ServiceM8ViaN8nConfig
BASE='https://pmhk.app.n8n.cloud/api/v1'
HOOK='https://pmhk.app.n8n.cloud/webhook'
WORKFLOW_ID='vzI7TNzV6nfMq5tN'
TOKEN=secrets.token_urlsafe(32)
client=ServiceM8ViaN8n(ServiceM8ViaN8nConfig(BASE,HOOK,os.environ['N8N_API_KEY'],'urQ93vMwAVWns3CB','ServiceM8 | Voilà Floor Care | PROD'))
definition=json.loads(Path(os.environ.get('VFC_DEFINITION','vfc-verified-intake.json')).read_text(encoding='utf-8'))
report={'scope':'VFC verified text enquiry intake','customer_contacted':False,'scheduled':False,'invoiced':False,'paid':False}
def obj(value):return value[0] if isinstance(value,list) and value else value
def call(url,method='GET',body=None,headers=None):
    req=urllib.request.Request(url,data=None if body is None else json.dumps(body).encode(),method=method,headers={'Content-Type':'application/json',**(headers or {})})
    try:
        with urllib.request.urlopen(req,timeout=40) as r:return r.status,json.load(r)
    except urllib.error.HTTPError as e:
        try:data=json.load(e)
        except Exception:data={}
        return e.code,data
def cf(method='GET',payload=None):
    if not os.environ.get('CLOUDFLARE_ACCOUNT_ID') or not os.environ.get('CLOUDFLARE_API_TOKEN'):raise RuntimeError('Cloudflare account/token missing in execution context')
    status,data=call('https://api.cloudflare.com/client/v4/accounts/'+os.environ['CLOUDFLARE_ACCOUNT_ID']+'/pages/projects/voila-floor',method,payload,{'Authorization':'Bearer '+os.environ['CLOUDFLARE_API_TOKEN']})
    if status!=200 or data.get('success') is not True:
        report['cloudflare_error_codes']=[e.get('code') for e in data.get('errors',[])]
        raise RuntimeError('VFC Pages configuration HTTP '+str(status))
    return data['result']
def secured(workflow,token,path):
    wf=copy.deepcopy(workflow)
    webhook=next(n for n in wf['nodes'] if n['name']=='Lead Webhook')
    webhook['parameters']['path']=path
    wf['nodes'].append({'id':'Verify Ingress','name':'Verify Ingress','type':'n8n-nodes-base.code','typeVersion':2,'position':[-400,0],'parameters':{'jsCode':"if(String(($json.headers||{})['x-vfc-ingest-token']||'')!=="+json.dumps(token)+")throw new Error('Unauthorised intake');return $input.all();"}})
    wf['connections']['Lead Webhook']={'main':[[{'node':'Verify Ingress','type':'main','index':0}]]}
    wf['connections']['Verify Ingress']={'main':[[{'node':'Normalise + Safety Gate','type':'main','index':0}]]}
    return wf
def main():
    staff=client.call('staff.json')
    if not any(s.get('uuid')=='01a0c8ff-7d66-73c0-b292-1bc897ceb41b' for s in staff):raise RuntimeError('VFC tenant identity mismatch')
    report['tenant_verified']=True
    promote=os.environ.get('VFC_PROMOTE')=='true'
    project=cf() if promote else None
    # Refuse promotion without being able to preserve the existing Pages configuration.
    if project and project.get('name')!='voila-floor':raise RuntimeError('Wrong Pages project')
    temp_path='vfc-intake-proof-'+secrets.token_hex(16)
    staged=secured(definition,TOKEN,temp_path);staged['name']='TEMP | VFC verified intake proof'
    temp=client._n8n('/workflows','POST',staged)
    job_uuid=None
    try:
        client._n8n('/workflows/'+temp['id']+'/activate','POST')
        key=secrets.token_hex(12)
        body={'source':'website','customer_name':'BVP CUSTOMER ZERO — DO NOT SERVICE','email':'vfc-intake-proof@example.invalid','phone':'0400000000','job_address':'Synthetic test only — do not attend','service':'carpet cleaning','message':'Synthetic controlled VFC persistence test; do not contact, schedule, invoice or service.','privacy_consent':True,'correlation_id':str(uuid.uuid4()),'idempotency_key':key,'attachments':[]}
        # Determine the exact synthetic UUID in advance so failed responses can still be cleaned up.
        job_uuid=key[:8]+'-'+key[8:12]+'-4'+key[12:15]+'-8'+key[15:18]+'-'+key[18:]+'000000'
        url=HOOK+'/'+temp_path
        for attempt in range(8):
            status,receipt=call(url,'POST',body,{'x-vfc-ingest-token':TOKEN})
            if status!=404:break
            time.sleep(1)
        if status!=200 or receipt.get('captured') is not True or receipt.get('receipt',{}).get('record_uuid')!=job_uuid:
            # Sanitised execution diagnostics: only node names and error message, never input/output payloads.
            recent=client._n8n('/executions?workflowId='+temp['id']+'&limit=1')
            if recent.get('data'):
                execution=client._n8n('/executions/'+str(recent['data'][0]['id'])+'?includeData=true')
                err=execution.get('data',{}).get('resultData',{}).get('error',{})
                report['failed_node']=err.get('node',{}).get('name')
                report['error_message']=str(err.get('message',''))[:180]
            raise RuntimeError('Staged capture failed HTTP '+str(status))
        first=obj(client.call('job/'+job_uuid+'.json'))
        if first.get('uuid')!=job_uuid or 'VFC intake key: '+key not in first.get('job_description',''):raise RuntimeError('Independent read-back failed')
        if first.get('queue_uuid')!='01a0ce80-1297-7f59-93f0-b46b4afedd4b' or first.get('queue_assigned_staff_uuid')!='01a0c8ff-7d66-73c0-b292-1bc897ceb41b':raise RuntimeError('Lead follow-up queue or owner not persisted')
        body['correlation_id']=str(uuid.uuid4())
        status,replay=call(url,'POST',body,{'x-vfc-ingest-token':TOKEN})
        after=obj(client.call('job/'+job_uuid+'.json'))
        if status!=200 or replay.get('receipt',{}).get('record_uuid')!=job_uuid or first.get('job_description')!=after.get('job_description'):raise RuntimeError('Replay changed or duplicated the record')
        bad_status,_=call(url,'POST',body,{'x-vfc-ingest-token':'invalid'})
        if bad_status<400:raise RuntimeError('Unauthorised request accepted')
        report.update(staged_capture=True,independent_readback=True,replay_same_record=True,unauthorised_rejected=True,synthetic_job_uuid=job_uuid)
    finally:
        if job_uuid:
            try:
                existing=obj(client.call('job/'+job_uuid+'.json'))
                if existing and 'BVP CUSTOMER ZERO' in existing.get('job_description',''):
                    client.call('job/'+job_uuid+'.json','POST',{'status':'Unsuccessful'})
                    report['synthetic_closed']=obj(client.call('job/'+job_uuid+'.json')).get('status')=='Unsuccessful'
            except Exception:report['cleanup_lookup_unavailable']=True
        client._n8n('/workflows/'+temp['id']+'/deactivate','POST')
        client._n8n('/workflows/'+temp['id'],'DELETE')
    if not report.get('synthetic_closed'):raise RuntimeError('Synthetic cleanup not confirmed')
    if promote:
        original=client._n8n('/workflows/'+WORKFLOW_ID)
        if original.get('name') not in ('Voila Floor - Lead Intake - Stage 1 Dry Run',definition['name']):raise RuntimeError('Workflow identity changed')
        updated=secured(definition,TOKEN,'voila-floor-lead-intake')
        envs=copy.deepcopy(project['deployment_configs']['production'].get('env_vars',{}))
        envs['N8N_INGEST_TOKEN']={'type':'secret_text','value':TOKEN}
        envs['N8N_LEAD_WEBHOOK_URL']={'type':'secret_text','value':HOOK+'/voila-floor-lead-intake'}
        client._n8n('/workflows/'+WORKFLOW_ID+'/deactivate','POST')
        try:
            client._n8n('/workflows/'+WORKFLOW_ID,'PUT',updated)
            client._n8n('/workflows/'+WORKFLOW_ID+'/activate','POST')
            cf('PATCH',{'deployment_configs':{'production':{'env_vars':envs}}})
        except Exception:
            client._n8n('/workflows/'+WORKFLOW_ID+'/deactivate','POST')
            client._n8n('/workflows/'+WORKFLOW_ID,'PUT',{k:original[k] for k in ('name','nodes','connections','settings')})
            if original.get('active'):client._n8n('/workflows/'+WORKFLOW_ID+'/activate','POST')
            raise
        reread=client._n8n('/workflows/'+WORKFLOW_ID)
        if reread.get('active') is not True:raise RuntimeError('Promoted workflow not active')
        report.update(promoted=True,workflow_id=WORKFLOW_ID,pages_environment_updated=True,website_redeployment_required=True)
try:
    main();report['passed']=True
except Exception as exc:
    report['passed']=False;report['failure']=str(exc)[:180]
finally:
    print(json.dumps(report,ensure_ascii=True));Path('vfc-intake-proof.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if not report['passed']:sys.exit(1)
