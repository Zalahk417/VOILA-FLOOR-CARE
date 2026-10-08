"""Prove actual public website capture, independently reread, replay and clean up.

Run in the existing EGI Actions context. The website is the sole job creator.
No customer communication, service booking, invoices or payments are permitted.
"""
import hashlib,json,os,sys,uuid,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,os.environ.get('EGI_ROOT',str(Path.cwd())))
from automation.providers.servicem8.n8n_bridge import ServiceM8ViaN8n,ServiceM8ViaN8nConfig
client=ServiceM8ViaN8n(ServiceM8ViaN8nConfig('https://pmhk.app.n8n.cloud/api/v1','https://pmhk.app.n8n.cloud/webhook',os.environ['N8N_API_KEY'],'urQ93vMwAVWns3CB','ServiceM8 | Voilà Floor Care | PROD'))
body={'submission_id':str(uuid.uuid4()),'customer_name':'BVP CUSTOMER ZERO - DO NOT SERVICE','email':'vfc-public-proof@example.invalid','phone':'0400000000','job_address':'Synthetic proof only - do not attend','service':'carpet cleaning','message':'Controlled VFC public website persistence proof. Do not contact, schedule, invoice, charge or service.','privacy_consent':'yes','customer_type':'','measurements':'','preferred_timing':'','attachments':[]}
canonical={'submission_id':body['submission_id'],'source':'website','customer_name':body['customer_name'].lower(),'email':body['email'].lower(),'phone':body['phone'],'job_address':body['job_address'].lower(),'service':body['service'].lower(),'message':body['message'].lower(),'customer_type':'','measurements':'','preferred_timing':'','attachments':[]}
key=hashlib.sha256(json.dumps(canonical,separators=(',',':')).encode()).hexdigest()[:24]
job_id=key[:8]+'-'+key[8:12]+'-4'+key[12:15]+'-8'+key[15:18]+'-'+key[18:]+'000000'
report={'scope':'public website to VFC ServiceM8','website':'https://voilafloor.com.au/api/enquiry','customer_contacted':False,'scheduled':False,'invoiced':False,'paid':False,'synthetic_job_uuid':job_id}
def one(value):return value[0] if isinstance(value,list) and value else value
def submit(payload):
    req=urllib.request.Request(report['website'],data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'VFC-authorised-proof/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=40) as r:return r.status,json.load(r)
    except urllib.error.HTTPError as e:return e.code,{}
try:
    status,receipt=submit(body)
    report['website_http_status']=status
    assert status==200 and receipt.get('ok') is True and receipt.get('captured') is True and receipt.get('correlation_id'),'Website capture not acknowledged'
    report['correlation_id']=receipt['correlation_id']
    first=one(client.call('job/'+job_id+'.json'))
    assert first.get('uuid')==job_id and receipt['correlation_id'] in first.get('job_description',''),'Website-created record not independently verified'
    assert first.get('status')=='Quote' and first.get('queue_uuid')=='01a0ce80-1297-7f59-93f0-b46b4afedd4b' and first.get('queue_assigned_staff_uuid')=='01a0c8ff-7d66-73c0-b292-1bc897ceb41b','Draft ownership/queue missing'
    report.update(captured=True,independent_readback=True,queue_and_owner_verified=True)
    status,replay=submit(body)
    after=one(client.call('job/'+job_id+'.json'))
    assert status==200 and replay.get('captured') is True and first.get('job_description')==after.get('job_description'),'Retry did not preserve same record'
    report['replay_same_record']=True
    status,_=submit({**body,'privacy_consent':'no'})
    assert status==400,'Missing consent not rejected'
    report['invalid_consent_rejected']=True
except Exception as exc:
    report['failure']=str(exc)[:150]
finally:
    try:
        record=one(client.call('job/'+job_id+'.json'))
        if record and 'BVP CUSTOMER ZERO' in record.get('job_description','') and key in record.get('job_description',''):
            client.call('job/'+job_id+'.json','POST',{'status':'Unsuccessful'})
            report['synthetic_closed']=one(client.call('job/'+job_id+'.json')).get('status')=='Unsuccessful'
    except Exception:report['cleanup_lookup_unavailable']=True
    report['passed']='failure' not in report and report.get('synthetic_closed') is True
    print(json.dumps(report));Path('vfc-public-intake-proof.json').write_text(json.dumps(report,indent=2))
if not report['passed']:sys.exit(1)
