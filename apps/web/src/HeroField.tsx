import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const sheetVertex=`varying vec2 vUv; void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`;
const sheetFragment=`
  varying vec2 vUv; uniform float uOpacity;
  void main(){
    vec2 p=abs(vUv-.5)*2.0;
    float edge=pow(max(p.x,p.y),18.0);
    float fade=(1.0-smoothstep(.96,1.0,p.x))*(1.0-smoothstep(.96,1.0,p.y));
    gl_FragColor=vec4(vec3(1.0,.42,.18),(.035+edge*.55)*fade*uOpacity);
  }`;
const shadowFragment=`varying vec2 vUv; void main(){vec2 p=(vUv-.5)*2.0;gl_FragColor=vec4(0.0,0.0,0.0,exp(-dot(p,p)*4.0)*.38);}`;

export default function HeroField({phase,playing,reduced}:{phase:number;playing:boolean;reduced:boolean}){
  const host=useRef<HTMLDivElement>(null);
  const control=useRef({phase,playing,reduced});
  const redraw=useRef<(()=>void)|null>(null);
  const [failed,setFailed]=useState(false);
  useEffect(()=>{control.current={phase,playing,reduced};redraw.current?.();},[phase,playing,reduced]);
  useEffect(()=>{
    const element=host.current;if(!element)return;
    let renderer:THREE.WebGLRenderer;
    try{renderer=new THREE.WebGLRenderer({alpha:false,antialias:true,powerPreference:'low-power'});}catch{setFailed(true);return;}
    renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.5));
    renderer.setClearColor('#111b1c',1);
    renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.78;
    element.appendChild(renderer.domElement);renderer.domElement.setAttribute('aria-hidden','true');
    const scene=new THREE.Scene();scene.background=new THREE.Color('#111b1c');
    const camera=new THREE.PerspectiveCamera(35,1,.1,40);camera.position.set(0,.2,8.8);camera.lookAt(0,0,0);
    const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();
    const environment=pmrem.fromScene(room,.04);scene.environment=environment.texture;scene.environmentIntensity=.65;
    room.dispose();pmrem.dispose();
    scene.add(new THREE.HemisphereLight('#d5f4e6','#263f40',.75));
    const key=new THREE.DirectionalLight('#fff1d5',2);key.position.set(-3,5,5);scene.add(key);
    const rim=new THREE.DirectionalLight('#7dd7df',2.5);rim.position.set(4,1,-3);scene.add(rim);
    const warm=new THREE.PointLight('#ff7540',5,12,2);warm.position.set(-3,0,2);scene.add(warm);
    const specimen=new THREE.Group();specimen.position.y=.08;scene.add(specimen);
    const nucleusGeometry=new THREE.IcosahedronGeometry(1,4);
    const positions=nucleusGeometry.attributes.position;
    for(let i=0;i<positions.count;i++){
      const x=positions.getX(i),y=positions.getY(i),z=positions.getZ(i);
      const bump=1+.035*Math.sin(x*13+y*7)*Math.cos(z*11-x*3)+.025*Math.sin(y*19+z*5);
      positions.setXYZ(i,x*bump,y*bump,z*bump);
    }
    nucleusGeometry.computeVertexNormals();
    const wireGeometry=new THREE.WireframeGeometry(new THREE.IcosahedronGeometry(1,2));
    const wireMaterial=new THREE.LineBasicMaterial({color:'#efb480',transparent:true,opacity:.1,depthWrite:false});
    const nuclei:{mesh:THREE.Mesh;wire:THREE.LineSegments;material:THREE.MeshPhysicalMaterial;position:THREE.Vector3;seed:number;scale:THREE.Vector3}[]=[];
    const count=26;
    for(let i=0;i<count;i++){
      const seed=((i*37)%97)/97,angle=i*2.3999632297;
      const radius=Math.cbrt((i+.8)/count),vertical=2*((i*.754877666+.21)%1)-1;
      const radial=Math.sqrt(1-vertical*vertical);
      const center=new THREE.Vector3(Math.cos(angle)*radial*radius*2.03,vertical*radius*1.2,Math.sin(angle)*radial*radius*1.18);
      const material=new THREE.MeshPhysicalMaterial({color:new THREE.Color().setHSL(.43+seed*.06,.36,.25+seed*.13),
        metalness:.12,roughness:.3,clearcoat:1,clearcoatRoughness:.16,envMapIntensity:.85,
        emissive:'#133a35',emissiveIntensity:.35});
      const mesh=new THREE.Mesh(nucleusGeometry,material);
      mesh.position.copy(center);mesh.scale.setScalar(.28+seed*.13);mesh.scale.y*=1.12;mesh.rotation.set(seed*2,seed*3,seed);
      specimen.add(mesh);
      const wire=new THREE.LineSegments(wireGeometry,wireMaterial);wire.position.copy(center);wire.scale.copy(mesh.scale).multiplyScalar(1.025);wire.rotation.copy(mesh.rotation);wire.renderOrder=10;specimen.add(wire);
      nuclei.push({mesh,wire,material,position:center,seed,scale:mesh.scale.clone()});
    }
    const granuleGeometry=new THREE.IcosahedronGeometry(1,1);
    const granuleMaterial=new THREE.MeshStandardMaterial({color:'#b5d7bd',metalness:.35,roughness:.3,emissive:'#6b6240',emissiveIntensity:.2});
    const granules=new THREE.InstancedMesh(granuleGeometry,granuleMaterial,count*18);
    const transform=new THREE.Object3D();
    nuclei.forEach((nucleus,index)=>{
      for(let j=0;j<18;j++){
        const angle=j*2.3999632297,z=1-2*(j+.5)/18,r=Math.sqrt(1-z*z);
        const normal=new THREE.Vector3(Math.cos(angle)*r,z*1.12,Math.sin(angle)*r);
        normal.applyEuler(nucleus.mesh.rotation).multiplyScalar(nucleus.mesh.scale.x*.98);
        transform.position.copy(nucleus.position).add(normal);transform.scale.setScalar(.018+(j%3)*.006);transform.updateMatrix();
        granules.setMatrixAt(index*18+j,transform.matrix);
      }
    });specimen.add(granules);
    const membraneGeometry=new THREE.SphereGeometry(1,64,40);
    const membraneMaterial=new THREE.MeshPhysicalMaterial({color:'#d9ece4',metalness:0,roughness:.025,
      transmission:.995,thickness:.08,ior:1.08,clearcoat:.45,clearcoatRoughness:.04,envMapIntensity:.28,
      attenuationColor:'#a8d9cb',attenuationDistance:4,transparent:true,depthWrite:false});
    const membrane=new THREE.Mesh(membraneGeometry,membraneMaterial);membrane.scale.set(2.55,1.63,1.63);specimen.add(membrane);
    const contourGeometry=new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(1,2));
    const contourMaterial=new THREE.LineBasicMaterial({color:'#8fcec0',transparent:true,opacity:.08});
    const contour=new THREE.LineSegments(contourGeometry,contourMaterial);contour.scale.copy(membrane.scale).multiplyScalar(1.01);specimen.add(contour);
    const sheetGeometry=new THREE.PlaneGeometry(3.4,3.6);
    const sheetMaterial=new THREE.ShaderMaterial({vertexShader:sheetVertex,fragmentShader:sheetFragment,transparent:true,
      depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,uniforms:{uOpacity:{value:1}}});
    const sheet=new THREE.Mesh(sheetGeometry,sheetMaterial);sheet.rotation.y=Math.PI/2;sheet.renderOrder=8;specimen.add(sheet);
    const sheetEdgeGeometry=new THREE.EdgesGeometry(sheetGeometry);
    const sheetEdgeMaterial=new THREE.LineBasicMaterial({color:'#ff9460',transparent:true,opacity:.75});
    const sheetEdge=new THREE.LineSegments(sheetEdgeGeometry,sheetEdgeMaterial);sheet.add(sheetEdge);
    const shadowGeometry=new THREE.PlaneGeometry(7,4);
    const shadowMaterial=new THREE.ShaderMaterial({vertexShader:sheetVertex,fragmentShader:shadowFragment,transparent:true,depthWrite:false});
    const shadow=new THREE.Mesh(shadowGeometry,shadowMaterial);shadow.rotation.x=-Math.PI/2;shadow.position.y=-2.25;scene.add(shadow);
    const dustGeometry=new THREE.BufferGeometry();
    const dustPositions=Array.from({length:140},(_,i)=>{
      const angle=i*2.3999632297,r=2.7+(i%11)*.11;
      return [Math.cos(angle)*r,Math.sin(angle)*r*.65,Math.sin(i*3.17)*2.5];
    }).flat();dustGeometry.setAttribute('position',new THREE.Float32BufferAttribute(dustPositions,3));
    const dustMaterial=new THREE.PointsMaterial({color:'#bddbd0',size:.018,transparent:true,opacity:.35,depthWrite:false});
    const dust=new THREE.Points(dustGeometry,dustMaterial);scene.add(dust);
    const composer=new EffectComposer(renderer);
    const renderPass=new RenderPass(scene,camera);
    const bloom=new UnrealBloomPass(new THREE.Vector2(600,450),.2,.35,1.25);
    const output=new OutputPass();composer.addPass(renderPass);composer.addPass(bloom);composer.addPass(output);
    let frame=0,disposed=false,contextLost=false,visible=true,time=0,last=performance.now(),renders=0,dragging=false;
    const pointer=new THREE.Vector2(),rotation=new THREE.Vector2(),dragStart=new THREE.Vector2();
    let modelMix=phase===1?1:0;
    let activePhase=phase,phaseTime=playing&&!reduced?0:2,illumination=phase===1?0:1;
    function draw(now:number){
      frame=0;if(disposed||contextLost||!visible||document.visibilityState==='hidden')return;
      const current=control.current,animate=current.playing&&!current.reduced;
      const delta=Math.min((now-last)/1000,.05);last=now;if(animate)time+=delta;
      if(current.phase!==activePhase){activePhase=current.phase;phaseTime=animate?0:2;}
      if(animate)phaseTime+=delta;
      modelMix=current.reduced||!animate?(current.phase===1?1:0):THREE.MathUtils.damp(modelMix,current.phase===1?1:0,3,delta);
      const model=modelMix;
      const exposure=current.phase===0?1:current.phase===1?0:Math.exp(-Math.pow((phaseTime-2)/.42,2));
      illumination=animate?THREE.MathUtils.damp(illumination,exposure,7,delta):exposure;
      const scan=current.phase===0?THREE.MathUtils.lerp(-2.6,2.6,Math.min(phaseTime/4,1)):.55;
      specimen.rotation.set(.24+(current.reduced?0:Math.sin(time*.19)*.12)+rotation.y,-.38+(current.reduced?0:time*.12)+rotation.x,-.34);
      if(!current.reduced){specimen.rotation.y+=pointer.x*.2;specimen.rotation.x+=pointer.y*.1;}
      specimen.position.y=.08+(current.reduced?0:Math.sin(time*.55)*.08);
      membraneMaterial.transmission=.995-model*.06;membraneMaterial.roughness=.025+model*.045;
      membraneMaterial.opacity=1-model*.8;membrane.scale.set(2.55,1.63,1.63).multiplyScalar(1+model*.1);
      contourMaterial.opacity=.05+model*.2;wireMaterial.opacity=.035+model*.65;
      sheet.position.x=scan;sheet.visible=illumination>.015;sheetMaterial.uniforms.uOpacity.value=illumination;sheetEdgeMaterial.opacity=.65*illumination;
      nuclei.forEach(({mesh,wire,material,position,seed,scale})=>{
        const light=Math.exp(-Math.pow((position.x-scan)*2.8,2))*illumination;
        const pulse=current.phase===2&&seed>.88?illumination*.8:0;
        material.emissive.setRGB(.04+light*.8+pulse*.6,.12+light*.16,.1);
        material.emissiveIntensity=.45+light*.8;
        material.roughness=.24+model*.35;material.metalness=.12+model*.2;
        const breathe=1+(current.reduced?0:Math.sin(time*.6+seed*12)*.025);
        mesh.position.copy(position).multiplyScalar(breathe*(1+model*.25));wire.position.copy(mesh.position);
        mesh.scale.copy(scale).multiplyScalar(1-model*.82);
      });
      granules.visible=model<.4;
      warm.position.x=scan;warm.intensity=5*illumination;dust.rotation.y=current.reduced?0:time*.025;
      composer.render(delta);renderer.domElement.dataset.frames=String(++renders);
      if(animate)frame=requestAnimationFrame(draw);
    }
    const invalidate=()=>{if(!frame&&!disposed){last=performance.now();frame=requestAnimationFrame(draw);}};redraw.current=invalidate;
    const resize=new ResizeObserver(()=>{
      const {width,height}=element.getBoundingClientRect();if(!width||!height)return;
      camera.aspect=width/height;camera.position.z=camera.aspect<1.05?10.5:8.8;camera.updateProjectionMatrix();
      renderer.setSize(width,height);composer.setSize(width,height);invalidate();
    });resize.observe(element);
    const intersection=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)invalidate();else{cancelAnimationFrame(frame);frame=0;}});intersection.observe(element);
    const move=(event:PointerEvent)=>{
      if(control.current.reduced&&!dragging)return;
      const rect=element.getBoundingClientRect();
      pointer.set((event.clientX-rect.left)/rect.width-.5,(event.clientY-rect.top)/rect.height-.5);
      if(dragging){rotation.x+=(event.clientX-dragStart.x)*.007;rotation.y+=(event.clientY-dragStart.y)*.005;dragStart.set(event.clientX,event.clientY);}
      invalidate();
    };
    const down=(event:PointerEvent)=>{dragging=true;dragStart.set(event.clientX,event.clientY);element.setPointerCapture(event.pointerId);};
    const up=()=>{dragging=false;};const leave=()=>{if(!dragging)pointer.set(0,0);invalidate();};
    const keyboard=(event:KeyboardEvent)=>{
      if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home'].includes(event.key))return;
      event.preventDefault();
      if(event.key==='Home')rotation.set(0,0);else if(event.key==='ArrowLeft')rotation.x-=.18;else if(event.key==='ArrowRight')rotation.x+=.18;else if(event.key==='ArrowUp')rotation.y-=.12;else rotation.y+=.12;
      invalidate();
    };
    const visibility=()=>{if(document.visibilityState==='visible')invalidate();else{cancelAnimationFrame(frame);frame=0;}};
    const lost=(event:Event)=>{event.preventDefault();contextLost=true;cancelAnimationFrame(frame);frame=0;setFailed(true);};
    element.addEventListener('pointermove',move,{passive:true});element.addEventListener('pointerdown',down);element.addEventListener('pointerup',up);element.addEventListener('pointercancel',up);element.addEventListener('pointerleave',leave);element.addEventListener('keydown',keyboard);
    document.addEventListener('visibilitychange',visibility);renderer.domElement.addEventListener('webglcontextlost',lost);invalidate();
    return()=>{
      disposed=true;redraw.current=null;cancelAnimationFrame(frame);resize.disconnect();intersection.disconnect();
      element.removeEventListener('pointermove',move);element.removeEventListener('pointerdown',down);element.removeEventListener('pointerup',up);element.removeEventListener('pointercancel',up);element.removeEventListener('pointerleave',leave);element.removeEventListener('keydown',keyboard);
      document.removeEventListener('visibilitychange',visibility);renderer.domElement.removeEventListener('webglcontextlost',lost);
      [nucleusGeometry,wireGeometry,granuleGeometry,membraneGeometry,contourGeometry,sheetGeometry,sheetEdgeGeometry,shadowGeometry,dustGeometry].forEach(g=>g.dispose());
      nuclei.forEach(n=>n.material.dispose());[wireMaterial,granuleMaterial,membraneMaterial,contourMaterial,sheetMaterial,sheetEdgeMaterial,shadowMaterial,dustMaterial].forEach(m=>m.dispose());
      bloom.dispose();output.dispose();renderPass.dispose();composer.dispose();environment.dispose();renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();
    };
  },[]);
  return <div className="hero-field" ref={host} data-fallback={failed||undefined} tabIndex={0} role="img" aria-label="Conceptual three-dimensional specimen. Drag or use arrow keys to rotate; Home resets the view.">{failed?<div className="hero-field-fallback" aria-hidden="true"><div/><div/><div/><div/><div/><div/><div/></div>:null}</div>;
}
