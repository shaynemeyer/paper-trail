---
name: favicon
description: Regenerates frontend/public/favicon.ico from Paper Trail's own sidebar brand mark (the ScrollText icon in the bg-sidebar-primary badge in app-sidebar.tsx, colored from --sidebar-primary/--sidebar-primary-foreground in index.css) instead of a generic image-to-icon conversion. Use this whenever the user wants to regenerate, refresh, or update the favicon/app icon after changing the sidebar logo icon or the brand/primary color, or asks to "make the favicon match the logo again" or "the favicon looks out of date."
---

# Favicon from Sidebar Brand Mark

Paper Trail's favicon isn't a fixed image — it's derived from the same brand mark rendered live
in the sidebar (`frontend/src/components/layout/app-sidebar.tsx`): a rounded-square badge colored
with the `--sidebar-primary` CSS variable, containing a lucide-react icon (currently `ScrollText`)
stroked in `--sidebar-primary-foreground`. The point of this skill is to keep `favicon.ico` in
sync with that mark by re-deriving it from source every time, rather than hand-picking a hex color
and re-drawing the icon paths from memory (which is what produces subtle drift between the sidebar
and the favicon after a rebrand).

## When to run it

Run `scripts/generate_favicon.py` whenever:
- The icon component inside the `bg-sidebar-primary` badge in `app-sidebar.tsx` changes (a
  different lucide-react icon).
- `--sidebar-primary` or `--sidebar-primary-foreground` in `frontend/src/index.css` changes.
- The user just asks for the favicon to be regenerated/refreshed/kept in sync with branding.

You don't need to know today's specific icon or color to use this — the script reads both from
those two source files each run, so it stays correct after a rebrand without any edits to this
skill.

## Running it

```bash
python3 .claude/skills/favicon/scripts/generate_favicon.py
```

It prints the icon name and resolved colors it found, then writes
`frontend/public/favicon.ico` (16/32/48/64/128/256 px, packed into one multi-resolution `.ico`).

Requirements it checks for itself and fails loudly on if missing:
- `rsvg-convert` on `PATH` (macOS: `brew install librsvg`) for SVG → PNG rasterization.
- A Python interpreter with Pillow installed, for packing the PNGs into the `.ico` container. The
  script probes a few candidates (`python3`, its own interpreter, any `~/.pyenv/versions/*/bin/python3`)
  because the bare `python3` on `PATH` in this repo resolves to `backend/.venv`, which doesn't have
  Pillow — don't assume `python3` has it.

After running, verify the frontend still builds cleanly with the new asset:

```bash
cd frontend && bun run build
```

## How it derives the icon (for reference / debugging)

1. **Icon shape**: regex-finds the `className="..."` containing `bg-sidebar-primary` in
   `app-sidebar.tsx`, then the first PascalCase JSX tag right after it (e.g. `<ScrollText
   className="size-4" />` → `ScrollText`). Converts to kebab-case and reads the icon's raw SVG path
   data straight from the installed package at
   `frontend/node_modules/lucide-react/dist/esm/icons/<kebab-name>.mjs` (the `__iconNode` array) —
   not from a vendored copy, so a lucide-react version bump or icon swap is picked up for free.
2. **Colors**: regex-finds `--sidebar-primary` and `--sidebar-primary-foreground` inside the first
   `:root { }` block (light mode) of `index.css`, each as `oklch(L C H)`, and converts OKLCH → sRGB
   hex using the standard OKLab cone-response matrix (constants `0.3963377774`/`0.2158037573`/etc.)
   → LMS-to-linear-RGB matrix (`4.0767416621`/`-3.3077115913`/etc.) → sRGB gamma curve (linear below
   `0.0031308`, power curve above). This conversion is necessary because Tailwind v4's `@theme`
   colors here are defined in OKLCH, not hex/RGB, but SVG fills need sRGB.
3. **Composition**: builds a 256×256 SVG — a rounded rect (`rx` ≈ 22% of size, matching the
   sidebar's `rounded-lg` badge proportions) filled with the primary color, and the icon's paths
   centered and scaled to ~65% of the badge, stroked (not filled) in the foreground color with
   `stroke-width="2"` and round caps/joins — matching lucide's default stroke-icon style.
4. **Rasterization**: `rsvg-convert` renders that one SVG at each target size (16/32/48/64/128/256),
   then Pillow packs all of them into a single `.ico`.

## Notes

- `frontend/public/favicon.svg` (the primary `rel="icon"` in `index.html`) is left untouched — this
  skill only writes `favicon.ico`, which `index.html` references as `rel="alternate icon"
  type="image/x-icon"` for browsers/contexts that prefer `.ico`. If the user wants the primary
  `.svg` replaced with this same derived mark too, that's a separate ask — don't do it unprompted.
- If `extract_badge_icon_name`/`extract_light_mode_color` fail (script exits with a clear `error:`
  message), it means the badge markup or CSS variable moved to a different shape than expected —
  re-read the current `app-sidebar.tsx`/`index.css` and adjust the regex in
  `scripts/generate_favicon.py` rather than hardcoding a fallback value.
