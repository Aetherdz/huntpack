# HuntPack Site — Design System

Single source of truth for the HuntPack GitHub Pages site (`docs/`). Every color,
font size, spacing value, and component below traces to a token. No orphan hex codes.

## 0. Research Log (greenfield)

- Embedded refs: first pass picked `voltagent` (void-black + emerald, terminal-native).
  **RE-ROUTED on user request** — the user named a live site ("شوف موقع opencode — سوي
  لي نفس الأسلوب"): Layer B reference `opencode.ai.md` becomes the token source of
  truth. **Layer A `taste-skill.md`** stays (anti-slop landing discipline).
  Live site fetched (`The open source AI coding agent`, terminal hero, monospace
  everywhere, nav GitHub/Docs/Download) → layout grammar captured.
- Lazyweb: skipped — no network image tooling available in this environment.
- Imagen drafts: skipped — no image-gen tool available. Hero focal object is an
  ASCII terminal window (opencode-style), hand-written in `<pre>`.
- Existing brand asset: `docs/assets/banner.svg` (reticle mark, `#0d1117` + `#00e063`)
  — the emerald accent is preserved as the single brand accent (replacing opencode's
  blue); the cool canvas is dropped for opencode's warm near-black. The raster
  banner stays a repo asset, not the page hero.

## 1. Atmosphere & Identity

A terminal emulator at 2am: warm near-black (`#201d1d`, a lived-in reddish-brown,
never clinical black) with off-white text (`#fdfcfc`) — every word, every label,
every button rendered in the same monospace voice. Nothing decorative, nothing
elevated: surfaces are flat, depth comes from hairlines and background shifts,
the way a real terminal has no shadows. The signature is the **ASCII reticle** —
a crosshair drawn in box-drawing characters inside the hero terminal, the one
moment that says "target acquired." Sections are separated by generous vertical
spacing, not dividers. This is a code tool speaking code: hierarchy is size and
weight alone, the brand accent (emerald) appears surgically on the few things
that act.

## 2. Color

### Palette

| Role | Token | Value | Usage |
|------|-------|-------|-------|
| Canvas | `--bg` | `#201d1d` | Page background, button fills (warm near-black) |
| Surface/elevated | `--bg-elevated` | `#302c2c` | Terminal windows, code blocks, hover fills |
| Border/warm | `--border` | `rgba(15,0,0,.12)` | Hairline separators, section rules |
| Border/outline | `--border-strong` | `#646262` | Container outlines, button borders |
| Text/primary | `--text-1` | `#fdfcfc` | Headlines, body, button text (warm off-white) |
| Text/secondary | `--text-2` | `#9a9898` | Lead, captions, muted links |
| Text/muted | `--text-3` | `#84848a` | Metadata, line numbers, tags (lifted from #6e6e73 to pass WCAG AA 4.5:1 on `--bg`) |
| Accent | `--accent` | `#00e063` | Brand emerald — links, focus, key highlights (replaces opencode blue) |
| Success | `--ok` | `#30d158` | Confirmed findings, positive lines |
| Danger | `--err` | `#ff3b30` | Killed findings, errors |
| Warning | `--warn` | `#ff9f0a` | Suspicious-but-unconfirmed, warnings |

### Rules

- Accent is used **only** on interactive or high-signal moments. Never decorative fills.
- Semantic colors follow Apple HIG (like opencode): green = success, red = danger,
  orange = warning — reserved for terminal verdict lines.
- No pure `#000000`, no pure `#ffffff`. Warm undertone is load-bearing.
- One accent: emerald everywhere or nowhere. No second chromatic voice.

## 3. Typography

### Scale (Berkeley Mono register — mono everywhere, zero web-font requests)

| Level | Token | Size | Weight | LH | Usage |
|-------|-------|------|--------|----|-------|
| H1 | `--fs-h1` | `38px` | 700 | 1.5 | Hero title |
| H1/mobile | — | `clamp(28px, 6vw, 38px)` | 700 | 1.4 | Hero < 640px |
| H2 | `--fs-h2` | `16px` | 700 | 1.5 | Section titles, group labels |
| Body | `--fs-body` | `16px` | 400 | 1.5 | Paragraphs |
| Body/medium | — | `16px` | 500 | 1.5 | Links, buttons, nav |
| Caption | `--fs-caption` | `14px` | 400 | 2.0 | Footnotes, metadata, tags |
| Terminal | `--fs-mono` | `14px` | 400 | 1.6 | ASCII hero, code blocks |

### Stack (single family — "everything is code")

`"Berkeley Mono", "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", Courier New, monospace`

### Rules

- **One font, one voice.** No sans-serif, no serif anywhere. Hierarchy is weight
  (700/500/400) and size only.
- Line-height 1.5 standard, 2.0 relaxed for captions — the monospace grid breathes.
- Never introduce a second typeface. No web fonts loaded.

## 4. Spacing & Layout

### Base unit: 8px (4px for fine adjustments only)

| Token | Value | Usage |
|-------|-------|-------|
| `--sp-1` | 4px | Micro adjustments, borders |
| `--sp-2` | 8px | Tight gaps, icon spacing |
| `--sp-3` | 12px | Compact paddings |
| `--sp-4` | 16px | Standard gaps, list rhythm |
| `--sp-5` | 20px | Comfortable paddings |
| `--sp-6` | 24px | Card/inner paddings, gaps |
| `--sp-8` | 32px | Between groups |
| `--sp-10` | 40px | Within-section rhythm |
| `--sp-12` | 48px | Major section breaks |
| `--sp-16` | 64px | Section rhythm |
| `--sp-20` | 80px | Hero/terminal spacing |
| `--sp-24` | 96px | Maximum separation |

### Grid

- Max content width: **880px** centered (`--content: min(880px, 100% - 48px)`) —
  narrow, reading-optimized, like opencode.
- Primary pattern: single column. Lists and terminal blocks span full width.
- Breakpoints: sm 640 / md 768 / lg 1024. Multi-column (footer) collapses below 640.
- Hero: centered, terminal block full-width of content.

### Radius (locked scale — two values only)

| Token | Value | Usage |
|-------|-------|-------|
| `--r-default` | 4px | Everything: buttons, containers, code blocks |
| `--r-input` | 6px | (reserved) form inputs only |

No pills, no large radii. Utilitarian corners.

## 5. Components

### Terminal window (hero + routing)
- **Structure**: `<pre>` with box-drawing characters, no chrome bars — the ASCII is
  the whole element (opencode-style). Single monospace block, flat `--bg-elevated`.
- **Spacing**: padding `--sp-6`; radius `--r-default`; border `--border-strong` 1px.
- **States**: static; accent used inside for "ok"/verdict lines.
- **A11y**: `aria-label` describes the demo; copy inside remains selectable text.

### Primary button
- **Structure**: `<a class="btn">` — `--bg` fill, `--text-1` text, 1px `--border-strong`, radius `--r-default`, padding **4px 20px**, weight 500.
- **States**: hover — border lightens to `#8a8888`, text → `--accent`; active — bg shifts `--bg-elevated`; focus — 1px solid `--accent` outline.
- **A11y**: text `#fdfcfc` on `#201d1d` = 13:1. One label per intent ("View on GitHub").

### Text link
- **Structure**: `<a>` — `--text-1`, weight 500, **underline 1px** by default (opencode default link).
- **States**: hover — color → `--accent`; focus — 1px `--accent` outline.
- **Variants**: muted (`--text-2`, no underline) for nav/secondary; accent (`--accent`) for key CTAs.

### Skill row (the "arsenal" — no cards, pure text)
- **Structure**: list of rows, `16px` mono — name (weight 700) + one-line desc (weight 400, `--text-2`) + stage tag (caption, `--text-3`). Rows separated by `1px var(--border)` hairlines.
- **States**: hover — name → `--accent`; row bg shift to `--bg-elevated`.
- **Layout**: single column, `--sp-4` vertical rhythm between items. Group labels as code comments (`// understand`).

### Stage list (pipeline)
- **Structure**: ordered list, mono rows `01 → 06` — num (accent), name (700), descriptor (400, `--text-2`). Hairline separators.
- **States**: hover row bg → `--bg-elevated`.
- **A11y**: `aria-label="Pipeline stages"`.

### Code block (install)
- **Structure**: `<pre>` mono on `--bg-elevated`, `--border-strong`, radius 4px. Copy button in top-right (caption size).
- **States**: copy swaps to "Copied" (`--ok`) for 1.6s.

### Navigation
- Horizontal, `--bg` solid (no blur), single line at desktop, height 64px.
- Brand logotype left in mono, links weight 500 with underline on hover, one dark-fill button right.
- Mobile (<640px): collapses to toggle, stacked panel.

## 6. Motion & Interaction

| Type | Duration | Easing | Usage |
|------|----------|--------|-------|
| Micro | 120ms | ease-out | Hover color/border shifts |

### Rules

- **Minimal by design** (terminal-inspired): color transitions 100–150ms only.
- No scale, no translate, no rotate, no reveal-on-scroll, no glow pulses, no marquee.
- Motion serves state: hover/active/focus feedback only. Content appears instantly.
- `prefers-reduced-motion`: nothing to reduce beyond the 120ms color fades — they are
  not disabled because they are not motion-sensitive (color-only, no vestibular impact).

## 7. Depth & Surface

Strategy: **flat, border-only** (opencode — zero shadows, zero gradients, zero blur).

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat | none | Page canvas, most text |
| Subtle | `1px var(--border)` | Hairline separators between rows/lists |
| Outline | `1px var(--border-strong)` | Terminal windows, code blocks, buttons |

Surface differentiation via `--bg` → `--bg-elevated` shifts only. No elevation
illusion anywhere.

## 8. Accessibility Constraints & Accepted Debt

### Constraints

- WCAG 2.2 AA floor: text-1 on bg 13:1, text-2 on bg 6.6:1, muted 4.7:1, accent
  `#00e063` on `#201d1d` ≈ 7:1 — all pass AA; body is AAA.
- Visible `:focus-visible`: 1px `--accent` outline offset 2px on every interactive element.
- Full keyboard reachability: skip-link to `#main`, landmarks (`header/nav/main/section/footer`),
  list semantics, `aria-expanded` on nav toggle, `aria-label` on copy buttons.
- `lang="en"`, unique `<title>`, meta description, OG/Twitter, JSON-LD
  (SoftwareApplication + WebSite), canonical URL.
- Terminal/pre content is real selectable text — no images.

### Accepted Debt

| Item | Location | Why accepted | Owner / Exit |
|------|----------|--------------|--------------|
| No automated Lighthouse in CI | repo-wide | No browser tooling in this environment; page is zero-request static (no fonts/CDN/JS-heavy) | Re-audit in browser when tooling available |
| OG image is an SVG | hero | GitHub serves SVG fine; raster generation not available here | Replace with PNG if scrapers misbehave |
| Berkeley Mono not self-hosted | typography | No font files available; falls back to ui-monospace/SFMono (system-native, zero cost) | Self-host WOFF2 if brand fidelity demanded |
