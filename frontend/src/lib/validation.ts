// Mirrors backend/app/models/document.py's DESCRIPTION_MAX_WORDS and word-count
// check -- keep these in sync if the backend limit changes.
export const DESCRIPTION_MAX_WORDS = 500

export function countWords(value: string): number {
  const trimmed = value.trim()
  return trimmed === "" ? 0 : trimmed.split(/\s+/).length
}
