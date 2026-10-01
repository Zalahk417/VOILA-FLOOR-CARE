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

  const timeline=window.VoilaTourTimeline;
  if(!timeline)return;
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
  let duration=20,raf=0,ready=false,targetTime=0,presentedTime=0,lastScene='',seekPending=false;
  const frameCallbacks=typeof video.requestVideoFrameCallback==='function';
  // Reset fresh visits and reloads; preserve Back/Forward and intentional anchors.
  const navigationEntry=performance.getEntriesByType?.('navigation')?.[0];
  if(!location.hash&&navigationEntry?.type!=='back_forward'){
    if('scrollRestoration' in history)history.scrollRestoration='manual';
    scrollTo({top:0,behavior:'instant'});
  }

  const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
  const progress=()=>{
    const r=shell.getBoundingClientRect();
    const range=Math.max(1,shell.offsetHeight-innerHeight);
    return clamp(-r.top/range,0,1);
  };
  const placeHotspots=(time,scene)=>{
    const r=stage.getBoundingClientRect();
    const zoom=time>=18.4?1+clamp((time-18.4)/1.3,0,1)*.32:1;
    video.style.transform='scale('+zoom+')';
    hotspots.forEach(el=>{
      const service=timeline.services[el.dataset.service];
      const point=service&&timeline.pointAt(service.track,time);
      const pos=point&&timeline.projectSurface(point,el.dataset.service,r.width,r.height,video.videoWidth||854,video.videoHeight||480,zoom);
      const active=ready&&!shell.classList.contains('media-unavailable')&&!reducedMotion.matches&&time>.9&&scene.services.includes(el.dataset.service)&&pos.visible;
      el.hidden=!active;
      el.tabIndex=active?0:-1;
      el.setAttribute('aria-hidden',active?'false':'true');
      if(active){
        // Keep the label in view while the pointer retains the surface's true coordinate.
        const half=el.offsetWidth/2+8;
        const labelX=clamp(pos.x,half,r.width-half);
        el.style.left=labelX.toFixed(1)+'px';
        el.style.top=pos.y.toFixed(1)+'px';
        el.style.setProperty('--pointer-shift',(pos.x-labelX).toFixed(1)+'px');
      }
    });
  };
  const setScene=(scene)=>{
    if(scene.no===lastScene)return;
    lastScene=scene.no;
    if(sceneNumber)sceneNumber.textContent=scene.no;
    if(sceneName)sceneName.textContent=scene.name;
    if(sceneServices){
      sceneServices.replaceChildren(...scene.services.map(key=>{
        const {label,href}=timeline.services[key];
        const a=document.createElement('a');
        a.href=href;
        a.textContent=label+' →';
        return a;
      }));
    }
  };
  const setWelcome=(p)=>{
    if(!welcome)return;
    const fadeStart=.005,fadeEnd=.085;
    const exit=clamp((p-fadeStart)/(fadeEnd-fadeStart),0,1);
    welcome.style.opacity=(1-exit).toFixed(3);
    welcome.style.transform='translateY('+(-34*exit).toFixed(1)+'px)';
    welcome.style.visibility=exit>=.999?'hidden':'visible';
    welcome.setAttribute('aria-hidden',exit>=.999?'true':'false');
    welcome.inert=exit>=.999;
    stage.classList.toggle('tour-started',exit>=.999);
    const readout=stage.querySelector('.scene-readout');
    if(readout)readout.inert=exit<.999;
    const worker=welcome.querySelector('.welcome-worker');
    if(worker) worker.style.transform='translateY('+(-18*exit).toFixed(1)+'px) scale('+(1+.018*exit).toFixed(4)+')';
  };
  const seek=()=>{
    if(!ready||seekPending||video.seeking||reducedMotion.matches)return;
    if(Math.abs(video.currentTime-targetTime)>.035){
      seekPending=true;
      try{video.currentTime=targetTime}catch{seekPending=false}
    }
  };
  const update=()=>{
    raf=0;
    const p=progress();
    if(bar)bar.style.width=(p*100).toFixed(2)+'%';
    const time=presentedTime;
    const unavailable=shell.classList.contains('media-unavailable');
    const finalActive=reducedMotion.matches||unavailable||(p>=.90&&time>=18.4);
    chapters.forEach(el=>{
      el.classList.toggle('is-active',finalActive);
      el.inert=!finalActive;
      el.setAttribute('aria-hidden',finalActive?'false':'true');
    });
    stage.classList.toggle('is-final',finalActive);
    setWelcome(reducedMotion.matches||unavailable?0:p);
    const scene=timeline.sceneAt(time);
    placeHotspots(time,scene);
    setScene(scene);
    const end=Math.min(19.7,Math.max(.01,duration-.1));
    targetTime=clamp(p/.90,0,1)*end;
    seek();
  };
  const request=()=>{if(!raf)raf=requestAnimationFrame(update)};

  video.addEventListener('loadedmetadata',()=>{
    duration=Number.isFinite(video.duration)&&video.duration>0?video.duration:20;
    ready=true;
    update();
  });
  video.addEventListener('loadeddata',()=>{ready=true;if(!frameCallbacks)presentedTime=video.currentTime;request()});
  video.addEventListener('seeked',()=>{
    seekPending=false;
    if(!frameCallbacks)presentedTime=video.currentTime;
    request();
  });
  if(frameCallbacks){
    const onFrame=(_,metadata)=>{
      presentedTime=metadata.mediaTime;
      request();
      video.requestVideoFrameCallback(onFrame);
    };
    video.requestVideoFrameCallback(onFrame);
  }
  addEventListener('scroll',request,{passive:true});
  addEventListener('resize',request,{passive:true});
  addEventListener('pageshow',request);
  reducedMotion.addEventListener('change',request);

  if(startTour)startTour.addEventListener('click',()=>{
    const range=Math.max(1,shell.offsetHeight-innerHeight);
    const top=scrollY+shell.getBoundingClientRect().top+range*.095;
    scrollTo({top,behavior:'smooth'});
  });

  video.addEventListener('error',()=>{
    shell.classList.add('media-unavailable');
    hotspots.forEach(el=>{el.hidden=true});
    request();
  });

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
