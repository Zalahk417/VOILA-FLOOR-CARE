/* Coordinates are calibrated on the 854 × 480 master film, in decoded seconds. */
((root)=>{
  const scenes=[
    {start:0,end:3.8,no:'01',name:'Entry · Tile & Grout',services:['tile']},
    {start:3.8,end:6.6,no:'02',name:'Living · Rug & Tile',services:['rug','tile']},
    {start:6.6,end:10.8,no:'03',name:'Lounge · Carpet & Upholstery',services:['carpet','couch']},
    {start:10.8,end:12.2,no:'04',name:'Hallway · Carpet',services:['carpet']},
    {start:12.2,end:18.4,no:'05',name:'Ensuite · Shower & Stone',services:['shower','stone']},
    {start:18.4,end:Infinity,no:'06',name:'Terrace · Terracotta',services:['terracotta']}
  ];
  const services={
    tile:{label:'Tile & Grout',href:'/services/tile-grout-cleaning/',track:[[0,.5,.84],[3.8,.55,.85],[5,.34,.85],[6.6,.22,.88]]},
    rug:{label:'Rug & Wool',href:'/services/rug-cleaning/',track:[[3.8,.43,.60],[4.5,.33,.62],[5.5,.20,.65],[6.6,.09,.66]]},
    carpet:{label:'Carpet & Wool',href:'/services/carpet-cleaning/',track:[[6.6,.70,.83],[8,.58,.83],[9,.52,.85],[10,.40,.84],[10.8,.31,.85],[12,.38,.88],[13.2,.28,.88]]},
    couch:{label:'Couch & Leather',href:'/services/upholstery-leather/',track:[[6.6,.66,.60],[7.5,.66,.63],[8.5,.60,.63],[9.5,.48,.64],[10,.27,.66],[10.8,.06,.66]]},
    shower:{label:'Shower & Grout',href:'/services/tile-grout-cleaning/',track:[[12.2,.74,.68],[13.2,.68,.65],[14.5,.60,.68],[15.5,.56,.70],[16.5,.49,.70],[17.5,.39,.70],[18.4,.20,.73]]},
    stone:{label:'Natural Stone',href:'/services/natural-stone/',track:[[12.2,.72,.89],[13.2,.53,.88],[14.5,.45,.89],[16,.40,.89],[17.5,.27,.88],[18.4,.12,.88]]},
    terracotta:{label:'Terracotta & Sealing',href:'/services/floor-sealing-finishing/',track:[[18.4,.74,.84],[19,.66,.84],[19.7,.62,.84],[20,.60,.84]]}
  };
  const sceneAt=time=>scenes.find(scene=>time>=scene.start&&time<scene.end)||scenes[0];
  // Approximate horizontal surface bounds around each calibrated anchor. A narrow
  // viewport may crop the anchor while still showing part of the same surface.
  const horizontalExtent={tile:.20,rug:.10,carpet:.18,couch:.16,shower:.08,stone:.12,terracotta:.24};
  const pointAt=(track,time)=>{
    if(time<=track[0][0])return {x:track[0][1],y:track[0][2]};
    for(let i=1;i<track.length;i++){
      if(time<=track[i][0]){
        const a=track[i-1],b=track[i],mix=(time-a[0])/(b[0]-a[0]);
        return {x:a[1]+(b[1]-a[1])*mix,y:a[2]+(b[2]-a[2])*mix};
      }
    }
    const last=track[track.length-1];return {x:last[1],y:last[2]};
  };
  const project=(point,width,height,videoWidth,videoHeight,zoom=1)=>{
    const scale=Math.max(width/videoWidth,height/videoHeight);
    const x=(point.x*videoWidth*scale-(videoWidth*scale-width)/2)*zoom-width*(zoom-1);
    const y=(point.y*videoHeight*scale-(videoHeight*scale-height)/2)*zoom-height*(zoom-1)/2;
    return {x,y,visible:x>=0&&x<=width&&y>=0&&y<=height};
  };
  const projectSurface=(point,key,width,height,videoWidth,videoHeight,zoom=1)=>{
    const result=project(point,width,height,videoWidth,videoHeight,zoom);
    if(!result.visible&&result.y>=0&&result.y<=height){
      const radius=horizontalExtent[key]||0;
      const left=project({x:point.x-radius,y:point.y},width,height,videoWidth,videoHeight,zoom);
      const right=project({x:point.x+radius,y:point.y},width,height,videoWidth,videoHeight,zoom);
      if(right.x>=20&&left.x<=width-20){
        result.x=Math.max(20,Math.min(width-20,result.x));
        result.visible=true;
      }
    }
    return result;
  };
  const api={scenes,services,sceneAt,pointAt,project,projectSurface};
  root.VoilaTourTimeline=api;
  if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
