# Build a deck from scratch (paste this prompt)

Copy this exact text into Claude / Gemini / ChatGPT alongside the contents of the kit folder.

---

```
You have access to the GlobalLogic Deck Kit. Before doing anything:

1. Read INSTRUCTIONS.md in full.
2. Read BRAND_GUIDE.md.
3. Read SLIDE_PATTERNS.md.
4. Skim reference-deck.html to see how the patterns compose into a real 62-slide deck.

Now build me a deck.

TOPIC: [one sentence describing the deck]

AUDIENCE: [who's in the room]

LENGTH: [number of slides, or duration in minutes]

SECTIONS: [section breaks you want, comma-separated — or "decide for me"]

REQUIRED CONTENT: [paste any source material, outlines, key messages, stats]

Output a single self-contained HTML file. Link to tokens.css and deck-stage.js (they live alongside in the kit). Use the 8 patterns from SLIDE_PATTERNS.md. Follow the voice rules in BRAND_GUIDE.md. Don't invent layouts unless content shape demands it.
```

---

# Rebrand an existing deck (paste this prompt)

```
You have access to the GlobalLogic Deck Kit. Before doing anything:

1. Read INSTRUCTIONS.md, BRAND_GUIDE.md, SLIDE_PATTERNS.md.
2. Skim reference-deck.html.

I'm attaching an existing deck (PDF / PPTX / text dump). Rebuild it in the GlobalLogic visual system:

- Carry every fact and list item across. Do not summarize or omit.
- Map each source slide to one of the 8 patterns in SLIDE_PATTERNS.md based on its information shape.
- Preserve section breaks (Part 01, Part 02 …) as steel-gray section dividers.
- Rewrite voice to match BRAND_GUIDE.md — sentence case, no exclamation marks, no emoji, one orange anchor word per headline.
- Keep slide numbering sequential (01 / NN through NN / NN).

Output a single self-contained HTML file linking to tokens.css and deck-stage.js.

[Attach source deck here]
```

---

# Single-file portable output (paste this prompt)

```
Build me the deck described above, but output a SINGLE HTML file with everything inlined:

- Inline tokens.css into a <style> block
- Inline deck-stage.js into a <script> block
- Convert font @font-face URLs to base64 data URIs from the fonts/ folder
- Replace image references with base64 data URIs from the assets/ folder

The output should open and render correctly even if I delete every other file in the kit.
```

---

# Export to PPTX (paste this prompt, after building the HTML)

```
The HTML deck is built. Now export it to a .pptx file.

Best path: open the HTML in a headless browser, navigate slide by slide, screenshot each <section> at 1920×1080, and stitch the screenshots into a 16:9 PowerPoint at 200 DPI.

If you can't do that, give me a print-to-PDF version and instructions for importing into PowerPoint.
```
