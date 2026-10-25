export const slides = [
  { id: 'opening', title: 'See more. Illuminate less.', footer: 'See more. Illuminate less.' },
  { id: 'problem', title: 'The cost of looking', footer: 'The cost of looking' },
  { id: 'solution', title: 'Meet Peekaboo', footer: 'A better moment to look.' },
  { id: 'approach', title: 'How Peekaboo decides', footer: 'Observe. Estimate. Decide.' },
  { id: 'model', title: 'Gaussian cell models', footer: 'A compact representation' },
  { id: 'compute', title: 'Native CUDA Rust', footer: 'Fresh off the frontier' },
  { id: 'demo', title: 'The comparison', footer: 'The comparison' },
];
export const slideIds = slides.map(slide => slide.id);
export const demoSlideIndex = slideIds.indexOf('demo');
export function slideIndex(hash) {
  const index = slideIds.indexOf(hash.replace(/^#/, ''));
  return index < 0 ? 0 : index;
}
