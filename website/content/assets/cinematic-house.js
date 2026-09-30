(()=> {
  const shell=document.getElementById('house-tour');
  const stage=shell?.querySelector('.scrub-stage');
  const video=document.getElementById('house-film');
  const bar=document.getElementById('progress-bar');
  const chapters=[...document.querySelectorAll('.chapter')];
  const hotspots=[...document.querySelectorAll('.surface-hotspot')];
  const sceneNumber=document.getElementById('scene-number');
  const sceneName=document.getElementById('scene-name');
  const sceneServices=document.getElementById('scene-services');
  const welcome=document.getElementById('welcome-layer');
  const startTour=document.getElementById('start-tour');
  const leadForm=document.getElementById('house-lead-form');
  const photoInput=document.getElementById('lead-photos');
  const photoSummary=document.getElementById('photo-summary');
  const leadStatus=document.getElementById('lead-status');
  if(!shell||!stage||!video)return;

  let duration=20,raf=0,ready=false,last=-1,lastScene=-1;

  const scenes=[
    {start:0,end:.22,no:'01',name:'Entry · Tile & Grout',services:[['Tile & Grout','/services/tile-grout-cleaning/']]},
    {start:.22,end:.42,no:'02',name:'Living · Rug & Tile',services:[['Rug & Wool','/services/rug-cleaning/'],['Tile & Grout','/services/tile-grout-cleaning/']]},
    {start:.42,end:.59,no:'03',name:'Lounge · Carpet & Upholstery',services:[['Carpet & Wool','/services/carpet-cleaning/'],['Couch & Leather','/services/upholstery-leather/']]},
    {start:.59,end:.77,no:'04',name:'Ensuite · Shower & Stone',services:[['Shower & Grout','/services/tile-grout-cleaning/'],['Natural Stone','/services/natural-stone/']]},
    {start:.77,end:1.01,no:'05',name:'Terrace · Terracotta',services:[['Terracotta & Sealing','/services/floor-sealing-finishing/'],['Natural Stone','/services/natural-stone/']]}
  ];

  const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
  const progress=()=>{
    const r=shell.getBoundingClientRect();
    const range=Math.max(1,shell.offsetHeight-innerHeight);
    return clamp(-r.top/range,0,1);
  };
  const parseTrack=(value='')=>value.split(';').map(row=>row.split(',').map(Number))
    .filter(row=>row.length===3&&row.every(Number.isFinite))
    .map(([p,x,y])=>({p,x,y})).sort((a,b)=>a.p-b.p);
  hotspots.forEach(el=>{el._track=parseTrack(el.dataset.track)});

  const trackPoint=(points,p)=>{
    if(!points.length)return null;
    if(p<=points[0].p)return points[0];
    if(p>=points[points.length-1].p)return points[points.length-1];
    for(let i=0;i<points.length-1;i++){
      const a=points[i],b=points[i+1];
      if(p>=a.p&&p<=b.p){
        const t=(p-a.p)/Math.max(.00001,b.p-a.p);
        return{x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t,p};
      }
    }
    return points[points.length-1];
  };
  const project=(x,y)=>{
    const r=stage.getBoundingClientRect();
    return{x:x*r.width,y:y*r.height};
  };
  const placeHotspots=(p)=>{
    hotspots.forEach(el=>{
      const a=Number(el.dataset.start)||0,b=Number(el.dataset.end)||1;
      const active=p>=a&&p<b;
      el.hidden=!active;
      el.tabIndex=active?0:-1;
      el.setAttribute('aria-hidden',active?'false':'true');
      if(active){
        const point=trackPoint(el._track,p);
        if(point){
          const pos=project(point.x,point.y);
          el.style.left=pos.x.toFixed(1)+'px';
          el.style.top=pos.y.toFixed(1)+'px';
        }
      }
    });
  };
  const setScene=(p)=>{
    const idx=Math.max(0,scenes.findIndex(s=>p>=s.start&&p<s.end));
    const scene=scenes[idx<0?scenes.length-1:idx]||scenes[scenes.length-1];
    if(idx===lastScene)return;
    lastScene=idx;
    if(sceneNumber)sceneNumber.textContent=scene.no;
    if(sceneName)sceneName.textContent=scene.name;
    if(sceneServices){
      sceneServices.replaceChildren(...scene.services.map(([label,href])=>{
        const a=document.createElement('a');
        a.href=href;
        a.textContent=label+' →';
        return a;
      }));
    }
  };
  const setWelcome=(p)=>{
    if(!welcome)return;
    const exit=clamp(p/.14,0,1);
    welcome.style.setProperty('--welcome-exit',exit.toFixed(3));
    welcome.setAttribute('aria-hidden',exit>.985?'true':'false');
  };
  const setVideoTime=(p)=>{
    if(!ready)return;
    const terraceHold=Math.max(.01,duration-2.05);
    const t=p>=.90?terraceHold:Math.min(p*duration,terraceHold);
    if(Math.abs(video.currentTime-t)>.035)video.currentTime=t;
  };
  const update=()=>{
    raf=0;
    const p=progress();
    if(bar)bar.style.width=(p*100).toFixed(2)+'%';
    chapters.forEach(el=>{
      const a=Number(el.dataset.start)||0,b=Number(el.dataset.end)||1;
      el.classList.toggle('is-active',p>=a&&p<b);
    });
    setWelcome(p);
    placeHotspots(p);
    setScene(p);
    if(Math.abs(p-last)>.0008){last=p;setVideoTime(p)}
  };
  const request=()=>{if(!raf)raf=requestAnimationFrame(update)};

  video.addEventListener('loadedmetadata',()=>{
    duration=Number.isFinite(video.duration)&&video.duration>0?video.duration:20;
    ready=true;
    try{video.currentTime=.01}catch{}
    update();
  });
  video.addEventListener('canplay',()=>{ready=true;request()});
  addEventListener('scroll',request,{passive:true});
  addEventListener('resize',request,{passive:true});

  if(startTour)startTour.addEventListener('click',()=>{
    const range=Math.max(1,shell.offsetHeight-innerHeight);
    const top=scrollY+shell.getBoundingClientRect().top+range*.16;
    scrollTo({top,behavior:'smooth'});
  });

  const prime=()=>{
    if(video.readyState<1)video.load();
    if(video.paused){
      const p=video.play();
      if(p&&p.then)p.then(()=>video.pause()).catch(()=>{});
    }
  };
  addEventListener('touchstart',prime,{once:true,passive:true});
  addEventListener('pointerdown',prime,{once:true,passive:true});

  const filesSelected=()=>Array.from(photoInput?.files||[]);
  const refreshPhotoSummary=()=>{
    if(!photoSummary)return;
    const files=filesSelected();
    if(!files.length){photoSummary.textContent='Up to 4 images · JPG, PNG or WebP · 3 MB each';return}
    photoSummary.textContent=files.length===1?files[0].name:files.length+' photos selected';
  };
  if(photoInput)photoInput.addEventListener('change',refreshPhotoSummary);

  const readAsDataURL=file=>new Promise((resolve,reject)=>{
    const reader=new FileReader();
    reader.onload=()=>resolve(String(reader.result||''));
    reader.onerror=()=>reject(new Error('Could not read photo'));
    reader.readAsDataURL(file);
  });

  if(leadForm)leadForm.addEventListener('submit',async e=>{
    e.preventDefault();
    if(leadStatus){leadStatus.textContent='Preparing your enquiry…';leadStatus.classList.remove('is-error')}
    const form=new FormData(leadForm);
    const files=filesSelected();
    if(files.length>4){
      if(leadStatus){leadStatus.textContent='Please choose no more than 4 photos.';leadStatus.classList.add('is-error')}
      return;
    }
    const tooLarge=files.find(file=>file.size>3*1024*1024);
    if(tooLarge){
      if(leadStatus){leadStatus.textContent=tooLarge.name+' is over 3 MB.';leadStatus.classList.add('is-error')}
      return;
    }
    let attachments=[];
    try{
      attachments=await Promise.all(files.map(async file=>({
        name:file.name.slice(0,120),
        type:file.type,
        size:file.size,
        data_url:await readAsDataURL(file)
      })));
    }catch{
      if(leadStatus){leadStatus.textContent='One of the photos could not be read.';leadStatus.classList.add('is-error')}
      return;
    }
    const payload={
      customer_name:String(form.get('customer_name')||''),
      phone:String(form.get('phone')||''),
      email:String(form.get('email')||''),
      job_address:String(form.get('job_address')||''),
      service:String(form.get('service')||'Floor care enquiry'),
      customer_type:'Residential / property',
      measurements:'',
      preferred_timing:'',
      message:String(form.get('message')||''),
      privacy_consent:form.get('privacy_consent')==='yes'?'yes':'no',
      attachments
    };
    try{
      const res=await fetch('/api/enquiry',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
      const out=await res.json().catch(()=>({}));
      if(!res.ok||!out.ok)throw new Error(out.error||'Enquiry could not be sent');
      leadForm.reset();
      refreshPhotoSummary();
      if(leadStatus){
        leadStatus.textContent='Sent. Reference: '+(out.correlation_id||'received')+'. We’ll be in touch.';
        leadStatus.classList.remove('is-error');
      }
    }catch(err){
      if(leadStatus){
        leadStatus.textContent=String(err?.message||'Enquiry could not be sent. Please call 0402 221 071.');
        leadStatus.classList.add('is-error');
      }
    }
  });

  request();
})();