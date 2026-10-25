export const slideIds = ['opening', 'problem', 'approach', 'model', 'compute', 'demo'];
export function slideIndex(hash) {
  const index = slideIds.indexOf(hash.replace(/^#/, ''));
  return index < 0 ? 0 : index;
}
