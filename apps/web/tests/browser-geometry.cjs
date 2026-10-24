// Run with the Playwright CLI's run-code --filename option on the dev preview.
// Uses the actual production shader, reads GPU alpha values and independently
// evaluates the projected covariance quadratic form at every pixel center.
async (page) => {
  const result=await page.evaluate(async()=>{
    const source=await(await fetch('/src/Viewer3D.tsx')).text();
    const match=source.match(/import\s+\*\s+as\s+THREE\s+from\s+["']([^"']+)["']/);
    if(!match)throw new Error('Could not resolve the dev module Three.js import');
    const T=await import(match[1]);
    const {splatVertex,splatFragment}=await import('/src/Viewer3D.tsx');
    const renderer=new T.WebGLRenderer({alpha:true,antialias:false,premultipliedAlpha:false});
    const n=129;renderer.setSize(n,n,false);renderer.setClearColor(0,0);
    const target=new T.WebGLRenderTarget(n,n,{format:T.RGBAFormat,type:T.UnsignedByteType});
    const camera=new T.OrthographicCamera(-4,4,4,-4,.1,100);
    camera.position.set(0,0,8);camera.lookAt(0,0,0);
    const cases=[{name:'diagonal',c:[.36,0,0,0,.81,0,0,0,.49],angle:0},{name:'rotated cross-covariance',c:[.5,.18,.08,.18,.9,-.12,.08,-.12,.6],angle:.63},{name:'thin anisotropic',c:[.03,.02,.01,.02,1.4,.12,.01,.12,.5],angle:-.41}];
    const results=[];
    for(const fixture of cases){
      camera.rotation.set(0,0,fixture.angle);camera.updateMatrixWorld();
      const base=new T.PlaneGeometry(2,2),geometry=new T.InstancedBufferGeometry();
      geometry.index=base.index;geometry.attributes.position=base.attributes.position;
      geometry.setAttribute('center',new T.InstancedBufferAttribute(new Float32Array([0,0,0]),3));
      const c=fixture.c;
      geometry.setAttribute('diagonal',new T.InstancedBufferAttribute(new Float32Array([c[0],c[4],c[8]]),3));
      geometry.setAttribute('offDiagonal',new T.InstancedBufferAttribute(new Float32Array([c[1],c[2],c[5]]),3));
      geometry.setAttribute('amplitude',new T.InstancedBufferAttribute(new Float32Array([.8]),1));
      geometry.setAttribute('tint',new T.InstancedBufferAttribute(new Float32Array([.3,.4,.5]),3));
      geometry.instanceCount=1;
      const material=new T.ShaderMaterial({vertexShader:splatVertex,fragmentShader:splatFragment,transparent:true,depthWrite:false,side:T.DoubleSide});
      const scene=new T.Scene(),mesh=new T.Mesh(geometry,material);mesh.frustumCulled=false;scene.add(mesh);
      renderer.setRenderTarget(target);renderer.clear();renderer.render(scene,camera);
      const pixels=new Uint8Array(n*n*4);renderer.readRenderTargetPixels(target,0,0,n,n,pixels);
      const e=camera.matrixWorld.elements,right=[e[0],e[1],e[2]],up=[e[4],e[5],e[6]];
      const quadratic=(a,b)=>a.reduce((sum,v,i)=>sum+v*b.reduce((s,w,j)=>s+c[i*3+j]*w,0),0);
      const a=quadratic(right,right),b=quadratic(right,up),d=quadratic(up,up),det=a*d-b*b;
      let maxError=0,totalError=0,nonzero=0;
      for(let y=0;y<n;y++)for(let x=0;x<n;x++){
        const px=(x+.5)/n*8-4,py=(y+.5)/n*8-4;
        const q=(d*px*px-2*b*px*py+a*py*py)/det;
        const alpha=.78*.8*Math.exp(-.5*q);
        const expected=q>16||alpha<.002?0:Math.round(alpha*255);
        const actual=pixels[(y*n+x)*4+3];
        const error=Math.abs(expected-actual);maxError=Math.max(maxError,error);totalError+=error;if(actual)nonzero++;
      }
      geometry.dispose();material.dispose();
      if(nonzero<10||maxError>2)throw new Error(JSON.stringify({fixture:fixture.name,maxError,nonzero}));
      results.push({name:fixture.name,pixels:n*n,maxAlphaErrorLSB:maxError,meanAlphaErrorLSB:totalError/(n*n),nonzero});
    }
    target.dispose();renderer.dispose();renderer.forceContextLoss();
    return {passed:true,toleranceAlphaLSB:2,cases:results};
  });
  return result;
}
