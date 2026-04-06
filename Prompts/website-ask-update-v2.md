---
max_turns: 150
effort: medium
---

# 00-template-partials-refactor
effort: high

## What and Why

Refactor `template.html` from a single monolithic HTML file into section-based partial templates. This makes each section independently editable and safe for parallel CC sessions. Also update `build.py` to assemble partials, and update `CLAUDE.md` to document the new architecture.

### Target structure

```
sections/
  head.html          # Everything up to and including <body> / outer wrapper open
  home.html          # home-section
  market.html        # market-section
  businessmodel.html # businessmodel-section (or however it's IDed)
  physics.html       # physics/engineering section
  team.html          # team-section
  ask.html           # ask-section
  closing.html       # final slide/CTA section + closing tags
  pitch-video.html   # pitch-video-section (if it's a separate section)
```

Use the existing `<section id="...">` tags in the HTML as split points. Each partial contains everything from the section's opening tag through its closing tag. `head.html` is the preamble (doctype, head, opening body/wrapper tags). `closing.html` is everything after the last section through `</html>`, including any trailing scripts.

### build.py changes

Update `build.py` to:
1. Read all `.html` files from `sections/` in a defined order (maintain a `SECTION_ORDER` list in build.py rather than relying on alphabetical sort).
2. Concatenate them into the full template HTML.
3. Then do the existing `{{placeholder}}` replacement from `content.yaml` as before.
4. Write `index.html` as before.

Preserve the existing markdown-to-HTML conversion logic (`**bold**`, `==highlight==`, `[link](url)`, paragraph wrapping in `<span class="p">`). Don't change that.

Remove `template.html` after confirming the new pipeline produces identical output.

### CLAUDE.md updates

Update the Architecture section and Content Pipeline section to reflect:
- `template.html` no longer exists; replaced by `sections/*.html`
- `build.py` assembles sections before placeholder replacement
- Section order is defined in `build.py`
- To edit a section's structure, edit `sections/name.html`
- To edit text content, edit `content.yaml` (unchanged)
- CDN script tags can be added to any section partial or to `head.html`

## Constraints

- The output of `python build.py` after this refactor must produce byte-identical `index.html` to what the current pipeline produces. Diff them to verify.
- Don't change `content.yaml`.
- Don't rename any CSS classes or IDs — just split the file at section boundaries.
- Keep all inline `<script>` and `<style>` blocks in whichever partial they belong to.

## Done When

- `cp index.html index_before.html` (save current), then `python build.py`, then `diff index_before.html index.html` shows no differences
- `template.html` is deleted (or renamed to `template.html.bak` if you want a safety net)
- `ls sections/` shows the partial files
- `CLAUDE.md` documents the new architecture
- Git commit all changes with message: "Refactor template.html into section partials, update build.py and CLAUDE.md"

---

# 01-ask-section-text-update
depends_on: 00-template-partials-refactor

## What and Why

Update the Ask section text in `content.yaml` to reflect the revised fundraising strategy: wider round range (up to €500k), corrected ZIM feasibility figures (€100k eligible/study at 70% = €70k grant, not €87.5k), ZIM R&D Kooperation added to the cascade, EIC Pathfinder alongside SPRIND, and removal of "single check" / "not assembling a syndicate" language.

Replace these YAML values exactly:

**`text02`:**
```
**Strategic Investment Round.**

FluxTech is raising up to €500k to join committed capital.

This is a leverage round. Every euro of equity activates a cascade of non-dilutive grants, scaling total deployment from ~€400k to ~€1M depending on round size.
```

**`text06`:**
```
==GründungsBONUS Plus (Berlin)==: Triggers up to €50k in matched grant funding directly from this private raise.

==Two ZIM Feasibility Studies (Federal)==: Provides up to €140k in R&D funding to validate our two primary technical risks.

==ZIM R&D Kooperationsprojekt (Federal)==: Scales with co-funding capacity. Up to €252k for FluxTech plus up to €280k for a research partner.
```

**`text34`:**
```
Total Strategic Deployment: From ~€400k to ~€1M, depending on round size.
```

**`text38`:**
```
**The Technical Gate.**

Successful completion of these studies positions FluxTech for the next funding layer. This includes SPRIND (up to €1M) and EIC Pathfinder (up to €3M), all without requiring additional equity.
```

Leave `text39`, `text35`, `text33`, `text01` unchanged.

## Constraints

- Only edit values in `content.yaml`. Do not change keys.
- Do not touch any `sections/*.html` files or `build.py`.
- Preserve YAML formatting conventions: `|` for multiline, markdown (`**bold**`, `==highlight==`).
- Run `python build.py` after edits.

## Done When

- `python build.py` runs without errors
- `grep -c "€80k" content.yaml` returns 0
- `grep -c "€87.5k" content.yaml` returns 0
- `grep -c "€490k" content.yaml` returns 0
- `grep -c "single check" content.yaml` returns 0
- `grep -c "not assembling a syndicate" content.yaml` returns 0
- `grep "500k" content.yaml` returns matches
- `grep "EIC Pathfinder" content.yaml` returns a match
- `grep "Kooperationsprojekt" content.yaml` returns a match
- Git commit all changes with message: "Update Ask section: widen round to €500k, correct ZIM figures, add ZIM R&D and EIC Pathfinder"

---

# 02-ask-interactive-widget
depends_on: 01-ask-section-text-update
effort: high

## What and Why

Add an interactive grant leverage calculator to the Ask section as the hero element. Investors drag a slider to explore how their check size activates non-dilutive grants — stacked bar chart + live metric cards update in real time. Uses Chart.js from CDN.

### Implementation

Edit `sections/ask.html` to:

1. Add `<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>` near the top of the section partial (or in a script tag before the widget).
2. Insert the widget HTML between the `{{text39}}` block (funding cascade intro) and the `{{text35}}` block (milestones).
3. Hide the static `{{text06}}` and `{{text34}}` elements with `display: none` in a scoped style block — keep the placeholders so build.py doesn't break, but don't show the static text since the widget replaces it.

### Widget structure

1. **Slider**: "Investment size" from €100k to €500k, step €10k, default €250k. Styled to match the site (dark background, cyan/green accent).
2. **Four metric cards** in a responsive row: Total dilutive, Total non-dilutive, Total deployment, Grant leverage. Dark card backgrounds, gradient accent on labels.
3. **Stacked bar chart** (Chart.js). Stacks: Private capital (#5F5E5A), GründungsBONUS (#1D9E75), ZIM feasibility (#3266ad), ZIM R&D (#7F77DD). X-axis: check sizes €100k–€500k in €50k steps. Y-axis: total capital in €k.
4. **Shaded "optimal zone"** overlay from €200k–€350k with a label, drawn via a Chart.js plugin.
5. **Footer text**: "Next non-dilutive layer: SPRIND (up to €1M) · EIC Pathfinder (up to €3M) — no additional equity required"

### Grant cascade formulas (embed exactly)

```javascript
const COMMITTED = 55;
const BONUS = 50;
const FEAS_GRANT = 140;
const FEAS_COFUND = 60;
const OPERATING_RESERVE = 80;
const BUFFER = 20;

function calc(newCheckK) {
  const totalDilutive = COMMITTED + newCheckK;
  const coFundAvail = Math.max(0, totalDilutive - FEAS_COFUND - OPERATING_RESERVE - BUFFER);
  const zimRD = Math.min(coFundAvail * (45 / 55), 252);
  const totalNonDilutive = BONUS + FEAS_GRANT + zimRD;
  const totalDeployment = totalDilutive + totalNonDilutive;
  const leverage = totalNonDilutive / totalDilutive;
  return { totalDilutive, zimRD, totalNonDilutive, totalDeployment, leverage };
}
```

### Design

- Match existing site aesthetic: dark backgrounds (#1a1d21 or similar from the site CSS), Poppins font, cyan-green gradient accent (#00B573 to #0096CE).
- Chart background transparent, grid lines subtle (rgba white at low opacity).
- Metric cards: dark surface, small muted label, large white number.
- Slider: custom-styled with accent color thumb, dark track.
- Chart.js legend: disabled (use custom HTML legend above chart with colored squares).
- Responsive: metric cards stack 2x2 on mobile, chart fills width.
- All widget CSS scoped to a wrapper class (e.g. `.grant-widget`) to avoid leaking into other sections.

## Constraints

- Only edit `sections/ask.html`. Do not modify `content.yaml`, `build.py`, or other section partials.
- Chart.js loaded from `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js` — no other external dependencies.
- All widget JS inline within `sections/ask.html` (not a separate .js file).
- Preserve all `{{placeholder}}` tokens in ask.html — build.py must still succeed.
- Test with `python -m http.server 8000` (YouTube embeds and some features require HTTP, not file://).

## Done When

- `python build.py` runs without errors
- `python -m http.server 8000 &` serves the site
- `curl -s http://localhost:8000 | grep -c "chart.umd.js"` returns 1 (Chart.js CDN loaded)
- `curl -s http://localhost:8000 | grep -c 'type="range"'` returns at least 1 (slider present)
- `curl -s http://localhost:8000 | grep -c "COMMITTED"` returns at least 1 (widget JS present)
- `curl -s http://localhost:8000 | grep -c "€87.5k"` returns 0 (old figures gone from visible content)
- `curl -s http://localhost:8000 | grep -c "EIC Pathfinder"` returns at least 1
- Visual check: open in browser, drag slider, confirm chart and metrics update in real time
- Git commit all changes with message: "Add interactive grant leverage widget to Ask section with Chart.js"
