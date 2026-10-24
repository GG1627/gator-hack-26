import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { worldPoint, worldCovariance } from './geometry.mjs';
import type { Run, SceneFrame } from './types';

// Project covariance onto the camera plane, then draw genuine anisotropic
// Gaussian footprints. This is an inspection renderer, not the frozen 3D-MIP
// scoring renderer. Camera projection is orthographic and alpha is display-only.
export const splatVertex = `
attribute vec3 center;
attribute vec3 diagonal;
attribute vec3 offDiagonal;
attribute float amplitude;
attribute vec3 tint;
varying vec2 local;
varying float strength;
varying vec3 color;
void main() {
  mat3 C = mat3(diagonal.x,offDiagonal.x,offDiagonal.y,
                offDiagonal.x,diagonal.y,offDiagonal.z,
                offDiagonal.y,offDiagonal.z,diagonal.z);
  vec3 right = vec3(viewMatrix[0][0],viewMatrix[1][0],viewMatrix[2][0]);
  vec3 up = vec3(viewMatrix[0][1],viewMatrix[1][1],viewMatrix[2][1]);
  float a = max(dot(right,C*right),1e-8);
  float b = dot(right,C*up);
  float d = max(dot(up,C*up),1e-8);
  float l00 = sqrt(a);
  float l10 = b/l00;
  float l11 = sqrt(max(d-l10*l10,1e-8));
  local = position.xy * 4.0;
  vec2 offset = vec2(l00*local.x,l10*local.x+l11*local.y);
  vec4 view = viewMatrix * vec4(center,1.0);
  view.xy += offset;
  gl_Position = projectionMatrix * view;
  strength = clamp(amplitude,0.0,1.0);
  color = tint;
}`;
export const splatFragment = `
varying vec2 local;
varying float strength;
varying vec3 color;
void main(){
  float q=dot(local,local);
  if(q>16.0) discard;
  float alpha=0.78*strength*exp(-0.5*q);
  if(alpha<0.002) discard;
  gl_FragColor=vec4(color,alpha);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

function depthColor(depth: number) {
  const a = new THREE.Color('#5b95a8');
  const b = new THREE.Color('#a0c4c7');
  const c = new THREE.Color('#dab49a');
  return depth < .65 ? a.lerp(b, depth / .65) : b.lerp(c, (depth - .65) / .35);
}

function disposeObject(object: THREE.Object3D) {
  object.traverse(child => {
    const renderable = child as THREE.Mesh;
    renderable.geometry?.dispose();
    if (renderable.material) (Array.isArray(renderable.material) ? renderable.material : [renderable.material]).forEach(m => m.dispose());
  });
}

type Runtime = {renderer: THREE.WebGLRenderer; scene: THREE.Scene; camera: THREE.OrthographicCamera; controls: OrbitControls; content: THREE.Group; fit: () => void; draw: () => void; manual: boolean};

export default function Viewer3D({run, frame, points, mode, structure, resetKey, cameraAction, onError}: {
  run: Run; frame: SceneFrame | null; points: ArrayBuffer | null; mode: 'spatial' | 'gaussians'; structure: boolean; resetKey: number; cameraAction: {kind: string; id: number}; onError: (message: string) => void;
}) {
  const host = useRef<HTMLDivElement>(null);
  const runtime = useRef<Runtime | null>(null);
  const origin = [run.shape[2] * run.voxel_size_xyz_um[0] / 2, run.shape[1] * run.voxel_size_xyz_um[1] / 2, run.shape[0] * run.voxel_size_xyz_um[2] / 2];
  useEffect(() => {
    if (!host.current) return;
    const container = host.current;
    let renderer: THREE.WebGLRenderer;
    try { renderer = new THREE.WebGLRenderer({antialias: true, alpha: true, powerPreference: 'high-performance'}); }
    catch { onError('3D rendering is unavailable on this device. The microscope images remain available.'); return; }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    renderer.setClearColor(0xf7f6f1, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.domElement.setAttribute('aria-label', 'Interactive specimen. Drag to rotate; scroll to zoom. Use Reset view to restore the camera.');
    renderer.domElement.setAttribute('role', 'img');
    container.appendChild(renderer.domElement);
    const scene = new THREE.Scene();
    scene.add(new THREE.AmbientLight(0xffffff,2.2));
    const light=new THREE.DirectionalLight(0xffffff,2.5);light.position.set(-40,90,60);scene.add(light);
    const camera = new THREE.OrthographicCamera(-55,55,28,-28,.1,1000);
    camera.position.set(65,50,85);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = false;
    controls.enablePan = true;
    controls.minZoom = .3; controls.maxZoom = 8;
    controls.mouseButtons = {LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN};
    const content = new THREE.Group();
    scene.add(content);
    const box = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(origin[0]*2,origin[2]*2,origin[1]*2)), new THREE.LineBasicMaterial({color:'#bec8c5',transparent:true,opacity:.33}));
    scene.add(box);
    const grid = new THREE.GridHelper(origin[0]*2,8,'#c7cfcb','#d8dcd5');
    grid.position.y = -origin[2];
    const gm = grid.material as THREE.Material; gm.transparent = true; gm.opacity = .32;
    scene.add(grid);
    let drawCount = 0;
    const draw = () => {
      renderer.render(scene,camera);
      container.dataset.draws = String(++drawCount);
      container.dataset.geometries=String(renderer.info.memory.geometries);
      container.dataset.programs=String(renderer.info.programs?.length??0);
    };
    const fit = () => {
      const bounds = new THREE.Box3().setFromObject(content);
      if (bounds.isEmpty()) { draw(); return; }
      const center = bounds.getCenter(new THREE.Vector3());
      // Ellipsoid/point geometry bounds are physical. Project all eight corners
      // into camera orientation to fit without changing physical aspect ratios.
      const direction = camera.position.clone().sub(controls.target).normalize();
      controls.target.copy(center); camera.position.copy(center).addScaledVector(direction,150);
      camera.lookAt(center); camera.updateMatrixWorld();
      const inverse = camera.matrixWorldInverse;
      const projected = new THREE.Box3();
      for (const x of [bounds.min.x,bounds.max.x]) for (const y of [bounds.min.y,bounds.max.y]) for (const z of [bounds.min.z,bounds.max.z]) projected.expandByPoint(new THREE.Vector3(x,y,z).applyMatrix4(inverse));
      const size = projected.getSize(new THREE.Vector3());
      const aspect = Math.max(1,container.clientWidth) / Math.max(1,container.clientHeight);
      const half = Math.max(size.y/2, size.x/(2*aspect), 5)*1.04;
      camera.left=-half*aspect;camera.right=half*aspect;camera.top=half;camera.bottom=-half;
      camera.zoom=1;camera.updateProjectionMatrix();controls.update();draw();
    };
    const rt = {renderer,scene,camera,controls,content,fit,draw,manual:false};
    runtime.current = rt;
    controls.addEventListener('start', () => {rt.manual=true;});
    controls.addEventListener('change', draw);
    const resize = new ResizeObserver(() => {
      renderer.setSize(container.clientWidth,container.clientHeight,false);
      const half = camera.top;
      const aspect = container.clientWidth / Math.max(1,container.clientHeight);
      camera.left=-half*aspect;camera.right=half*aspect;camera.updateProjectionMatrix();if(!rt.manual)fit();else draw();
    });
    resize.observe(container);
    const lost = (event: Event) => {event.preventDefault();onError('The 3D context was interrupted. Switch to Microscope or reload to restore it.');};
    renderer.domElement.addEventListener('webglcontextlost',lost);
    return () => {
      resize.disconnect();controls.dispose();disposeObject(scene);renderer.dispose();
      renderer.domElement.removeEventListener('webglcontextlost',lost);
      renderer.forceContextLoss();renderer.domElement.remove();runtime.current=null;
    };
  }, [run.key]);

  useEffect(() => {
    const rt = runtime.current;
    if (!rt) return;
    while(rt.content.children.length) {const child=rt.content.children[0];rt.content.remove(child);disposeObject(child);}
    if (mode === 'spatial' && points) {
      const raw = new Uint16Array(points);
      const count = raw.length / 4;
      const positions = new Float32Array(count*3);
      const colors = new Float32Array(count*3);
      const strengths = new Float32Array(count);
      for(let i=0;i<count;i++){
        positions.set(worldPoint([raw[i*4]*run.voxel_size_xyz_um[0],raw[i*4+1]*run.voxel_size_xyz_um[1],raw[i*4+2]*run.voxel_size_xyz_um[2]],origin),i*3);
        colors.set(depthColor(raw[i*4+2]/Math.max(1,run.shape[0]-1)).toArray(),i*3);
        strengths[i]=raw[i*4+3]/65535;
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
      geometry.setAttribute('tint',new THREE.BufferAttribute(colors,3));
      geometry.setAttribute('signal',new THREE.BufferAttribute(strengths,1));
      const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,
        uniforms:{pixelRatio:{value:Math.min(window.devicePixelRatio,1.75)}},
        vertexShader:`attribute vec3 tint;attribute float signal;varying vec3 color;varying float strength;uniform float pixelRatio;void main(){color=tint;strength=signal;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);gl_PointSize=(1.1+signal*1.6)*pixelRatio;}`,
        fragmentShader:`varying vec3 color;varying float strength;void main(){float r=length(gl_PointCoord-.5)*2.;if(r>1.)discard;gl_FragColor=vec4(color,(.32+.56*strength)*exp(-2.*r*r));\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}`});
      rt.content.add(new THREE.Points(geometry,material));
      if(host.current)host.current.dataset.points=String(count);
    } else if(mode === 'gaussians' && frame){
      const count=frame.gaussians.length;
      const base=new THREE.PlaneGeometry(2,2);
      const geometry=new THREE.InstancedBufferGeometry();
      geometry.index=base.index;geometry.attributes.position=base.attributes.position;geometry.attributes.uv=base.attributes.uv;
      const centers=new Float32Array(count*3),diagonals=new Float32Array(count*3),off=new Float32Array(count*3),colors=new Float32Array(count*3),amplitudes=new Float32Array(count);
      const bounds=new THREE.Box3();
      frame.gaussians.forEach((g,i)=>{
        const center=worldPoint(g.center,origin),c=worldCovariance(g.covariance);
        centers.set(center,i*3);diagonals.set([c[0],c[4],c[8]],i*3);off.set([c[1],c[2],c[5]],i*3);
        colors.set(depthColor(g.center[2]/(origin[2]*2)).toArray(),i*3);amplitudes[i]=g.amplitude;
        const radius=[Math.sqrt(c[0])*2,Math.sqrt(c[4])*2,Math.sqrt(c[8])*2];
        bounds.expandByPoint(new THREE.Vector3(...center.map((v,j)=>v-radius[j]) as [number,number,number]));
        bounds.expandByPoint(new THREE.Vector3(...center.map((v,j)=>v+radius[j]) as [number,number,number]));
      });
      geometry.setAttribute('center',new THREE.InstancedBufferAttribute(centers,3));
      geometry.setAttribute('diagonal',new THREE.InstancedBufferAttribute(diagonals,3));
      geometry.setAttribute('offDiagonal',new THREE.InstancedBufferAttribute(off,3));
      geometry.setAttribute('amplitude',new THREE.InstancedBufferAttribute(amplitudes,1));
      geometry.setAttribute('tint',new THREE.InstancedBufferAttribute(colors,3));
      geometry.instanceCount=count;geometry.boundingBox=bounds;
      const material=new THREE.ShaderMaterial({vertexShader:splatVertex,fragmentShader:splatFragment,transparent:true,depthWrite:false,side:THREE.DoubleSide});
      const mesh=new THREE.Mesh(geometry,material);mesh.frustumCulled=false;rt.content.add(mesh);
      // Shaded 2-sigma level-set geometry makes physical shape inspectable;
      // these are model contours, never a claimed biological cell surface.
      const surfaces=new THREE.InstancedMesh(new THREE.SphereGeometry(1,24,16),new THREE.MeshPhysicalMaterial({color:'#c0dbe2',roughness:.42,metalness:0,transparent:true,opacity:structure ? .1 : .28,depthWrite:false,clearcoat:.12}),count);
      frame.gaussians.forEach((g,i)=>{
        const b=g.basis,r=g.radii.map(v=>v*2),c=worldPoint(g.center,origin);
        surfaces.setMatrixAt(i,new THREE.Matrix4().set(b[0]*r[0],b[1]*r[1],b[2]*r[2],c[0], b[6]*r[0],b[7]*r[1],b[8]*r[2],c[1], -b[3]*r[0],-b[4]*r[1],-b[5]*r[2],c[2], 0,0,0,1));
        surfaces.setColorAt(i,depthColor(g.center[2]/(origin[2]*2)));
      });
      surfaces.instanceMatrix.needsUpdate=true;if(surfaces.instanceColor)surfaces.instanceColor.needsUpdate=true;
      // Exact world-axis 2-sigma bounds avoid fitting the camera to transformed
      // unit-cube corners, which overestimate rotated ellipsoid extents.
      surfaces.boundingBox=bounds.clone();
      rt.content.add(surfaces);
      const selected=frame.gaussians.filter((_,i)=>structure||i%8===0);
      const outlines=new THREE.InstancedMesh(new THREE.SphereGeometry(1,20,12),new THREE.MeshBasicMaterial({color:'#438296',wireframe:true,transparent:true,opacity:structure ? .25 : .12,depthWrite:false}),selected.length);
      selected.forEach((g,i)=>{
        const b=g.basis,r=g.radii.map(v=>v*2),c=worldPoint(g.center,origin);
        const matrix=new THREE.Matrix4().set(b[0]*r[0],b[1]*r[1],b[2]*r[2],c[0], b[6]*r[0],b[7]*r[1],b[8]*r[2],c[1], -b[3]*r[0],-b[4]*r[1],-b[5]*r[2],c[2], 0,0,0,1);
        outlines.setMatrixAt(i,matrix);
      });
      outlines.instanceMatrix.needsUpdate=true;outlines.boundingBox=bounds.clone();rt.content.add(outlines);
      if(host.current)host.current.dataset.components=String(count);
    }
    if(!rt.manual)rt.fit(); else rt.draw();
  },[frame,points,mode,structure,run.key]);

  useEffect(()=>{const rt=runtime.current;if(rt){rt.manual=false;rt.fit();}},[resetKey]);
  useEffect(()=>{
    const rt=runtime.current;if(!rt||!cameraAction.id)return;
    rt.manual=true;
    const offset=rt.camera.position.clone().sub(rt.controls.target);
    if(cameraAction.kind==='left'||cameraAction.kind==='right'){
      offset.applyAxisAngle(new THREE.Vector3(0,1,0),cameraAction.kind==='left' ? .15 : -.15);
      rt.camera.position.copy(rt.controls.target).add(offset);
    }else{rt.camera.zoom=THREE.MathUtils.clamp(rt.camera.zoom*(cameraAction.kind==='in'?1.15:1/1.15),.3,8);rt.camera.updateProjectionMatrix();}
    rt.controls.update();rt.draw();
  },[cameraAction]);
  return <div className="webgl-stage" ref={host} data-mode={mode}/>;
}
