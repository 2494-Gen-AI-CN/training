# D-0019 — Site theme: cool slate neutrals with self-hosted Inter (body) and JetBrains Mono (code); Revature orange accent kept

- Date: 2026-10-11
- Status: accepted
- Decision: Site theme: cool slate neutrals with self-hosted Inter (body) and JetBrains Mono (code); Revature orange accent kept
- Why: Whole-site palette review (calendar + notes page rendered in light and dark for four candidates). Cool blue-grey neutrals make the five phase colours and the orange CTAs stand out; the dark surface #0b1220 gives the best legibility of the set (accent 8.0:1). Inter/JetBrains Mono replace the inconsistent OS font stacks. Fonts are self-hosted latin-subset variable woff2 (80 KB total) so the site stays offline-safe and free of third-party requests.
- Affects: docs/assets/css/style.css (:root and dark tokens, @font-face), docs/assets/fonts/, every page via ?v= cache-bust
- Supersedes: —
- Superseded-by: —

## Notes

Rejected: B editorial cream with Source Serif headings (textbook feel, heaviest fonts, cream projects yellow), C high-contrast Plex (best for projectors but plainest), D harbour teal (best contrast but drops the orange identity). Google Fonts <link> rejected in favour of self-hosting: classroom Wi-Fi and privacy. Phase colours unchanged (D-0018).
