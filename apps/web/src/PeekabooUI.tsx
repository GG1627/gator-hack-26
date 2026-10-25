import type { ButtonHTMLAttributes, ReactNode, Ref } from 'react';
import { Icon } from './Icon';

export function Button({ children, variant = 'primary', className = '', ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'quiet'; children: ReactNode }) {
  return <button className={`peek-button ${variant} ${className}`} {...props}>{children}</button>;
}

export function Arrow({ back = false }: { back?: boolean }) {
  return <span className={back ? 'direction back' : 'direction'}><Icon name="arrow" size={21}/></span>;
}

export function SourceDisclosure({ children, label = 'Research & references', detailsRef }: { children: ReactNode; label?: string; detailsRef?: Ref<HTMLDetailsElement> }) {
  return <details ref={detailsRef} className="source-disclosure"><summary>{label}<span aria-hidden="true">+</span></summary><div className="source-body">{children}</div></details>;
}

export function SourceLink({ href, children }: { href: string; children: ReactNode }) {
  return <a href={href} target="_blank" rel="noreferrer">{children}<Icon name="arrow" size={15}/></a>;
}

export function CaptureStatus({ capture, source, count }: { capture: boolean; source: number; count: number }) {
  return <div className={`capture-status ${capture ? 'captured' : 'holding'}`}>
    <span className="capture-indicator" aria-hidden="true"/><span>{capture ? 'Captured' : 'Holding'}<small>Frame {String(source).padStart(3, '0')} · {capture ? 'one exposure' : 'no new exposure'}</small></span>
    <span className="capture-number">{String(count).padStart(2, '0')}<small>images</small></span>
  </div>;
}
