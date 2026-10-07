"""Build VFC-specific intake using standard n8n nodes and the existing EGI binding."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build():
    stage=json.loads((ROOT/'n8n/voila-floor-lead-intake-stage1.json').read_text(encoding='utf-8'))
    nodes=stage['nodes'][:2]
    credential={'serviceM8CredentialsApi':{'id':'urQ93vMwAVWns3CB','name':'ServiceM8 | Voilà Floor Care | PROD'}}
    def code(name,text):
        nodes.append({'id':name,'name':name,'type':'n8n-nodes-base.code','typeVersion':2,'position':[len(nodes)*240,0],'parameters':{'jsCode':text}})
    def http(name,url,method='GET',body=None):
        p={'url':url,'authentication':'predefinedCredentialType','nodeCredentialType':'serviceM8CredentialsApi','options':{'response':{'response':{'fullResponse':True,'neverError':True}}}}
        if method!='GET':p['method']=method
        if body:p.update(sendBody=True,contentType='raw',rawContentType='application/json',body=body)
        nodes.append({'id':name,'name':name,'type':'n8n-nodes-base.httpRequest','typeVersion':4.2,'position':[len(nodes)*240,0],'parameters':p,'credentials':credential,'alwaysOutputData':True})
    code('Prepare Intake',(ROOT/'n8n/intake-prepare.js').read_text(encoding='utf-8'))
    joburl='={{ "https://api.servicem8.com/api_1.0/job/"+$node["Prepare Intake"].json.uuid+".json" }}'
    http('Find Existing Job',joburl)
    code('Check Existing Job',"const p=$node['Prepare Intake'].json; const status=Number($json.statusCode); const job=$json.body; if(status===404)return [{json:{exists:false}}]; if(status===200&&job?.uuid===p.uuid&&String(job.job_description||'').includes('VFC intake key: '+p.key))return [{json:{exists:true}}]; throw new Error('Provider lookup failed or conflicting record');")
    nodes.append({'id':'Already Saved','name':'Already Saved','type':'n8n-nodes-base.if','typeVersion':2.2,'position':[1200,0],'parameters':{'conditions':{'options':{'caseSensitive':True,'leftValue':'','typeValidation':'strict','version':2},'conditions':[{'id':'exists','leftValue':'={{ $json.exists }}','rightValue':True,'operator':{'type':'boolean','operation':'true','singleValue':True}}],'combinator':'and'},'options':{}}})
    http('Create Intake Job','https://api.servicem8.com/api_1.0/job.json','POST','={{ JSON.stringify($node["Prepare Intake"].json.payload) }}')
    # Read back even after an ambiguous create response; never blindly create another ID.
    http('Verify Saved Job',joburl)
    code('Verified Receipt',"const p=$node['Prepare Intake'].json; const job=$json.body; if(Number($json.statusCode)!==200||job?.uuid!==p.uuid||!String(job.job_description||'').includes('VFC intake key: '+p.key))throw new Error('No verified saved job');return [{json:{ok:true,captured:true,correlation_id:p.correlation,receipt:{system:'servicem8',record_uuid:p.uuid,verified:true,idempotency_key:p.key}}}];")
    nodes.append({'id':'Return Receipt','name':'Return Receipt','type':'n8n-nodes-base.respondToWebhook','typeVersion':1.4,'position':[2400,0],'parameters':{'respondWith':'json','responseBody':'={{ $json }}','options':{}}})
    def edge(target):return [{'node':target,'type':'main','index':0}]
    connections={a:{'main':[edge(b)]} for a,b in [('Lead Webhook','Normalise + Safety Gate'),('Normalise + Safety Gate','Prepare Intake'),('Prepare Intake','Find Existing Job'),('Find Existing Job','Check Existing Job'),('Check Existing Job','Already Saved'),('Create Intake Job','Verify Saved Job'),('Verify Saved Job','Verified Receipt'),('Verified Receipt','Return Receipt')]}
    connections['Already Saved']={'main':[edge('Verify Saved Job'),edge('Create Intake Job')]}
    return {'name':'Voila Floor - Verified Lead Intake','nodes':nodes,'connections':connections,'settings':{'executionOrder':'v1','saveDataSuccessExecution':'none','saveDataErrorExecution':'none','saveManualExecutions':False}}
if __name__=='__main__':
    (ROOT/'n8n/voila-floor-verified-intake.json').write_text(json.dumps(build(),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
