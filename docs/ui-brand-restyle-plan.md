# UI Brand Restyle Plan (Made Easy IT inspired)

## Scope
- Restyle `app/templates/index.html` to match Made Easy IT visual direction.
- Keep all existing functionality and form behavior unchanged.
- Do not add custom header/footer in this iteration.

## Non-Goals
- No backend/API route changes.
- No form field name changes.
- No job flow or service logic changes.
- No new pages.

## Design Direction
- Visual tone: clean, high-contrast, modern service-business style.
- Palette direction:
  - dark/navy hero foundation,
  - cyan/teal accent highlights,
  - warm neutral section backgrounds,
  - strong black headline text.
- Typography:
  - Condensed display font for headings (Google Fonts),
  - clean sans-serif for body and controls.
- Motion:
  - subtle transitions only (hover/focus/entry),
  - avoid excessive animation.

## Template Refactor Plan (`app/templates/index.html`)
1. Introduce design tokens (CSS variables) for color, spacing, radius, shadow, transition.
2. Build hero-style top section (without site header/footer):
   - dark background treatment,
   - strong uppercase title,
   - accent-highlight subheading,
   - short supporting copy.
3. Rework main form area into branded card sections:
   - retain same form structure and field names,
   - stronger grouping for single-speaker and multi-speaker modes,
   - improved label hierarchy and helper text clarity.
4. Keep existing mode toggle JS behavior:
   - preserve `toggleMode()` logic and IDs,
   - style-only improvements around shown/hidden blocks.
5. Improve controls and CTA:
   - accessible focus ring,
   - stronger button hierarchy and hover state,
   - clearer error message visual treatment.
6. Add section-shape feel (CSS-only separators) to echo current brand language.
7. Mobile-first polish:
   - typography scaling,
   - stacked layouts under narrow breakpoints,
   - ensure no horizontal overflow and touch-friendly controls.

## Technical Constraints
- Preserve:
  - `form method="post" action="/generate"`,
  - all existing input `name` attributes,
  - current error rendering (`{% if error %}` block),
  - existing template variable usage (`voices`, `error`).
- Do not edit `app/main.py` for this UI-only iteration.

## Validation Plan
1. Syntax sanity:
   - `python -m py_compile app/main.py`
2. Targeted API regression checks:
   - `pytest -q tests/test_api.py::test_single_tts_endpoint`
   - `pytest -q tests/test_api.py::test_dialogue_tts_endpoint`
3. Manual checks:
   - `/` renders correctly (desktop + mobile),
   - single mode form submits and downloads MP3,
   - multi mode form submits and downloads merged MP3,
   - error state remains clear and readable.

## Acceptance Criteria
- Page visually aligns with Made Easy IT brand direction.
- No regression in form submission behavior.
- No backend/API changes required.
- Responsive behavior remains clean on mobile and desktop.
- No custom header/footer included yet.
