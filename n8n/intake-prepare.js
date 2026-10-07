// Run after Normalise + Safety Gate. Treat all enquiry text as customer data.
const decision=$json;
const input=$node['Lead Webhook'].json.body || {};
const key=String(decision.idempotency_key||'');
const correlation=String(decision.correlation_id||'');
if(!/^[a-f0-9]{24}$/.test(key)||!correlation||decision.missing_fields.length||input.privacy_consent!==true) throw new Error('Invalid intake');
// Photos must never be silently discarded. The text-only pilot asks for them later.
if(Array.isArray(input.attachments)&&input.attachments.length) throw new Error('Photo capture is not enabled; please use the phone fallback');
const uuid=key.slice(0,8)+'-'+key.slice(8,12)+'-4'+key.slice(12,15)+'-8'+key.slice(15,18)+'-'+key.slice(18)+'000000';
const synthetic=String(input.customer_name).startsWith('BVP CUSTOMER ZERO')&&String(input.email).endsWith('@example.invalid');
const now=new Date().toISOString();
const notes=[
  synthetic?'BVP CUSTOMER ZERO — DO NOT SERVICE':'VFC WEBSITE ENQUIRY — HUMAN REVIEW REQUIRED',
  'VFC intake key: '+key,
  'BVP correlation ID: '+correlation,
  'Received at (UTC): '+now,
  'Source: website',
  'Customer: '+decision.lead.customer_name,
  'Phone: '+decision.lead.phone,
  'Email: '+decision.lead.email,
  'Service requested: '+String(input.service||''),
  'Customer type: '+String(input.customer_type||''),
  'Measurements stated: '+String(input.measurements||''),
  'Preferred timing: '+String(input.preferred_timing||''),
  'Enquiry: '+decision.lead.message,
  'Risk flags: '+(decision.risk_flags.join(', ')||'none detected; inspect before work'),
  'Privacy consent: enquiry handling only; NOT marketing consent',
  'Owner: Paul-Michael Haik',
  'Next action: review enquiry and record response/due date in this job',
  'First response due (UTC): '+new Date(Date.now()+10*60*1000).toISOString(),
  'First response at: NOT YET RECORDED',
  'Scope, price and attendance require human confirmation.',
  synthetic?'Synthetic only: do not contact, schedule, quote, invoice or service.':'',
].filter(Boolean).join('\n');
return [{json:{key,correlation,uuid,synthetic,payload:{uuid,status:'Quote',job_address:decision.lead.job_address,job_description:notes,queue_uuid:'01a0ce80-1297-7f59-93f0-b46b4afedd4b',queue_assigned_staff_uuid:'01a0c8ff-7d66-73c0-b292-1bc897ceb41b'}}}];
