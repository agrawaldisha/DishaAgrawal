# GlobalLogic Brand Guide

> Engineering Impact for and with clients.

GlobalLogic is a Hitachi Group company and a digital engineering services firm. The brand voice is **senior, considered, low on adjectives, craft-focused**. The visual identity is restrained: near-monochrome steel grays punctuated by a single signature accent — Impact Orange.

---

## Color

### The full palette

| Token (CSS var) | Hex | Use |
|---|---|---|
| `--gl-impact-orange` | `#FF671F` | **Primary accent.** Single phrases, eyebrow labels, accent rules. Never a background fill. |
| `--gl-impact-orange-2` | `#FF8A4C` | Hover state for orange. |
| `--gl-impact-blue` | `#1F4DFF` | Secondary highlight, link color. Use when orange is unavailable (e.g., orange-on-light-steel is too low contrast). |
| `--gl-steel-100` | `#1B1F2A` | Strongest body text on white. The closing-slide background. |
| `--gl-steel-75` | `#384358` | Section-divider background ("the navy slides"). White text on top. |
| `--gl-steel-50` | `#8B95A6` | Captions, meta, disabled state. |
| `--gl-steel-25` | `#C9CFD8` | Hairline borders, dividers, table rules. |
| `--gl-light-steel` | `#F1F2F4` | Cool off-white surface. The most-used "soft" background. |
| `--gl-white` | `#FFFFFF` | Primary background. |

### The three rules

1. **Orange is a verb, not a wallpaper.** Use it on a single emphasized word in a headline (wrap in `<em class="hl">`), an eyebrow label, a thin accent rule. Never as a slide background, never as a large card fill.
2. **Avoid orange on light steel** — the contrast is too low. Use Impact Blue or Steel Gray 100 there.
3. **Three surfaces total**, max, in any single composition: White + Light Steel + Steel Gray 75. Never introduce a fourth.

### Data-viz palette (locked away)

| Token | Hex | Use |
|---|---|---|
| `--gl-data-teal` | `#2BB1A6` | |
| `--gl-data-amber` | `#F2A93B` | Info-graphics only — when you need 4–6 |
| `--gl-data-violet` | `#7B5BD9` | distinct categorical colors. Never on |
| `--gl-data-rose` | `#E5436B` | general slides, never as accent. |
| `--gl-data-sage` | `#5BAA7C` | |

---

## Typography

**Manrope** is the brand face. Loaded from local TTFs (200–800 weights) by `tokens.css`. JetBrains Mono is the monospace.

### The scale (1920×1080 deck context)

| Role | Size | Weight | Line | Tracking | Use |
|---|---|---|---|---|---|
| Display | 148–172 | 700 | 0.95 | -0.025em | Title-slide / closing headlines. |
| H1 | 84 | 700 | 1.02 | -0.02em | Content-slide headlines. |
| H2 | 64 | 700 | 1.02 | -0.02em | Section dividers, secondary headlines. |
| H3 | 38 | 700 | 1.05 | -0.01em | Card/panel titles. |
| H4 | 26 | 700 | 1.15 | -0.005em | Tile titles. |
| Lead | 22 | 400 | 1.45 | 0 | Subtitle / lead paragraph. |
| Body | 18 | 400 | 1.5 | 0 | Tile body, card descriptions. |
| Small | 14 | 400 | 1.5 | 0 | Captions, footers. |
| Eyebrow | 18 | 600 | 1 | +0.16em UPPER | The pre-headline label. **Always Impact Orange.** |
| Mono | 13–14 | 700 | 1 | +0.14em UPPER | Section numbers, footers, labels. |

### Rules

- **Headlines are sentence case.** Not Title Case. Not ALL CAPS.
- **One emphasized word per headline,** wrapped in `<em class="hl">` (renders as Impact Orange, not italic).
- **Eyebrow labels** sit above the headline. Always in orange, always uppercase, always +0.16em letter-spacing.
- **Tabular figures** in stats and tables. Default proportional in prose.

---

## Imagery

### The signature: 3D faceted orange hero textures

`assets/hero-orange-fan.jpg`, `hero-orange-stack.jpg`, `hero-orange-blades.jpg` — high-fashion, editorial 3D renders of faceted orange forms on white. Use as:

- **Right half of the cover slide** (`background: url(...) center/cover`).
- **Bottom-right corner of section dividers**, with `mix-blend-mode: screen; opacity: 0.7` over the steel-gray background — creates a glowing accent.
- **Right portion of the closing slide**, same `screen` blend over the dark `--gl-steel-100`.

**Never** crop them small, never use as background fills, never overlay text on the busiest part.

### Photography

`assets/photo-healthcare.jpg`, `photo-finance-app.jpg`, `photo-business-meeting.jpg` — real, candid, warm lifestyle imagery. Use full-bleed in image-story slides. Never apply color tints or filters.

### Logo mark

`assets/logo-mark-black.jpg` (for white surfaces) and `logo-mark-white.jpg` (for dark surfaces) — the GlobalLogic pinwheel mark. Pair with the wordmark in a left-aligned brand lockup at top-left of every slide:

```html
<div class="brand">
  <span class="mark"></span>           <!-- CSS-drawn or img -->
  <div>
    <div class="name">GlobalLogic</div>
    <div class="tag">A Hitachi Group Company</div>
  </div>
</div>
```

### Don'ts

- ❌ No gradients. The only gradient in the system is inside the orange "golden" callout block (see SLIDE_PATTERNS.md).
- ❌ No grain, no noise overlays, no repeating patterns.
- ❌ No glassmorphism / `backdrop-filter`. Surfaces are opaque.
- ❌ No drop shadows louder than `rgba(27,31,42,0.08)`.

---

## Borders, radii, shadow

- **Radii:** 8px on most cards, 14–18px on hero cards, 999px on pill tags only.
- **Borders:** 1px Steel Gray 25 hairlines. Never 2px+.
- **Shadow:** very restrained. The shadow ramp is `0.04 / 0.06 / 0.08` alpha — barely visible. Most surfaces sit flat with a hairline border instead of a shadow.

---

## Voice

### Tone

Confident, technical, low on adjectives. GlobalLogic talks like a senior engineering partner — not like a startup, not like a consultancy. They sell expertise, not novelty.

### Canonical examples

- **Tagline:** *"Engineering Impact for and with clients."* — capital **I** on Impact. The brand treats "Impact" as a proper noun.
- *"We use color sparingly so that when it is used it is more impactful."*
- *"Our secondary colors should not be used for our presentation decks unless there is a need to visually represent a large amount of data for info graphics."*

### Casing & punctuation

- **Sentence case** for everything except brand names and proper nouns.
- Color names ARE proper nouns: **Impact Orange**, **Steel Gray 75**, **Light Steel**.
- Oxford comma.
- No exclamation marks. Ever.
- No rhetorical questions.
- Numerals: spell out one through nine in body copy; use figures for 10+, in stats, and anywhere data is the point.

### Pronouns

- **"We"** for GlobalLogic.
- **"With clients"**, **"for our partners"** — collaboration framing, not service-provider framing.

### Forbidden

- ❌ Emoji. Anywhere. Not in headings, not in lists, not in social.
- ❌ Decorative unicode (`✨`, `→`, `★`) as inline glyphs. Use drawn SVG arrows or none at all.
- ❌ Exclamation points.
- ❌ "Game-changer", "synergy", "leverage" (as a verb), "best-in-class", "leading", "innovative" — adjectives that consultancies overuse.
- ❌ "AI-powered", "next-gen", "revolutionary" — empty modifiers.

---

## Motion (when animated)

- Easing: `cubic-bezier(0.2, 0.7, 0.2, 1)` — a soft out. No bounces, no springs, no overshoots.
- Durations: 120ms for state, 220ms for component transitions, 480ms only for full-section reveals.
- Fades and 4–8px translations only. No scale-from-zero, no rotation, no parallax.
