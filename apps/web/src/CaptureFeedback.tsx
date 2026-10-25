import { useEffect, useRef } from 'react';

/** Animate a new acquisition only while the replay clock is advancing. */
export function CaptureFeedback({ source, running }: { source: number; running: boolean }) {
  const previous = useRef(source);
  const border = useRef<HTMLSpanElement>(null);
  const scan = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    const changed = previous.current !== source;
    previous.current = source;
    if (!changed || !running || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const flash = border.current?.animate([{ opacity: 0.9 }, { opacity: 0 }], { duration: 520, easing: 'ease-out' });
    const sweep = scan.current?.animate([{ transform: 'translateY(-100%)', opacity: 0.8 }, { transform: 'translateY(100%)', opacity: 0 }], { duration: 450, easing: 'ease-out' });
    return () => { flash?.cancel(); sweep?.cancel(); };
  }, [source, running]);
  return <span className="capture-feedback" aria-hidden="true"><span ref={border} className="capture-flash"/><span ref={scan} className="capture-scan"/></span>;
}
