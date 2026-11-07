# New Mexico Eats: name, icon and palette (final: Nick's decisions, 2026-11-07)

Final (Nick, 2026-11-07, "Yes, as proposed" on the 17-state review): the name and App Store subtitle as in
`playbook/app-store/listing.json`, icon concept A, the red chile pod, and the palette as built (below).

## Name
- **New Mexico Eats** (App Store name "New Mexico Eats: Red or Green", 29 characters; Home Screen "New Mexico Eats", 15). "Red or green?"
  is New Mexico's official state question (the chile you want), so it goes in the App Store name, not the brand. A web search
  (2026-11-06) found no app called "New Mexico Eats"; go-newmexico.com, a private travel site, has a general "New Mexico Eats" page, and
  EatingNewMexico.com is a food blog. Nick approved the name on 2026-11-07; no domain or USPTO search was run.
- Alternatives from the prompt: **Red or Green** (the state question, used by many local businesses, so hard to own) and **Enchanted
  Eats** (the "Land of Enchantment" nickname; a common business name). "Chile" stays out of the name (search mixes in the country).
- Avoided: the Tourism Department's "New Mexico True" brand, the Zia sun symbol (Zia Pueblo holds it sacred), the state flag, UNM and
  NMSU team names and marks.
- Bundle id `com.newmexicoeats.ios`; site nickstrom5.github.io/new-mexico-eats/ until a `newmexico.eatsranked.com` record exists.

## Icon (state-prompts/ICON-STYLE.md)
- **A, Nick's choice (2026-11-07): a ripe red chile pod with its green calyx and stem**, side view, on turquoise. Passes check.swift; reads as
  a chile at 60 px. It's red, not green, because Colorado Eats' icon is already a green chile pod (on navy): the strip60 comparison
  shows the two apart.
- B: a puffed sopaipilla with a honey drizzle, on turquoise. Passes; at 60 px it reads as a bread roll.
- C: a breakfast burrito smothered "Christmas" (red and green), on adobe. Passes; at 60 px it reads more like a sofa than a burrito.
Drawn by `scripts/icon-concepts.swift` (PNGs in `playbook/brand/`); `scripts/make-brand.swift` makes the app icon, site icons and
docs/og.png from A.

## Palette ("Christmas", the prompt's second option; no Zia, no team colors)
Chile red #8C1D18 (9.1:1 on white) for titles and tint; green chile #3F6B22 (white on it 6.3:1) for the hand-checked guide cards;
turquoise #0E7C86 (white on it 4.9:1) for honors chips, focus rings and the icon; chile yellow #FFD700 (the flag's) only as a fill under
chile-red text; adobe #FAF4E6 pages. Header band: the Sandia Mountains' long ridge in chile red over a green-chile and a chile-red
stripe.
