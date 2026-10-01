const test=require('node:test');
const assert=require('node:assert/strict');
const timeline=require('../website/content/assets/cinematic-timeline.js');
test('markers switch with actual film scenes, in either scroll direction',()=>{
  for(const [time,expected] of [[2,['tile']],[5,['rug','tile']],[9,['carpet','couch']],[12,['carpet']],[16,['shower','stone']],[19,['terracotta']],[9,['carpet','couch']],[2,['tile']]]){
    assert.deepEqual(timeline.sceneAt(time).services,expected);
  }
  assert.deepEqual(timeline.sceneAt(10.8).services,['carpet']);
  assert.deepEqual(timeline.sceneAt(13.2).services,['shower','stone']);
  assert.deepEqual(timeline.sceneAt(12.2).services,['shower','stone']);
});
test('object-fit cover maps source surfaces correctly and rejects cropped surfaces',()=>{
  const centre=timeline.project({x:.5,y:.5},390,844,854,480);
  assert.equal(centre.x,195);
  assert.equal(centre.y,422);
  assert.equal(timeline.project({x:.1,y:.5},390,844,854,480).visible,false);
  const landscape=timeline.project({x:.5,y:.5},1920,1080,854,480);
  assert.equal(landscape.x,960);
  assert.equal(landscape.y,540);
  assert.equal(timeline.projectSurface({x:.65,y:.63},'couch',390,844,854,480).visible,true);
  assert.equal(timeline.projectSurface({x:.1,y:.65},'rug',390,844,854,480).visible,false);
});
test('every surface retains its own valid service page and calibrated track',()=>{
  for(const scene of timeline.scenes)for(const key of scene.services){
    const service=timeline.services[key];
    assert.match(service.href,/^\/services\/[a-z-]+\/$/);
    const point=timeline.pointAt(service.track,scene.start);
    assert.ok(point.x>=0&&point.x<=1&&point.y>=0&&point.y<=1);
  }
  const couch=timeline.pointAt(timeline.services.couch.track,8.5);
  assert.equal(couch.x,.60);
  assert.equal(couch.y,.63);
});
