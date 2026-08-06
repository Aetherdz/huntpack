# HuntPack Site — Design System

Single source of truth for the HuntPack GitHub Pages site (`docs/`). Every color,
font size, spacing value, and component below traces to a token. No orphan hex codes.

## 0. Research Log (greenfield)

- Embedded refs: shortlisted `voltagent` (void-black + emerald, terminal-native),
  `shopify` (dark-first, neon green), `vercel` (black/white precision) → picked
  **Layer A `taste-skill.md`** (anti-slop landing discipline, developer audience)
  + **Layer B `voltagent.md`** (near-black canvas, emerald signal, warm charcoal
  borders, system-ui/mono — exact match for the bug-bounty terminal identity and
  the existing `banner.svg`).
- Lazyweb: skipped — no network image tooling available in this environment.
- Imagen drafts: skipped — no image-gen tool available. Hero focal object is a
  hand-built terminal window (real chrome, real content), per voltagent's
  "code snippets ARE the hero content" doctrine.
- Existing brand asset: `docs/assets/banner.svg` (reticle mark, #0d1117 family,
  #00e063 accent) — the site's canvas and accent are blended with it so the
  banner block sits flush in the hero.

## 1. Atmosphere & Identity

A deep-space command terminal for bug hunting. Near-black canvas interrupted only
by the electric pulse of emerald — the "power on" of a hunt in progress. Surfaces
are contained by warm charcoal borders, not shadows; depth reads as engineering
precision, not decoration. The signature is the **reticle**: a glowing crosshair
that says "target acquired — now verify." Every section feels like a module in a
cockpit: dense inside (mono data, stage numbers), cinematic between (huge vertical
runs). This is a tool page for hunters, not a SaaS pitch — the terminal window in
the hero is the hero.

## 2. Color

### Palette

| Role | Token | Value | Usage |
|------|-------|-------|-------|
| Canvas/void | `--bg-void` | `#08090c` | Page background |
| Canvas/hero | `--bg-hero` | `#0b0e13` | Hero band (blends banner) |
| Surface/card | `--bg-surface` | `#0f1115` | Cards, panels |
| Surface/elevated | `--bg-elevated` | `#14171c` | Terminal window, code blocks |
| Border/default | `--border` | `#2b2927` | Warm charcoal, standard containment |
| Border/strong | `--border-strong` | `#3a3733` | Emphasized containers, hover |
| Border/accent | `--accent` | `#00d992` | Active, selected, focus, links |
| Text/primary | `--text-1` | `#f0efec` | Headlines, body (snow, warm) |
| Text/secondary | `--text-2` | `#a8a29e` | Captions, lead, muted body |
| Text/tertiary | `--text-3` | `#7d8590` | Metadata, stage labels |
| Text/mint | `--mint` | `#2fd6a1` | CTA text on dark, ok-lines |
| Accent/dim | `--accent-dim` | `rgba(0,217,146,.10)` | Tints, glows, hover fills |
| Status/error | `--err` | `#fb565b` | Kill/error terminal lines only |

### Rules

- Emerald is an **accent only** — never a surface fill, never large backgrounds.
- One chromatic identity: green + warm neutrals on near-black. No blue/purple,
  no decorative warm colors (red/amber reserved for terminal error semantics).
- Depth comes from border weight/color, not shadows (voltagent doctrine).
- No pure `#000000`, no pure `#ffffff`.

## 3. Typography

### Scale (system-ui + mono only — zero web-font requests)

| Level | Token | Size | Weight | LH | LS | Usage |
|-------|-------|------|--------|----|----|-------|
| Display | `--fs-display` | `clamp(2.5rem,6vw,3.75rem)` | 700 | 1.02 | -0.025em | Hero H1 |
| H2 | `--fs-h2` | `clamp(1.75rem,3vw,2.25rem)` | 650 | 1.11 | -0.02em | Section heads |
| H3 | `--fs-h3` | `1.25rem` | 600 | 1.3 | 0 | Card titles |
| Body | `--fs-body` | `1rem` | 400 | 1.6 | 0 | Default text |
| Body/sm | `--fs-sm` | `.875rem` | 400 | 1.55 | 0 | Secondary info |
| Caption | `--fs-caption` | `.8125rem` | 500 | 1.4 | 0 | Metadata |
| Overline | `--fs-overline` | `.6875rem` | 600 | 1.3 | .14em | Uppercase labels (max 2/page) |
| Mono | `--fs-mono` | `.875rem` | 400 | 1.5 | 0 | Code, terminal |
| Mono/sm | `--fs-mono-sm` | `.75rem` | 400 | 1.45 | 0 | Terminal metadata |

### Stacks

- Sans (all text): `system-ui, -apple-system, "Segoe UI", Roboto, Ubuntu, Cantarell, "Noto Sans", sans-serif`
- Mono (terminal/code/numbers): `ui-monospace, "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", monospace`

### Rules

- Headings are compressed (LH ≤ 1.11, negative LS) — dense spec blocks, not airy copy.
- Body never below 14px. Mono reserved for code, terminal, stage numbers, buttons.
- `font-variant-numeric: tabular-nums` on stage numbers.

## 4. Spacing & Layout

### Base unit: 4px

| Token | Value | Usage |
|-------|-------|-------|
| `--sp-1` | 4px | Tight: icon gaps |
| `--sp-2` | 8px | Inline groups |
| `--sp-3` | 12px | Compact paddings |
| `--sp-4` | 16px | Standard paddings |
| `--sp-5` | 20px | Comfortable |
| `--sp-6` | 24px | Card padding, gaps |
| `--sp-8` | 32px | Between card groups |
| `--sp-10` | 40px | Within-section rhythm |
| `--sp-12` | 48px | Major breaks |
| `--sp-16` | 64px | Section rhythm |
| `--sp-20` | 80px | Hero/terminal spacing |
| `--sp-24` | 96px | Max separation |

### Grid

- Max content width: **1120px**, centered (`--content: min(1120px, 100% - 48px)`).
- Layouts: hero centered single-column; pipeline 6-col stepper; skills 3-col card
  grid (→2→1); routing 2-col split; install centered code.
- Breakpoints: sm 640 / md 768 / lg 1024. Every multi-col layout declares a
  `<768px` single-column fallback.

### Radius (locked scale)

| Token | Value | Usage |
|-------|-------|-------|
| `--r-sm` | 4px | Chips, inline code, small containers |
| `--r-md` | 6px | Buttons |
| `--r-lg` | 8px | Cards, terminal |
| `--r-pill` | 9999px | Stage tags, badges |

## 5. Components

### Reticle mark (hero + nav)
- **Structure**: inline SVG (circles + crosshair + ticks), viewBox 0 0 120 120.
- **Spacing**: 48px hero / 26px nav.
- **States**: static; glow layer pulses (hero only) via opacity on `::before` radial.
- **A11y**: `role="img"` + `aria-label="HuntPack reticle mark"`.
- **Motion**: glow `opacity` 0.35→0.85, 4s ease-in-out infinite; disabled under
  `prefers-reduced-motion`.

### Terminal window (hero focal object)
- **Structure**: `.term` card — header bar (3 traffic dots + title `huntpack — zsh`) + mono body.
- **Spacing**: padding `--sp-4/--sp-5`; radius `--r-lg`; border `--border` + `--border-strong` header.
- **States**: static; cursor blinks (mono block, steps() 1s) — meaningful "alive".
- **A11y**: the terminal is illustrative; a visually-hidden `<h2>` sibling states the pipeline summary.
- **Motion**: cursor blink only; off under reduced motion.

### Primary button (GitHub — one intent label "View on GitHub" everywhere)
- **Structure**: `<a class="btn btn-primary">` — accent border 1px, mint text, `--r-md`, padding 12px 18px.
- **States**: hover `--bg-surface`→`#1a1d22` + border `--accent`; active `translateY(1px)`; focus `outline 2px --accent` offset 2.
- **A11y**: text `--mint` on dark ≥ 9:1.

### Secondary link-button
- Same anatomy; text `--text-1`, border `--border-strong`; hover border `--accent`, text `--mint`.

### Skill card
- **Structure**: `<article class="card">` — mono name, stage tag pill, one-line desc, mono "load →" hint.
- **Spacing**: padding `--sp-6`; radius `--r-lg`; border `--border` 1px.
- **States**: hover border `--accent`, `translateY(-2px)`, glow `--accent-dim`; focus ring `--accent`.
- **Layout**: grid 3-col → 2 → 1.

### Stage stepper (pipeline)
- **Structure**: `<ol class="steps">` — 6 items, mono `01…06`, name, 4-word descriptor, node dot.
- **States**: node dot `--accent`; hover row border → `--accent`.
- **A11y**: `aria-label="Pipeline stages"` on the list.
- **Layout**: 6-col grid desktop, vertical list mobile with left rail.

### Code block (install)
- **Structure**: `.code` — `pre > code` mono on `--bg-elevated`, header bar with filename + copy button.
- **States**: copy button swaps to "Copied" (accent) for 1.6s.
- **A11y**: copy button `aria-label="Copy command"`, `role="button"` keyboard reachable.

### Site header
- **Structure**: sticky top, `--bg-void` + bottom `--border` 1px, height 64px, max-width content, flex: mark+wordmark | nav | GitHub btn.
- **Mobile**: nav collapses behind hamburger (aria-expanded), panel `--bg-surface` border-bottom.
- **States**: nav link hover → `--mint`; active section link `--accent` underline.

## 6. Motion & Interaction

| Type | Duration | Easing | Usage |
|------|----------|--------|-------|
| Micro | 120ms | ease-out | Button press, copy swap |
| Standard | 250ms | `cubic-bezier(.16,1,.3,1)` | Hover, panel open |
| Emphasis | 600ms | `cubic-bezier(.16,1,.3,1)` | Section reveal |
| Ambient | 4s | ease-in-out | Reticle glow pulse, cursor blink |

### Rules

- Only `transform` and `opacity` animate. Never layout properties.
- Reveal-on-scroll uses `IntersectionObserver` adding `.in` — no scroll listeners.
- Reduced motion (`prefers-reduced-motion: reduce`): all reveals instant, glow
  static, cursor hidden.
- Slop ban: no hover that changes nothing, no decorative loops. Glow says
  "power on", cursor says "terminal alive", reveal sequences content.

## 7. Depth & Surface

Strategy: **borders-only + one ambient glow** (voltagent).

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat | none | Page canvas |
| Contained | 1px `--border` | Cards, header, code blocks |
| Emphasized | 1px `--border-strong` | Terminal header, hover containers |
| Accent | 1px `--accent` | Active/selected, focus, links |
| Glow | `--accent-dim` radial (opacity-animated) | Hero reticle signature moment |

No box-shadows anywhere. Elevation is communicated by border weight/color and by
surface tone (`--bg-surface` → `--bg-elevated`).

## 8. Accessibility Constraints & Accepted Debt

### Constraints

- WCAG 2.2 AA floor: body ≥ 4.5:1 (measured: text-1 16:1, text-2 8:1, text-3 5.3:1,
  mint-on-surface 9:1 — all pass; large text ≥ 3:1).
- Visible `:focus-visible` ring: 2px `--accent`, offset 2px, on every interactive element.
- Full keyboard reachability: skip-link to `#main`, semantic landmarks
  (`header/nav/main/section/footer`), list semantics, `aria-expanded` on hamburger.
- `prefers-reduced-motion` fully respected (Section 6).
- `lang="en"`, unique `<title>`, meta description, OG/Twitter, JSON-LD
  (SoftwareApplication + WebSite), canonical URL.
- Terminal/code content remains readable text (no image fallbacks needed).

### Accepted Debt

| Item | Location | Why accepted | Owner / Exit |
|------|----------|--------------|--------------|
| No automated Lighthouse in CI | repo-wide | No browser tooling in this environment; page is zero-request static (no fonts/CDN/JS-heavy) so risk is low | Re-audit in browser when tooling available |
| OG image is an SVG | hero | GitHub serves SVG fine; raster generation not available here | Replace with PNG if scrapers misbehave |
