import { useEffect, useRef, useState } from 'react';

export function Microscope({ file, frame, label, root = '/demo/controlled/budget32/' }: { file: string; frame: number; label: string; root?: string }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    setImage(null); setFailed(false);
    const source = new Image(); let active = true;
    source.onload = () => { if (active) setImage(source); };
    source.onerror = () => { if (active) setFailed(true); };
    source.src = root + file;
    return () => { active = false; };
  }, [file, root]);
  useEffect(() => {
    const context = canvas.current?.getContext('2d');
    if (!context) return;
    context.fillStyle = '#111315'; context.fillRect(0, 0, 512, 512);
    if (image) { context.imageSmoothingEnabled = true; context.drawImage(image, (frame % 16) * 64, Math.floor(frame / 16) * 64, 64, 64, 0, 0, 512, 512); }
  }, [image, frame]);
  return <div className="lab-microscope"><canvas ref={canvas} width={512} height={512} role="img" aria-label={label} data-source-frame={frame}/>{!image ? <span className="lab-image-status" role="status">{failed ? 'Image could not load' : 'Loading image…'}</span> : null}</div>;
}
