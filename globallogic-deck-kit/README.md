# GlobalLogic Deck Kit

A portable, AI-ready handoff package for producing GlobalLogic-branded presentations.

Upload the contents of this folder to **Claude**, **Gemini**, **ChatGPT**, **Cursor**, or any LLM with file ingestion. Then ask it to build a deck. It will produce HTML slides that match the GlobalLogic 2024 Presentation Template — same orange-accent treatment, same Manrope typography, same steel-gray section dividers, same restraint.

## How to use it (the 30-second version)

1. **Upload this whole folder** (or zip) to your LLM of choice.
2. **Tell it:** *"Read `INSTRUCTIONS.md`. Build a deck using the GlobalLogic brand system on the topic of [your topic]. Output a single HTML file."*
3. The model will produce a self-contained `.html` file you can open in any browser. Print to PDF for distribution, or ask the model to export `.pptx`.

That's it. Everything the model needs — visual rules, voice, layout patterns, fonts, imagery, the working reference deck — is in this folder.

## What's in here

```
globallogic-deck-kit/
├── README.md              ← you are here
├── INSTRUCTIONS.md        ← system prompt: paste/upload this with your request
├── BRAND_GUIDE.md         ← visual rules + voice + content rules
├── SLIDE_PATTERNS.md      ← 8 reusable layout recipes (cover, section, stat, quote…)
├── tokens.css             ← design tokens (colors, type scale, spacing)
├── deck-stage.js          ← slide host: scaling, keyboard nav, print-to-PDF
├── reference-deck.html    ← the 62-slide AI-104 course as a worked example
├── assets/                ← logo, hero textures, photography (JPGs)
└── fonts/                 ← Manrope TTFs (200–800 weights)
```

## What "good" looks like

A correct GlobalLogic deck has:

- **One accent color, Impact Orange `#FF671F`**, used sparingly — on a single emphasized word, an eyebrow label, a thin accent rule. Never a full background.
- **Three surfaces total**, in any single composition: White, Light Steel `#F1F2F4`, Steel Gray 75 `#384358`. No fourth.
- **Manrope** for everything (display, body, mono fallback uses JetBrains Mono).
- **Generous breathing room** — 96–128px outer padding, tight headline leading (1.02), looser body leading (1.45).
- **Faceted 3D orange hero textures** on title and divider slides (provided in `assets/hero-orange-*.jpg`).
- **No emoji, no decorative unicode glyphs** as ornaments. No gradients in UI. No frosted glass. No drop shadows louder than `rgba(0,0,0,0.06)`.

## License & attribution

Brand assets and visual vocabulary are GlobalLogic property; this kit is for internal GlobalLogic team use. Manrope is licensed under SIL Open Font License 1.1.
