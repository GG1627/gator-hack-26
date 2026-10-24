import { test } from 'node:test';
import assert from 'node:assert/strict';
import {worldPoint,worldCovariance,projectCovariance,pointCloudUrl,contactSlots} from '../src/geometry.mjs';

test('physical axis rotation preserves points, covariance cross terms and eigenvalues',()=>{
  assert.deepEqual(worldPoint([10,20,30],[1,2,3]),[9,27,-18]);
  const c=[4,1,2,1,9,3,2,3,16];
  assert.deepEqual(worldCovariance(c),[4,2,-1,2,16,-3,-1,-3,9]);
  const before=c[0]+c[4]+c[8],after=worldCovariance(c);
  assert.equal(before,after[0]+after[4]+after[8]);
  const multiply=(m,v)=>[0,1,2].map(i=>v.reduce((s,x,j)=>s+m[i*3+j]*x,0));
  const v=[.3,.4,.5],rot=worldPoint(v,[0,0,0]);
  const q=v.reduce((s,x,i)=>s+x*multiply(c,v)[i],0);
  const qRot=rot.reduce((s,x,i)=>s+x*multiply(after,rot)[i],0);
  assert.ok(Math.abs(q-qRot)<1e-12);
});
test('orthographic covariance projection agrees with analytic rotated diagonal case',()=>{
  const s=Math.SQRT1_2;
  const result=projectCovariance([4,0,0,0,9,0,0,0,16],[s,s,0],[-s,s,0]);
  assert.ok(Math.abs(result[0]-6.5)<1e-12);
  assert.ok(Math.abs(result[1]-2.5)<1e-12);
  assert.ok(Math.abs(result[2]-6.5)<1e-12);
});
const run={frame_count:270,sequence_id:'embryo',methods:{photon:{config:{acquired_indices:[0,5,10,20,100,150,269]}}}};
test('spatial point-cloud selection never requests an unacquired or later volume',()=>{
  assert.equal(pointCloudUrl(run,99),'/demo/spatial/embryo/points/20.bin');
  assert.equal(pointCloudUrl(run,100),'/demo/spatial/embryo/points/100.bin');
  assert.equal(pointCloudUrl(run,268),'/demo/spatial/embryo/points/150.bin');
});
test('contact-sheet thumbnails are strictly past acquisitions on the common clock',()=>{
  for(const t of [0,1,99,134,269]){
    const slots=contactSlots(run,'photon',t);
    assert.equal(slots.length,18);
    assert.equal(slots.at(-1).end-slots[0].start+1,72);
    for(const slot of slots){
      if(slot.imageIndex!=null){assert.ok(slot.imageIndex<=t);assert.ok(run.methods.photon.config.acquired_indices.includes(slot.imageIndex));}
      if(slot.kind==='future')assert.equal(slot.imageIndex,null);
    }
  }
});
