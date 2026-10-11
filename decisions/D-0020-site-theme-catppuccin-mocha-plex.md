# D-0020 — Site theme: Catppuccin Mocha dark by default with Latte as the optional light mode; IBM Plex Sans + IBM Plex Mono self-hosted; no Revature branding colours

- Date: 2026-10-11
- Status: accepted
- Decision: Site theme: Catppuccin Mocha dark by default with Latte as the optional light mode; IBM Plex Sans + IBM Plex Mono self-hosted; no Revature branding colours
- Why: Readability from a home monitor was the brief: no pure black (halation), off-white ink around 11:1 rather than 21:1, pastel accents capped near 8:1 so emphasis stays gentle on 1,500-word pages, and a matched sans/mono pair so code and prose align. Dark is now the designed default; the OS preference only wins when it explicitly asks for light, and the toggle still saves a choice.
- Affects: docs/assets/css/style.css (tokens, @font-face), docs/assets/fonts/, docs/assets/js/theme.js resolve(), every page via ?v= cache-bust
- Supersedes: —
- Superseded-by: —

## Notes

Supersedes the look of D-0019 but not its mechanics (self-hosted latin-subset fonts, token-only theming) so it is logged as a new entry rather than a supersede. Rejected: Graphite (neutral but bland), Nord (best glare profile, weakest accent 6.2:1 and blue cast on phase colours), Gruvbox (warm, yellow cast collides with the amber Gen AI phase). Known trade-offs: Latte light mode is the weakest of the four at 7.1:1 ink and the blue accent sits near the data-phase blue.
