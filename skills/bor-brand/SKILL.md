---
name: bor-brand
description: Apply the Bor brand to a new or existing product when the user says “следуй бренду Bor”, “используй бренд Bor”, or requests Bor branding. Supplies the canonical b∅r mark, exports for web and native Android, and an optional Devices UI profile. Does not redesign the Bor logo.
---

# Bor brand kit

Use the resources shipped inside this skill; no sibling project, network connection,
font installation or MCP service is required to export them. The skill root is the
directory containing this SKILL.md. Run its scripts using their absolute paths.

## Identity and scope

- Text name: **Bor**. Graphic mark: **b∅r**, lowercase serif b and r with ∅ between
  them. Use assets/bybor-mark-light.svg for light backgrounds, dark.svg for dark.
  The SVG contours are authoritative; do not typeset, redraw, distort or add `by`
  inside the mark. These are two colors of one mark, not alternative logos.
- `by Bor` is a separate author signature. Use `<product> by Bor` only when
  appropriate for the requested product; never rename an existing product,
  domain, resource identifier or application ID merely to apply the brand.
- Default profile **identity** establishes identity only. It does not mandate
  Geist, a monochrome UI, product layout, sizes or spacing for every Bor project.
- **devices** is an opt-in reuse of the actual Devices UI: Geist, monochrome
  light/dark palettes, radii and layout values. Use it for Devices itself or when
  the user asks for the Devices look. Do not present it as a universal Bor rule.

Read references/brand.typ for the established identity and the distinction
between brand and product. Read references/integration.typ only for the target
platform you are integrating. Machine-readable values are in assets/brand.json;
use these values rather than inventing a second set of tokens.

## Apply in a project

Inspect the target project's instructions and existing components first. Choose the
identity profile unless the request or project clearly calls for Devices. Preserve
its architecture and current functionality. Explain the selected profile briefly.

Export into a dedicated directory before integrating with the project's existing
assets/theme. Do not export over its root or replace its theme wholesale:

```text
python <skill-root>/scripts/brand.py export --platform web --profile identity --output <project>/vendor/bor
python <skill-root>/scripts/brand.py export --platform android --profile devices --output <project>/vendor/bor --package <app.package>.branding
```

The export records version, origin and SHA-256 in bor-brand.lock.json. Rerunning
an unchanged export is safe. Differing files are refused unless --force is
explicitly used. Before updating an existing integration, inspect changes and
preserve deliberate product customizations.

- Web: use the supplied SVGs and bor-brand.css. The optional Devices selectors
  are scoped to data-bor-profile="devices" with data-bor-theme="light" or "dark";
  there are no global resets or required framework dependencies. example.html is
  an integration example, not a product page to copy wholesale.
- Android: integrate the res/ drawables; the launcher foreground preserves the
  existing adaptive safe area. Choose the appropriate background and launcher
  XML in the target app. Devices also exports the licensed Geist font and
  BorDevicesTokens.kt; wire these into the app's existing Compose theme. The kit
  does not change the application ID or generate a complete Android project.
- Other targets: use the canonical SVG geometry and the identity rules. OLED
  generation remains a board-specific Devices tool. Do not claim an iOS, OLED,
  Figma or full component-library exporter exists.

Validate an export with `python <skill-root>/scripts/brand.py check --output <dir>`.
This checks file integrity, not visual quality. Build the target when appropriate
and inspect real rendering in its relevant themes and sizes. Check proportional
scaling, usable contrast, legibility and accessible names. Report what was actually
verified and which target integration still needs testing.
