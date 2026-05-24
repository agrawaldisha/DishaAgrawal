# GlobalLogic Slide Patterns

Eight reusable slide layouts. Copy the HTML/CSS, swap in your content. Don't invent new layouts unless the content shape demands it.

All slides are **1920×1080** (16:9). Hosted by `<deck-stage>` in `deck-stage.js`, which handles scaling, keyboard nav, and print-to-PDF. Wrap them all in:

```html
<deck-stage>
  <section …>…</section>
  <section …>…</section>
</deck-stage>
```

Each section must include the **brand chrome** (top-left lockup + top-right "Confidential" + bottom-right slide number). Pattern shared by all slides:

```html
<div class="top">
  <div class="brand">
    <span class="mark"></span>
    <div><div class="name">GlobalLogic</div><div class="tag">A Hitachi Group Company</div></div>
  </div>
  <div class="conf">Confidential</div>
</div>
<!-- … slide body … -->
<div class="footer"><span>Deck name</span><span>NN / TT</span></div>
```

For dark surfaces (section divider / closing), add `.dark` to `.brand`, `.conf`, and `.footer`, and `.mark-w` to `.mark`.

---

## Pattern 01 — Cover

**Use for:** the title slide. Hero texture on the right, headline on the left.

**Visual cues:** orange-fan hero takes the right 54% of the slide, big sentence-case headline (148px) with one emphasized phrase, mono course-id label above.

```html
<section data-screen-label="01 Cover" class="s-cover">
  <div class="hero" style="background-image:url('assets/hero-orange-fan.jpg')"></div>
  <!-- top chrome -->
  <div class="pad-l stack">
    <div class="course-id">SECTION · 01</div>
    <h1>Headline goes<br>here, with <em class="hl">orange</em>.</h1>
    <div class="sub">One-sentence subtitle, 30px, steel-50 color, max-width ~780px.</div>
  </div>
  <!-- footer -->
</section>
```

**Required CSS** (per-slide; tokens come from `tokens.css`):

```css
.s-cover .hero{position:absolute;right:-60px;top:0;bottom:0;width:54%;background-size:cover;background-position:center}
.s-cover .stack{position:relative;z-index:2;max-width:1100px;padding-top:280px}
.s-cover h1{font-family:var(--gl-font-display);font-weight:700;font-size:148px;line-height:.95;letter-spacing:-.025em;margin:0 0 28px}
.s-cover .course-id{font-family:var(--gl-font-mono);font-size:22px;letter-spacing:.18em;color:var(--gl-impact-orange);font-weight:700;margin-bottom:32px}
.s-cover .sub{font-size:30px;line-height:1.3;color:var(--gl-fg-muted);max-width:780px}
```

---

## Pattern 02 — Section divider

**Use for:** the start of each major part of a deck. Steel-gray full-bleed, big sentence-case headline, orange section number, orange-stack texture glowing in the bottom-right corner.

```html
<section data-screen-label="02 Section" class="s-section">
  <div class="corner" style="background-image:url('assets/hero-orange-stack.jpg')"></div>
  <!-- top chrome (dark) -->
  <div class="pad-l stack">
    <div class="num">PART 02 · MODULE</div>
    <h2>Section title.<br>Two lines max.</h2>
    <div class="sub">One-sentence promise of what this section covers.</div>
  </div>
  <!-- footer (dark) -->
</section>
```

```css
.s-section{background:var(--gl-steel-75);color:#fff}
.s-section .corner{position:absolute;right:0;bottom:0;width:640px;height:640px;background-size:cover;background-position:center;mix-blend-mode:screen;opacity:.7}
.s-section .stack{position:relative;z-index:2;max-width:1300px;padding-top:240px}
.s-section .num{font-family:var(--gl-font-mono);font-size:20px;letter-spacing:.2em;color:var(--gl-impact-orange);margin-bottom:32px}
.s-section h2{font-family:var(--gl-font-display);font-weight:700;font-size:152px;line-height:.95;letter-spacing:-.025em;margin:0 0 28px}
.s-section .sub{font-size:28px;line-height:1.35;color:rgba(255,255,255,.7);max-width:1000px}
```

---

## Pattern 03 — Content slide (3-up or 4-up tile grid)

**Use for:** "Three reasons", "Four pillars", "Five forces". The workhorse layout. Each tile has an eyebrow label, headline, and 1–2 sentences of body.

```html
<section data-screen-label="03 Content" class="s-content">
  <!-- top chrome -->
  <div class="body">
    <div class="eyebrow">Eyebrow label</div>
    <h2>Slide headline with one <em class="hl">orange phrase</em>.</h2>
    <p class="lead">Optional lead paragraph, 22px, steel-75.</p>
    <div class="grid-3">  <!-- or .grid-4 for four tiles -->
      <div class="tile">
        <div class="lbl">01 · Topic</div>
        <h4>Tile headline.</h4>
        <p>One-to-two sentence supporting body.</p>
      </div>
      <!-- repeat -->
    </div>
  </div>
  <!-- footer -->
</section>
```

```css
.s-content h2{font-family:var(--gl-font-display);font-weight:700;font-size:80px;line-height:1.02;letter-spacing:-.02em;margin:0 0 18px}
.s-content .lead{font-size:22px;color:var(--gl-fg-muted);max-width:1400px;line-height:1.45}
.s-content .body{padding:200px 128px 120px}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;margin-top:48px}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-top:48px}
.tile{background:var(--gl-light-steel);border-radius:16px;padding:32px;display:flex;flex-direction:column;gap:14px;border-top:4px solid var(--gl-impact-orange);min-height:300px}
.tile h4{font-family:var(--gl-font-display);font-weight:700;font-size:26px;margin:0;line-height:1.15}
.tile p{font-size:16px;line-height:1.5;color:var(--gl-fg-muted);margin:0}
.tile .lbl{font-family:var(--gl-font-mono);font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--gl-impact-orange);font-weight:700}
.eyebrow{font-size:18px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--gl-impact-orange);margin-bottom:24px}
em.hl{color:var(--gl-impact-orange);font-style:normal}
```

---

## Pattern 04 — Two-column comparison

**Use for:** Old way vs. new way. Predictive vs. Generative. Underfitting vs. Overfitting. Anywhere two ideas need to face off.

```html
<div class="cmp-2">
  <div class="cmp-card steel">           <!-- light side -->
    <div class="ico">▭</div>
    <h3 class="ttl">Left column title</h3>
    <p class="desc">Body explaining the left side.</p>
  </div>
  <div class="cmp-card accent">          <!-- or .dark for steel-100 -->
    <div class="ico">◉</div>
    <h3 class="ttl">Right column title</h3>
    <p class="desc">Body explaining the right side.</p>
  </div>
</div>
```

```css
.cmp-2{display:grid;grid-template-columns:1fr 1fr;gap:48px;margin-top:48px}
.cmp-card{border-radius:18px;padding:40px 44px;display:flex;flex-direction:column;gap:16px}
.cmp-card.steel{background:var(--gl-light-steel)}
.cmp-card.accent{background:#FFF7F1;border:1px solid #FFD7BA}
.cmp-card.dark{background:var(--gl-steel-100);color:#fff}
.cmp-card .ttl{font-family:var(--gl-font-display);font-weight:700;font-size:38px;letter-spacing:-.01em;margin:0;line-height:1.05}
.cmp-card .desc{font-size:19px;line-height:1.5;color:var(--gl-fg-muted);margin:0}
.cmp-card.dark .desc{color:rgba(255,255,255,.75)}
```

---

## Pattern 05 — Stat / cheat-sheet table

**Use for:** A formal information table. Comparison matrices.

```html
<table class="cmp">
  <thead><tr><th>Feature</th><th>Column A</th><th class="accent">Column B</th></tr></thead>
  <tbody>
    <tr><td class="feat">Definition</td><td>Plain description.</td><td><b>Emphasized version.</b></td></tr>
    <!-- repeat -->
  </tbody>
</table>
```

```css
table.cmp{width:100%;border-collapse:collapse;font-size:18px;margin-top:36px}
table.cmp th, table.cmp td{padding:18px 24px;text-align:left;border-bottom:1px solid var(--gl-border);vertical-align:top}
table.cmp thead th{font-family:var(--gl-font-display);font-weight:700;font-size:22px;background:var(--gl-light-steel);color:var(--gl-fg)}
table.cmp thead th.accent{color:var(--gl-impact-orange)}
table.cmp .feat{font-family:var(--gl-font-mono);font-weight:700;font-size:14px;letter-spacing:.1em;text-transform:uppercase;color:var(--gl-fg-subtle);width:200px}
table.cmp td{font-size:18px;color:var(--gl-fg-muted);line-height:1.45}
table.cmp td b{color:var(--gl-fg);font-weight:600}
```

---

## Pattern 06 — Pull quote

**Use for:** Big editorial moments. A key takeaway. A customer voice. Dark steel-100 background, orange-blades texture glowing in the corner.

```html
<section data-screen-label="06 Quote" class="s-quote">
  <!-- top chrome (dark) -->
  <div class="body">
    <div class="attr">Attribution · context</div>
    <blockquote>"Big sentence with <em>one emphasized phrase</em> in orange."</blockquote>
    <div class="lead">Optional follow-up sentence, calmer.</div>
  </div>
  <!-- footer (dark) -->
</section>
```

```css
.s-quote{background:var(--gl-steel-100);color:#fff}
.s-quote::after{content:"";position:absolute;right:-200px;top:-200px;width:900px;height:900px;background:url('assets/hero-orange-blades.jpg') center/cover;opacity:.4;mix-blend-mode:screen;pointer-events:none}
.s-quote .body{padding:240px 200px 120px;position:relative;z-index:2}
.s-quote blockquote{font-family:var(--gl-font-display);font-weight:600;font-size:88px;line-height:1.05;letter-spacing:-.025em;margin:0;color:#fff;max-width:1500px}
.s-quote blockquote em{color:var(--gl-impact-orange);font-style:normal}
.s-quote .attr{font-family:var(--gl-font-mono);font-size:18px;letter-spacing:.16em;color:var(--gl-impact-orange);text-transform:uppercase;margin-bottom:48px;font-weight:600}
.s-quote .lead{font-size:24px;color:rgba(255,255,255,.7);margin-top:32px;max-width:1100px;line-height:1.4}
```

---

## Pattern 07 — Process flow (3, 4, or 5 steps)

**Use for:** Lifecycles. Pipelines. Step-by-step processes.

```html
<div class="flow f3">                    <!-- or .f4 for 4 steps, .f5 for 5 -->
  <div class="step"><div class="num">STEP 01</div><h4>Step name.</h4><p>What happens here.</p></div>
  <div class="arr">→</div>
  <div class="step"><div class="num">STEP 02</div><h4>Step name.</h4><p>What happens here.</p></div>
  <div class="arr">→</div>
  <div class="step"><div class="num">STEP 03</div><h4>Step name.</h4><p>What happens here.</p></div>
</div>
```

```css
.flow{display:grid;gap:14px;align-items:stretch;margin-top:48px}
.flow.f3{grid-template-columns:1fr 32px 1fr 32px 1fr}
.flow.f4{grid-template-columns:1fr 32px 1fr 32px 1fr 32px 1fr}
.flow.f5{grid-template-columns:1fr 28px 1fr 28px 1fr 28px 1fr 28px 1fr}
.flow .step{background:var(--gl-light-steel);border-radius:16px;padding:28px;display:flex;flex-direction:column;gap:10px;border-top:4px solid var(--gl-impact-orange)}
.flow .step .num{font-family:var(--gl-font-mono);font-size:12px;letter-spacing:.16em;color:var(--gl-impact-orange);font-weight:700}
.flow .step h4{font-family:var(--gl-font-display);font-weight:700;font-size:22px;margin:0;line-height:1.1}
.flow .step p{font-size:15px;line-height:1.5;color:var(--gl-fg-muted);margin:0}
.flow .arr{align-self:center;font-size:32px;color:var(--gl-impact-orange);font-weight:300;text-align:center}
```

---

## Pattern 08 — Closing slide

**Use for:** The last slide. Big "Thank you", contact info, follow-up links. Dark steel-100, orange-blades hero on the right.

```html
<section data-screen-label="NN Closing" class="s-close">
  <div class="accent" style="background-image:url('assets/hero-orange-blades.jpg')"></div>
  <!-- top chrome (dark) -->
  <h1>Thank<br>you.</h1>
  <div class="links">
    <div><span>Catalog</span><a href="…">link.url</a></div>
    <div><span>Course</span>Course name</div>
    <div><span>Audience</span>Team name</div>
  </div>
  <!-- footer (dark) -->
</section>
```

```css
.s-close{background:var(--gl-steel-100);color:#fff;display:flex;flex-direction:column;justify-content:center;padding:0 128px}
.s-close .accent{position:absolute;right:0;top:0;bottom:0;width:46%;background-size:cover;background-position:center;opacity:.55;mix-blend-mode:screen}
.s-close h1{font-family:var(--gl-font-display);font-weight:700;font-size:172px;line-height:.95;letter-spacing:-.025em;margin:0 0 56px}
.s-close .links{display:flex;gap:48px;color:rgba(255,255,255,.85);font-size:22px}
.s-close .links span{display:block;font-size:14px;letter-spacing:.14em;text-transform:uppercase;color:var(--gl-impact-orange);margin-bottom:8px;font-weight:600}
.s-close .links a{color:#fff}
```

---

## Brand chrome (used on every slide)

```css
.mark{width:38px;height:38px;background:#000;clip-path:polygon(45% 0,55% 0,55% 45%,100% 45%,100% 55%,55% 55%,55% 100%,45% 100%,45% 55%,0 55%,0 45%,45% 45%)}
.mark-w{background:#fff}
.brand{display:flex;align-items:center;gap:14px}
.brand .name{font-weight:700;font-size:22px;letter-spacing:-.01em}
.brand .tag{font-size:13px;color:var(--gl-fg-subtle);font-weight:500}
.brand.dark .name{color:#fff}
.brand.dark .tag{color:rgba(255,255,255,.6)}
.top{position:absolute;top:64px;left:128px;right:128px;display:flex;justify-content:space-between;align-items:center;z-index:3}
.conf{font-family:var(--gl-font-mono);font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--gl-fg-subtle)}
.conf.dark{color:rgba(255,255,255,.55)}
.footer{position:absolute;left:128px;right:128px;bottom:48px;display:flex;justify-content:space-between;align-items:center;font-size:14px;color:var(--gl-fg-subtle);font-family:var(--gl-font-mono);letter-spacing:.04em}
.footer.dark{color:rgba(255,255,255,.55)}
```

---

## A note on inventing new layouts

If your content shape doesn't fit one of the eight patterns above — for example, a heatmap, a Gantt chart, a side-by-side prompt + response — keep the **brand chrome, type scale, color tokens, and padding** identical to the patterns. Only the body composition changes. Refer to `reference-deck.html` for ~30 such custom one-offs from the AI-104 course.
