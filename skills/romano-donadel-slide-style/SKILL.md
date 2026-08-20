---
name: romano-donadel-slide-style
description: >
  Create or standardize Romano Donadel PowerPoint or HTML presentations with a
  corporate, minimalist and data-oriented identity. Use for executive reports,
  legal strategy decks, dashboards, investigations, client updates, analytical
  tables, timelines, comparisons and presentation templates that require the
  official white, black, dark-gray and orange visual system.
---

# Romano Donadel Corporate Slide Style

## Objective

Apply a corporate visual system that communicates clarity, control, precision and executive quality. Use this skill for new decks and for visual standardization of existing decks. Preserve the substantive content, client assets and declared data. Change only the visual treatment unless the user requests a content redesign.

Read `references/identidade-visual-extraida.md` before creating a new deck or standardizing a legacy deck. It records patterns extracted from the office materials without carrying client content into new work.

## Official visual system

| Role | Token | Use |
|---|---|---|
| Background | `#FFFFFF` | Main slide surface and content areas |
| Primary text | `#000000` | Main text, key numbers and high-priority information |
| Structure | `#63666A` | Secondary text, grid lines, borders, labels, footers and structural elements |
| Accent | `#F7A800` | Section bars, titles, subtitles, markers, important figures and decisive highlights |

Use white as the dominant visual field. Use orange to guide attention, not as a dominant fill. Do not use navy blue, metallic gold, gradients, ornamental frames or decorative iconography. If an existing deck contains legacy navy or gold, replace those tokens with the official system while preserving the content and layout. Do not alter an external client logo or its own mandatory colors.

## Logo and branding

Use the supplied official asset `assets/logo_romano_donadel.png` for Romano Donadel branding. It is the original gray-and-orange mark with transparency.

- Preserve its aspect ratio, transparent background and colors.
- Place it in the upper-right corner with clear margin on content slides.
- Use it smaller than the slide title and never as a decorative background.
- On cover slides, use the original mark centered or upper-right according to the composition.
- If a client logo is present, use its supplied white version when a dark-gray or orange support area is appropriate. Do not recolor, redraw or invent logos.

## Typography

Prioritize **Lato** for titles, body text and data labels. Use the bundled template and local assets so a deck does not depend on an external logo, template or image that may disappear from the environment.

| Element | Preferred font | Fallback | Rule |
|---|---|---|---|
| Titles | Lato Bold or Lato Heavy | Arial Bold, Calibri Bold or Noto Sans Bold | Uppercase, concise and high contrast |
| Body | Lato Regular or Lato Semibold | Arial, Calibri or Noto Sans | Plain, legible and technical |
| Data labels | Lato Semibold | Same fallback family as body | Use weight only when a value is decisive |

Use the local font only when the environment already provides it or when the user supplies a licensed font file. Do not download a font during generation. If Lato is unavailable, use a local sans-serif fallback and record the fallback in the generation manifest. Do not use decorative, handwritten or highly condensed fonts. Keep a single title family and a single body family throughout the deck.

## Default layout

Use 16 by 9 as the default format for new presentations. Preserve the aspect ratio of an existing file when editing it.

- Use white background with a consistent left and right margin.
- Keep the logo in the upper-right corner with breathing room.
- Use a short uppercase title at the upper-left.
- Add a thin orange rule, small orange marker or vertical orange section bar only when it improves hierarchy.
- Keep footer elements discreet in dark gray. Use confidentiality, date, page number or attribution only when relevant to the deck.
- Align all panels, table columns, diagrams and chart areas to a clear grid.
- Reserve generous white space around titles, data and conclusions.

## Required components

### Cover

Use the project title, client or matter identification, optional subtitle, date and Romano Donadel logo. Keep the cover sparse. A black-and-white architectural image may be used when supplied or explicitly requested. Do not add stock decoration merely to fill space.

### Section divider

Use a short uppercase section name, a vertical orange bar or thin orange rule and large white space. Use this pattern for changes of subject in longer reports.

### Executive summary

Use three to five indicators, conclusions or alerts. Make the critical number visually prominent in orange or black. Provide a short source label when the data needs attribution.

### Analytical table

Use white rows, dark-gray grid lines, black body text and an orange table title or decisive cell. Do not fill every cell with orange. Reserve semantic colors such as green, yellow and red for explicitly labeled operational status or risk only.

### Dashboard and chart

Choose the chart that directly answers the question. Use labels, totals and comparisons that remain readable at presentation distance. Use orange for the focal series or critical value, black and dark gray for the remaining series. Use a color legend whenever a status palette is used.

### Comparison, timeline and diagram

Use aligned columns, restrained borders, orthogonal connectors and clear labels. Prefer a small number of visual groups over dense decorative flows. State the decision, contrast or conclusion near the visual when it is not self-evident.

## Content hierarchy

- Use uppercase titles with a clear conclusion or topic.
- Keep one principal idea per content slide.
- Use bold only for information that merits immediate attention.
- Prefer tables, blocks, comparisons, timelines and diagrams over dense prose.
- Keep text technically precise and easy to scan.
- Do not use more than three or four supported points on a content slide unless the slide is an analytical table.
- Preserve exact legal terms, numbers, dates and citations supplied by the user.

## HTML tokens

Use the following tokens for HTML slides.

```css
:root {
  --rd-background: #FFFFFF;
  --rd-text: #000000;
  --rd-structure: #63666A;
  --rd-accent: #F7A800;
}
```

Use `assets/logo_romano_donadel.png` as the logo path and `templates/romano-donadel-base.pptx` as the native PowerPoint starting template when creating a new deck. Preserve both assets inside the project or package. Use `assets/` and `templates/` as local sources for recurring images and boilerplate. Do not reference a client machine path, a remote URL or a temporary upload path. If a new image is essential and no local asset exists, request or generate it once, copy it into the project and record it in the manifest before using it.

## Quality gate

Before delivering a deck, confirm all of the following.

1. The background is predominantly white.
2. Text, grid lines, labels and footers use black or dark gray.
3. Orange is limited to hierarchy, emphasis and critical data.
4. Titles are short, uppercase and visibly distinct from body content.
5. The Romano Donadel logo is present, proportionate and undistorted when branding is required.
6. Headers and footers are consistent across comparable slides.
7. Tables, charts and diagrams are readable without decorative clutter.
8. Status colors have declared meaning and are not used as brand decoration.
9. No navy-blue or metallic-gold legacy token remains unless it belongs to an immutable client asset.
10. The content, numbers, legal meaning and source attribution were not changed merely to apply styling.

## Available bundled resources

| Resource | Purpose |
|---|---|
| `assets/logo_romano_donadel.png` | Official Romano Donadel logo supplied by Ricardo |
| `templates/romano-donadel-base.pptx` | Local 16 by 9 starter template with logo, header, footer and official tokens |
| `references/identidade-visual-extraida.md` | Patterns extracted from office reference materials and component guidance |

Every recurring logo, template and office-owned image used by this skill must be bundled under `assets/` or `templates/`. Do not assume a file exists on the client machine. When working from an existing PowerPoint, preserve its valid structure and apply the visual rules directly.
