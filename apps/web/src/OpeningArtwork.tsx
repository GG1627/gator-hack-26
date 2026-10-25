import { useState } from 'react';
import { createPortal } from 'react-dom';
import SideRays from './SideRays';

export function OpeningArtwork({ active }: { active: boolean }) {
  const [motion, setMotion] = useState(true);
  return <>
    {createPortal(<div className="opening-rays" aria-hidden="true"><SideRays rayColor1="#FFC46B" rayColor2="#96c8ff" origin="top-right" speed={2.5} intensity={2} spread={2} density={5} followMouse blend={0.6} sharpness={0.5} tilt={0} falloff={1.6} glow={1} saturation={1} dust={0} mouseInfluence={0.5} intro lightMode={false} opacity={1} maxDevicePixelRatio={1.5} paused={!motion || !active}/></div>, document.body)}
    <div className="opening-artwork">
    <img className="capybara-scientist" src="/peekaboo/after-hours-capybara.png" width="1448" height="1086" alt="Illustrated capybara scientist in a lab coat, looking into a blue microscope" fetchPriority="high"/>
    <button className="motion-toggle" aria-pressed={motion} onClick={() => setMotion(value => !value)}>{motion ? 'Pause' : 'Enable'} ambient motion<span aria-hidden="true">{motion ? 'Ⅱ' : '▷'}</span></button>
    </div>
  </>;
}
