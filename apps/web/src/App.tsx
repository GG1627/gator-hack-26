import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { ControlledLab } from './ControlledLab';
import { StorySlide } from './StorySlides';
import { Arrow, Button } from './PeekabooUI';
import { slideIds, slideIndex } from './presentation.mjs';

const ResearchArchive = lazy(() => import('./ResearchArchive'));

export default function App() {
  const [slide, setSlide] = useState(() => slideIndex(window.location.hash));
  const [archiveOpen, setArchiveOpen] = useState(false);
  const [demoVisited, setDemoVisited] = useState(() => slide === 5);
  const dialog = useRef<HTMLDialogElement>(null);
  const focusPending = useRef(false);
  const researchButton = useRef<HTMLButtonElement>(null);
  const navigate = (index: number) => {
    const next = Math.max(0, Math.min(slideIds.length - 1, index));
    if (next === slide) return;
    focusPending.current = true;
    window.location.hash = slideIds[next];
  };
  useEffect(() => {
    const changed = () => {
      focusPending.current = true;
      const next = slideIndex(window.location.hash);
      setSlide(next);
      if (next === 5) setDemoVisited(true);
    };
    window.addEventListener('hashchange', changed);
    return () => window.removeEventListener('hashchange', changed);
  }, []);
  useEffect(() => {
    if (focusPending.current) {
      document.querySelector<HTMLElement>('[data-active-slide] h1')?.focus({ preventScroll: true });
      window.scrollTo({ top: 0, behavior: 'instant' });
      focusPending.current = false;
    }
    document.title = `Peekaboo — ${['See more. Illuminate less.', 'The cost of looking', 'Choose when to look', 'Gaussian cell models', 'Native CUDA Rust', 'The comparison'][slide]}`;
  }, [slide]);
  useEffect(() => {
    const keyboard = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (archiveOpen || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || target.closest('input, select, textarea, button, a, summary, [contenteditable="true"], [role="slider"]')) return;
      if (event.key === 'ArrowRight') { event.preventDefault(); navigate(slide + 1); }
      if (event.key === 'ArrowLeft') { event.preventDefault(); navigate(slide - 1); }
    };
    window.addEventListener('keydown', keyboard);
    return () => window.removeEventListener('keydown', keyboard);
  });
  useEffect(() => {
    if (archiveOpen) dialog.current?.showModal();
    else if (dialog.current?.open) dialog.current.close();
  }, [archiveOpen]);
  const closeArchive = () => { setArchiveOpen(false); researchButton.current?.focus(); };

  return <>
    <a className="skip-link" href="#presentation-content" onClick={event => { event.preventDefault(); document.getElementById('presentation-content')?.focus(); }}>Skip to presentation</a>
    <main className={`peekaboo ${slide === 0 ? 'opening' : ''}`}>
      <header className="peek-header">
        <a className="peek-brand" href="#opening" aria-label="Peekaboo home">Peekaboo<span className="brand-dot" aria-hidden="true"/></a>
        <nav aria-label="Main navigation"><button onClick={() => navigate(0)} aria-current={slide < 5 ? 'page' : undefined}>Story</button><button onClick={() => navigate(5)} aria-current={slide === 5 ? 'page' : undefined}>Demo</button></nav>
        {slide !== 0 ? <button ref={researchButton} className="research-trigger" onClick={() => setArchiveOpen(true)}>Research archive<Arrow/></button> : null}
      </header>
      <div id="presentation-content" tabIndex={-1}>
        {slide < 5 ? <section key={slide} className={`story-slide story-${slide}`} data-active-slide="true" aria-label={`Slide ${slide + 1} of 6`}><StorySlide active={!archiveOpen} index={slide} onStart={() => navigate(1)}/></section> : null}
        {demoVisited ? <div hidden={slide !== 5} data-active-slide={slide === 5 ? 'true' : undefined}><ControlledLab active={slide === 5 && !archiveOpen}/></div> : null}
      </div>
      <footer className="presentation-footer">
        <span className="footer-note">{slide === 0 ? 'See more. Illuminate less.' : ['','The cost of looking','Adaptive acquisition','A compact representation','Fresh off the frontier','The comparison'][slide]}</span>
        <nav className="slide-nav" aria-label="Slide navigation">
          <button aria-label="Previous slide" disabled={slide === 0} onClick={() => navigate(slide - 1)}><Arrow back/></button>
          <div className="slide-dots">{slideIds.map((id: string, index: number) => <button key={id} aria-label={`Go to slide ${index + 1}`} aria-current={index === slide ? 'step' : undefined} onClick={() => navigate(index)}><i/></button>)}</div>
          <span className="slide-count">{String(slide + 1).padStart(2, '0')} <span>/ 06</span></span>
          <button aria-label="Next slide" disabled={slide === 5} onClick={() => navigate(slide + 1)}><Arrow/></button>
        </nav>
        <span className="footer-event">GatorHack V · 2026</span>
      </footer>
    </main>
    <dialog ref={dialog} className="research-dialog" onCancel={closeArchive} onClose={() => { if (archiveOpen) closeArchive(); }} aria-labelledby="archive-title">
      <div className="dialog-bar"><span id="archive-title">Peekaboo / Research archive</span><Button variant="quiet" onClick={closeArchive}>Close archive <span aria-hidden="true">×</span></Button></div>
      {archiveOpen ? <Suspense fallback={<p role="status">Opening the research archive…</p>}><ResearchArchive/></Suspense> : null}
    </dialog>
  </>;
}
