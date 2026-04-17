# Dope Wars PWA Design Spec

**Goal:** Build a Progressive Web App version of the terminal Dope Wars game that can be installed and played on a phone, fully offline.

**Aesthetic:** Retro terminal — black background, green monospace text, CRT-inspired styling.

**Tech:** Pure static files (HTML/CSS/JS), no frameworks, no build step, no external dependencies.

---

## Files

All files live in `web/` alongside the existing Python game:

| File | Purpose |
|------|---------|
| `web/index.html` | Entire game — HTML structure, inline `<style>`, inline `<script>` |
| `web/manifest.json` | PWA manifest — app name, icons, theme, standalone display |
| `web/sw.js` | Service worker — cache-first offline strategy |
| `web/icon-192.png` | PWA icon 192x192 |
| `web/icon-512.png` | PWA icon 512x512 |

Icons are simple placeholders (green "DW" on black). Can be replaced later.

---

## UI Layout

Single scrollable screen, no view switching. Top to bottom:

### Header (fixed top)
- Row 1: Day counter (`Day 12/30`), current location name
- Row 2: Cash, Debt, Bank values
- Row 3: Health bar, gun count, carrying space remaining

### Market Table (main content)
- All 6 goods listed: name, current price, quantity owned
- Each row has inline Buy / Sell buttons
- Price spike = red highlight, price crash = bright green highlight

### Action Buttons (below market)
- **Jet** — tapping expands an inline destination list (5 other locations). Selecting one triggers travel (day advance, interest, new prices, events).
- **Bank** — expands inline with deposit/withdraw amount input and confirm button
- **Loan Shark** — expands inline with repay amount input and confirm button

### Events
- Event messages (mugger, found goods, price news) appear as toast overlays at the top of the screen, auto-dismiss after a few seconds
- Gun offer and trench coat offer appear as modal dialogs with Yes/No buttons

### Combat
- Cop encounters take over the screen as a full modal
- Shows: cop count, player health, event log of combat messages
- Two buttons: Fight (if guns > 0) and Run
- Dismisses when combat resolves (escaped, all cops killed, or player dies)

### Game Over
- Full-screen overlay with score breakdown: Cash + Bank - Debt = Score
- "YOU'RE DEAD" or "GAME OVER — 30 days are up!" header
- Play Again button

---

## Game Logic

Direct 1:1 port of `dopewars.py` pure functions to JavaScript.

### State Object
```javascript
{
  cash: 2000,
  debt: 5500,
  bank: 0,
  inventory: { Cocaine: 0, Heroin: 0, Acid: 0, Weed: 0, Speed: 0, Ludes: 0 },
  capacity: 100,
  currentLocation: randomChoice(LOCATIONS),
  day: 1,
  guns: 0,
  health: 100
}
```

### Constants
- `LOCATIONS`: ["Bronx", "Ghetto", "Central Park", "Manhattan", "Coney Island", "Brooklyn"]
- `GOODS`: same `{ name: [min, max] }` price ranges as Python version

### Functions
All follow the same pattern as Python: take state, return error string or null.

| Function | Signature | Notes |
|----------|-----------|-------|
| `generatePrices()` | `() → {good: price}` | Random price per good within range |
| `buy()` | `(state, good, qty, price) → string\|null` | Checks cash and capacity |
| `sell()` | `(state, good, qty, price) → string\|null` | Checks inventory |
| `deposit()` | `(state, amount) → string\|null` | Cash to bank |
| `withdraw()` | `(state, amount) → string\|null` | Bank to cash |
| `repayDebt()` | `(state, amount) → string\|null` | Caps at debt owed |
| `applyInterest()` | `(state) → void` | 10% compound on travel |
| `rollEvents()` | `(state, prices) → [{type, message, data}]` | Same probabilities as Python |
| `combatRound()` | `(state, numCops, choice) → {remaining, escaped, message}` | Fight or run |

### RNG
`Math.random()` based. Same probability thresholds as Python (15% cops, 15% price spike, 15% price crash, 10% mugger, 10% find goods, 10% gun offer, 10% coat offer).

### Rendering
One `render()` function reads state and updates the DOM directly. Called after every player action. No reactive framework.

### Input Handling
Event listeners on buttons. Quantity inputs use `<input type="number">` with appropriate min/max. Large tap targets for mobile usability (minimum 44x44px).

---

## Styling

### Retro Terminal Theme
- Background: black (`#000`)
- Text: green (`#33ff33` or similar phosphor green)
- Font: monospace system font stack (`"Courier New", Courier, monospace`)
- Subtle CRT effects via CSS: faint scanlines overlay, slight text-shadow glow
- Borders: single-line box-drawing style or simple solid green
- Inputs: black background, green text, green border
- Buttons: outlined green, green text, highlight on tap/hover

### Mobile Considerations
- Touch-friendly: all interactive elements at least 44x44px
- `user-scalable=no` to prevent zoom jank
- Body fills viewport height, scrollable content area between fixed header and action bar
- No horizontal scrolling

---

## PWA Configuration

### manifest.json
```json
{
  "name": "Dope Wars",
  "short_name": "Dope Wars",
  "start_url": "index.html",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#000000",
  "icons": [
    { "src": "icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

### Service Worker (sw.js)
- On install: cache `index.html`, `manifest.json`, `icon-192.png`, `icon-512.png`
- On fetch: cache-first strategy — serve from cache, fall back to network
- Enables full offline play after first visit

### Viewport Meta
```html
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
```

---

## What's NOT in Scope
- Sound effects or music
- Persistent high scores (could be added later via localStorage)
- Multiplayer or networking
- Custom icon art (placeholders only)
- Animations beyond basic CSS transitions
