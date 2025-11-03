# EduFunds UI Refresh – Implementation Notes

## Frontend Theme
- Introduced `Manrope` display font alongside Inter via Tailwind font family extension.
- Expanded brand palette with sand/blush accents, glow shadows, mesh gradients, and grid overlays for glassmorphism surfaces.
- Updated global `index.css` to apply mesh background, refined card/button components, enhanced badges, and modernized empty states.

## Layout & Navigation
- Rebuilt main layout header with logo-forward tile, dual CTA buttons, and blurred backdrop.
- Added background light blobs, glowing nav, and refined footer to align with new branding.
- Ensured responsive mobile navigation parity with desktop experience.

## Dashboard Experience
- Crafted hero section highlighting “Intelligente Fördermittelakquise” narrative and live cockpit stats widget.
- Visualized Ökosystem levels (EU, Bund, Länder, Stiftungen) with badges and takeaways.
- Added strategic decision matrix contrasting transformative programmes vs. agile project funding.
- Maintained stat cards, application/funding lists, and introduced institutional vs. project pathways banner.

## Funding Explorer
- New hero with landscape snapshot panel (volume, deadlines, KI coverage) and ecosystem badges.
- Enhanced filter banner, status metrics, and stat cards with interactive affordances.
- Async funding fetch now handles loading state resets with cleanup guards.

## Detail & Application Views
- Funding detail: safe async loading, CTA upgrades, consistent info boxes, and polished tab styling.
- Application detail: guarded async loading, resilient draft generation, and refreshed banners/buttons.

## Shared Components & Utilities
- Empty state component restyled with brand-forward visuals.
- Tailwind config extended for display font, shadows, mesh backgrounds, and brand colors.
- Search page copy updated with German quotation marks; debounced search uses `useCallback`.

## Quality Gates
- `npm run lint`
- `npm run build`
