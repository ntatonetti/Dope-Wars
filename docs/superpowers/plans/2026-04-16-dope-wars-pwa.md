# Dope Wars PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a mobile-friendly Progressive Web App version of the terminal Dope Wars game as pure static files, installable on a phone and playable offline.

**Architecture:** Single `web/index.html` with inline CSS and JS. Game logic is a 1:1 port of `dopewars.py` pure functions to JavaScript. A `render()` function updates the DOM after every action. PWA support via `manifest.json` and a cache-first service worker (`sw.js`). Retro green-on-black terminal aesthetic.

**Tech Stack:** Vanilla HTML/CSS/JS (no frameworks, no build step), PWA (manifest + service worker)

**Design Spec:** `docs/superpowers/specs/2026-04-16-dope-wars-pwa-design.md`

---

### Task 1: PWA Shell — manifest.json, service worker, and HTML skeleton

**Files:**
- Create: `web/manifest.json`
- Create: `web/sw.js`
- Create: `web/index.html`

This task creates the PWA infrastructure and a minimal HTML page that registers the service worker. No game logic yet — just enough to verify the PWA installs and caches correctly.

- [ ] **Step 1: Create `web/manifest.json`**

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

- [ ] **Step 2: Create `web/sw.js`**

```javascript
const CACHE_NAME = 'dopewars-v1';
const ASSETS = [
  'index.html',
  'manifest.json',
  'icon-192.png',
  'icon-512.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
```

- [ ] **Step 3: Create minimal `web/index.html` with PWA registration**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
  <meta name="theme-color" content="#000000">
  <link rel="manifest" href="manifest.json">
  <link rel="apple-touch-icon" href="icon-192.png">
  <title>Dope Wars</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #000;
      color: #33ff33;
      font-family: "Courier New", Courier, monospace;
      font-size: 14px;
      min-height: 100vh;
      min-height: 100dvh;
    }
    #app { padding: 8px; }
  </style>
</head>
<body>
  <div id="app">Dope Wars loading...</div>
  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('sw.js');
    }
  </script>
</body>
</html>
```

- [ ] **Step 4: Verify PWA shell loads**

Run: `cd web && python3 -m http.server 8000`

Open `http://localhost:8000` in a browser. Verify:
- Black screen with green "Dope Wars loading..." text
- No console errors
- Service worker registers (check DevTools > Application > Service Workers)

- [ ] **Step 5: Commit**

```bash
git add web/manifest.json web/sw.js web/index.html
git commit -m "feat(pwa): add PWA shell with manifest, service worker, and HTML skeleton"
```

---

### Task 2: Placeholder Icons

**Files:**
- Create: `web/icon-192.png`
- Create: `web/icon-512.png`

Generate simple placeholder PWA icons using an inline canvas in a Node script (or Python). Green "DW" text on black background.

- [ ] **Step 1: Create a Python script to generate icons**

```python
# web/generate_icons.py
from PIL import Image, ImageDraw, ImageFont
import sys

def make_icon(size, path):
    img = Image.new('RGB', (size, size), '#000000')
    draw = ImageDraw.Draw(img)
    font_size = size // 3
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Courier.dfont", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()
    text = "DW"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) // 2
    y = (size - th) // 2
    draw.text((x, y), text, fill='#33ff33', font=font)
    img.save(path)
    print(f"Created {path}")

if __name__ == "__main__":
    make_icon(192, "icon-192.png")
    make_icon(512, "icon-512.png")
```

If `Pillow` is not available, use this alternative approach that creates icons via an HTML canvas and saves as data URL, or just create minimal valid PNGs using pure Python:

```python
# web/generate_icons.py (no-dependency fallback)
import struct
import zlib

def create_png(width, height, bg_rgb, text_rgb):
    """Create a minimal PNG with a colored background."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    raw = b''
    for y in range(height):
        raw += b'\x00'  # filter byte
        for x in range(width):
            raw += bytes(bg_rgb)
    idat = chunk(b'IDAT', zlib.compress(raw))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

if __name__ == "__main__":
    for size, name in [(192, 'icon-192.png'), (512, 'icon-512.png')]:
        data = create_png(size, size, (0, 0, 0), (0x33, 0xff, 0x33))
        with open(name, 'wb') as f:
            f.write(data)
        print(f"Created {name}")
```

- [ ] **Step 2: Generate icons**

Run: `cd web && python3 generate_icons.py`

Verify both `icon-192.png` and `icon-512.png` exist and are valid images.

- [ ] **Step 3: Clean up and commit**

```bash
rm web/generate_icons.py
git add web/icon-192.png web/icon-512.png
git commit -m "feat(pwa): add placeholder PWA icons"
```

---

### Task 3: Game Constants and State

**Files:**
- Modify: `web/index.html` (add to `<script>` block)

Port the constants (`LOCATIONS`, `GOODS`) and initial state factory from `dopewars.py`.

- [ ] **Step 1: Add constants and state initialization to `web/index.html`**

Replace the `<script>` block content (keeping the service worker registration) with:

```javascript
// --- Constants ---
const LOCATIONS = ['Bronx', 'Ghetto', 'Central Park', 'Manhattan', 'Coney Island', 'Brooklyn'];

const GOODS = {
  Cocaine: [15000, 30000],
  Heroin:  [5000, 14000],
  Acid:    [1000, 4500],
  Weed:    [300, 900],
  Speed:   [70, 250],
  Ludes:   [10, 60],
};

const GOOD_NAMES = Object.keys(GOODS);

// --- State ---
function createState() {
  const inventory = {};
  for (const g of GOOD_NAMES) inventory[g] = 0;
  return {
    cash: 2000,
    debt: 5500,
    bank: 0,
    inventory,
    capacity: 100,
    currentLocation: LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)],
    day: 1,
    guns: 0,
    health: 100,
  };
}

function generatePrices() {
  const prices = {};
  for (const [good, [lo, hi]] of Object.entries(GOODS)) {
    prices[good] = lo + Math.floor(Math.random() * (hi - lo + 1));
  }
  return prices;
}

// --- Service Worker ---
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}

// --- Boot ---
let state = createState();
let prices = generatePrices();
document.getElementById('app').textContent = `Cash: $${state.cash} | Location: ${state.currentLocation}`;
```

- [ ] **Step 2: Verify state initialization works**

Run: `cd web && python3 -m http.server 8000`

Open `http://localhost:8000`. Verify the page shows "Cash: $2,000 | Location: [some location]" in green text on black.

- [ ] **Step 3: Commit**

```bash
git add web/index.html
git commit -m "feat(pwa): add game constants, state factory, and price generation"
```

---

### Task 4: Core Game Logic Functions

**Files:**
- Modify: `web/index.html` (add to `<script>` block, before `// --- Boot ---`)

Port all pure game logic functions from `dopewars.py`: buy, sell, deposit, withdraw, repayDebt, applyInterest, rollEvents, combatRound.

- [ ] **Step 1: Add buy and sell functions**

Insert before `// --- Boot ---`:

```javascript
// --- Game Logic ---
function buy(state, good, qty, price) {
  const cost = price * qty;
  if (cost > state.cash) return "You can't afford that!";
  const carried = Object.values(state.inventory).reduce((a, b) => a + b, 0);
  if (carried + qty > state.capacity) return "You can't carry that much!";
  state.cash -= cost;
  state.inventory[good] += qty;
  return null;
}

function sell(state, good, qty, price) {
  if (state.inventory[good] < qty) return "You don't have that many!";
  state.cash += price * qty;
  state.inventory[good] -= qty;
  return null;
}
```

- [ ] **Step 2: Add bank and loan shark functions**

Insert after sell:

```javascript
function deposit(state, amount) {
  if (amount > state.cash) return "You don't have that much cash!";
  state.cash -= amount;
  state.bank += amount;
  return null;
}

function withdraw(state, amount) {
  if (amount > state.bank) return "You don't have that much in the bank!";
  state.bank -= amount;
  state.cash += amount;
  return null;
}

function repayDebt(state, amount) {
  if (amount > state.cash) return "You don't have that much cash!";
  amount = Math.min(amount, state.debt);
  state.cash -= amount;
  state.debt -= amount;
  return null;
}

function applyInterest(state) {
  state.debt = Math.floor(state.debt * 1.10);
}
```

- [ ] **Step 3: Add random events**

Insert after applyInterest:

```javascript
function rollEvents(state, prices) {
  const events = [];

  if (Math.random() < 0.15) {
    const good = ['Weed', 'Speed', 'Ludes'][Math.floor(Math.random() * 3)];
    const multiplier = 4 + Math.floor(Math.random() * 5);
    prices[good] = GOODS[good][1] * multiplier;
    events.push({ type: 'price_spike', message: `Cops made a bust! ${good} prices skyrocket!` });
  }

  if (Math.random() < 0.15) {
    const good = ['Cocaine', 'Heroin', 'Acid'][Math.floor(Math.random() * 3)];
    const divisor = 4 + Math.floor(Math.random() * 5);
    prices[good] = Math.floor(GOODS[good][0] / divisor);
    events.push({ type: 'price_crash', message: `${good} prices have bottomed out!` });
  }

  if (Math.random() < 0.10) {
    const good = GOOD_NAMES[Math.floor(Math.random() * GOOD_NAMES.length)];
    let amount = 2 + Math.floor(Math.random() * 5);
    const carried = Object.values(state.inventory).reduce((a, b) => a + b, 0);
    const space = state.capacity - carried;
    amount = Math.min(amount, space);
    if (amount > 0) {
      state.inventory[good] += amount;
      events.push({ type: 'find_goods', message: `You find ${amount} units of ${good} on the ground!` });
    }
  }

  if (Math.random() < 0.10 && state.cash > 0) {
    const lost = 1 + Math.floor(Math.random() * Math.max(1, Math.floor(state.cash / 3)));
    state.cash -= lost;
    events.push({ type: 'mugger', message: `A mugger attacks! You lose $${lost.toLocaleString()}!` });
  }

  if (Math.random() < 0.15) {
    const minCops = 1 + Math.floor(state.day / 10);
    const maxCops = Math.max(minCops, Math.min(3 + Math.floor(state.day / 5), 8));
    const numCops = minCops + Math.floor(Math.random() * (maxCops - minCops + 1));
    events.push({ type: 'cops', message: `Officer Hardass and ${numCops} cops are chasing you!`, data: numCops });
  }

  if (Math.random() < 0.10) {
    events.push({ type: 'gun_offer', message: 'Would you like to buy a gun for $400?', data: 400 });
  }

  if (Math.random() < 0.10) {
    events.push({ type: 'coat_offer', message: 'Would you like to buy a trench coat for $200?', data: 200 });
  }

  return events;
}
```

- [ ] **Step 4: Add combat**

Insert after rollEvents:

```javascript
function combatRound(state, numCops, choice) {
  if (choice === 'run') {
    const escapeChance = Math.max(0.2, Math.min(0.9, 1.0 - numCops * 0.1));
    if (Math.random() < escapeChance) {
      return { remaining: numCops, escaped: true, message: 'You escaped!' };
    }
    const damage = numCops * (3 + Math.floor(Math.random() * 5));
    state.health = Math.max(0, state.health - damage);
    return { remaining: numCops, escaped: false, message: `You couldn't escape! They hit you for ${damage} damage.` };
  }

  if (choice === 'fight') {
    if (state.guns <= 0) {
      return { remaining: numCops, escaped: false, message: "You don't have any guns!" };
    }
    numCops -= 1;
    if (numCops > 0) {
      const damage = numCops * (3 + Math.floor(Math.random() * 5));
      state.health = Math.max(0, state.health - damage);
      return { remaining: numCops, escaped: false, message: `You killed a cop! ${numCops} remaining. They hit you for ${damage} damage.` };
    }
    return { remaining: 0, escaped: false, message: 'You killed the last cop!' };
  }

  return { remaining: numCops, escaped: false, message: '' };
}
```

- [ ] **Step 5: Quick smoke test in browser console**

Open `http://localhost:8000`, then in DevTools console:

```javascript
// Test buy
let s = createState(); s.cash = 10000;
console.assert(buy(s, 'Ludes', 5, 20) === null);
console.assert(s.cash === 9900);
console.assert(s.inventory.Ludes === 5);

// Test sell
console.assert(sell(s, 'Ludes', 3, 50) === null);
console.assert(s.cash === 10050);

// Test deposit/withdraw
console.assert(deposit(s, 1000) === null);
console.assert(s.bank === 1000);
console.assert(withdraw(s, 500) === null);
console.assert(s.cash === 9550);

console.log('All smoke tests passed');
```

- [ ] **Step 6: Commit**

```bash
git add web/index.html
git commit -m "feat(pwa): add all game logic — buy, sell, bank, events, combat"
```

---

### Task 5: HTML Structure and CSS Styling

**Files:**
- Modify: `web/index.html` (replace `<style>` and `<body>` content)

Build out the full UI structure and retro terminal CSS. No interactivity yet — just the static layout that `render()` will populate.

- [ ] **Step 1: Replace the `<style>` block with full CSS**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --green: #33ff33;
  --dim: #1a8c1a;
  --bg: #000;
  --red: #ff4444;
  --bright-green: #66ff66;
}

body {
  background: var(--bg);
  color: var(--green);
  font-family: "Courier New", Courier, monospace;
  font-size: 14px;
  min-height: 100vh;
  min-height: 100dvh;
  overflow-x: hidden;
}

/* CRT scanline overlay */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    rgba(0,0,0,0.15) 0px,
    rgba(0,0,0,0.15) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
  z-index: 9999;
}

#header {
  position: sticky;
  top: 0;
  background: var(--bg);
  border-bottom: 1px solid var(--dim);
  padding: 8px;
  z-index: 10;
  text-shadow: 0 0 5px var(--green);
}

.header-row {
  display: flex;
  justify-content: space-between;
  padding: 2px 0;
  flex-wrap: wrap;
  gap: 4px;
}

.header-row span {
  white-space: nowrap;
}

#market {
  padding: 8px;
}

#market table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

#market th {
  text-align: left;
  border-bottom: 1px solid var(--dim);
  padding: 4px 2px;
  color: var(--dim);
}

#market td {
  padding: 6px 2px;
  border-bottom: 1px solid #0a3a0a;
}

#market tr.spike td { color: var(--red); }
#market tr.crash td { color: var(--bright-green); }

#market .qty-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn {
  background: transparent;
  color: var(--green);
  border: 1px solid var(--green);
  font-family: inherit;
  font-size: 13px;
  padding: 6px 10px;
  min-width: 44px;
  min-height: 44px;
  cursor: pointer;
  text-shadow: 0 0 3px var(--green);
}

.btn:active {
  background: var(--green);
  color: var(--bg);
}

.btn:disabled {
  border-color: var(--dim);
  color: var(--dim);
  text-shadow: none;
}

#actions {
  padding: 8px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

#actions .btn {
  flex: 1;
  min-width: 80px;
}

.panel {
  padding: 8px;
  border: 1px solid var(--dim);
  margin: 8px;
  display: none;
}

.panel.open { display: block; }

.panel-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin: 6px 0;
}

.panel-row input {
  background: var(--bg);
  color: var(--green);
  border: 1px solid var(--green);
  font-family: inherit;
  font-size: 14px;
  padding: 6px;
  width: 100px;
  min-height: 44px;
}

.modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 100;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

.modal-overlay.open {
  display: flex;
}

.modal {
  border: 1px solid var(--green);
  padding: 16px;
  max-width: 360px;
  width: 100%;
  background: var(--bg);
  text-shadow: 0 0 5px var(--green);
}

.modal h2 {
  font-size: 16px;
  margin-bottom: 12px;
}

.modal .btn {
  margin-top: 8px;
  margin-right: 8px;
}

.toast {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  padding: 10px;
  text-align: center;
  font-weight: bold;
  z-index: 200;
  transition: opacity 0.3s;
  text-shadow: 0 0 5px var(--green);
  background: var(--bg);
  border-bottom: 1px solid var(--green);
}

.toast.fade-out { opacity: 0; }

#buy-modal .modal { max-width: 300px; }
```

- [ ] **Step 2: Replace the `<body>` HTML structure**

```html
<body>
  <!-- Header -->
  <div id="header">
    <div class="header-row">
      <span id="h-day">Day 1/30</span>
      <span id="h-location">Bronx</span>
    </div>
    <div class="header-row">
      <span id="h-cash">Cash: $2,000</span>
      <span id="h-debt">Debt: $5,500</span>
      <span id="h-bank">Bank: $0</span>
    </div>
    <div class="header-row">
      <span id="h-health">HP: 100</span>
      <span id="h-guns">Guns: 0</span>
      <span id="h-space">Space: 100</span>
    </div>
  </div>

  <!-- Market -->
  <div id="market">
    <table>
      <thead>
        <tr><th>Good</th><th>Price</th><th>Own</th><th></th></tr>
      </thead>
      <tbody id="market-body"></tbody>
    </table>
  </div>

  <!-- Action buttons -->
  <div id="actions">
    <button class="btn" id="btn-jet">JET</button>
    <button class="btn" id="btn-bank">BANK</button>
    <button class="btn" id="btn-shark">SHARK</button>
  </div>

  <!-- Jet panel (inline expand) -->
  <div id="jet-panel" class="panel">
    <div id="jet-destinations"></div>
  </div>

  <!-- Bank panel (inline expand) -->
  <div id="bank-panel" class="panel">
    <div class="panel-row">
      <input type="number" id="bank-amount" min="1" placeholder="Amount">
      <button class="btn" id="btn-deposit">DEP</button>
      <button class="btn" id="btn-withdraw">WD</button>
    </div>
  </div>

  <!-- Loan shark panel (inline expand) -->
  <div id="shark-panel" class="panel">
    <div class="panel-row">
      <input type="number" id="shark-amount" min="1" placeholder="Amount">
      <button class="btn" id="btn-repay">REPAY</button>
    </div>
  </div>

  <!-- Buy modal -->
  <div id="buy-modal" class="modal-overlay">
    <div class="modal">
      <h2 id="buy-title">Buy Ludes</h2>
      <p id="buy-info">Price: $50 | Max: 20</p>
      <div class="panel-row">
        <input type="number" id="buy-amount" min="1">
        <button class="btn" id="btn-buy-confirm">BUY</button>
        <button class="btn" id="btn-buy-cancel">X</button>
      </div>
      <p id="buy-error"></p>
    </div>
  </div>

  <!-- Sell modal -->
  <div id="sell-modal" class="modal-overlay">
    <div class="modal">
      <h2 id="sell-title">Sell Ludes</h2>
      <p id="sell-info">Price: $50 | Have: 10</p>
      <div class="panel-row">
        <input type="number" id="sell-amount" min="1">
        <button class="btn" id="btn-sell-confirm">SELL</button>
        <button class="btn" id="btn-sell-cancel">X</button>
      </div>
      <p id="sell-error"></p>
    </div>
  </div>

  <!-- Event offer modal (gun/coat) -->
  <div id="offer-modal" class="modal-overlay">
    <div class="modal">
      <p id="offer-text"></p>
      <button class="btn" id="btn-offer-yes">YES</button>
      <button class="btn" id="btn-offer-no">NO</button>
    </div>
  </div>

  <!-- Combat modal -->
  <div id="combat-modal" class="modal-overlay">
    <div class="modal">
      <h2>COPS!</h2>
      <p id="combat-info">Cops: 3 | HP: 100</p>
      <div id="combat-log"></div>
      <div id="combat-buttons">
        <button class="btn" id="btn-fight">FIGHT</button>
        <button class="btn" id="btn-run">RUN</button>
      </div>
      <button class="btn" id="btn-combat-done" style="display:none;">OK</button>
    </div>
  </div>

  <!-- Game over modal -->
  <div id="gameover-modal" class="modal-overlay">
    <div class="modal">
      <h2 id="gameover-title">GAME OVER</h2>
      <pre id="gameover-score"></pre>
      <button class="btn" id="btn-play-again">PLAY AGAIN</button>
    </div>
  </div>

  <script>
    // ... (game logic and boot code from previous tasks go here)
  </script>
</body>
```

- [ ] **Step 3: Verify layout in browser**

Run: `cd web && python3 -m http.server 8000`

Open `http://localhost:8000`. Verify:
- Green text on black background
- Scanline effect visible
- Header, empty market table, JET/BANK/SHARK buttons visible
- All elements legible and not overlapping

- [ ] **Step 4: Commit**

```bash
git add web/index.html
git commit -m "feat(pwa): add HTML structure and retro terminal CSS"
```

---

### Task 6: Render Function and Market Display

**Files:**
- Modify: `web/index.html` (add `render()` and market rendering to `<script>`)

The `render()` function reads state and prices and updates every DOM element. Also tracks which goods had price spikes/crashes for highlighting.

- [ ] **Step 1: Add event highlight tracking and render function**

Insert before `// --- Boot ---`:

```javascript
// --- UI State ---
let priceHighlights = {};  // { goodName: 'spike' | 'crash' }
let openPanel = null;      // 'jet' | 'bank' | 'shark' | null

function formatMoney(n) {
  return '$' + n.toLocaleString();
}

function render() {
  // Header
  document.getElementById('h-day').textContent = `Day ${state.day}/30`;
  document.getElementById('h-location').textContent = state.currentLocation;
  document.getElementById('h-cash').textContent = `Cash: ${formatMoney(state.cash)}`;
  document.getElementById('h-debt').textContent = `Debt: ${formatMoney(state.debt)}`;
  document.getElementById('h-bank').textContent = `Bank: ${formatMoney(state.bank)}`;
  document.getElementById('h-health').textContent = `HP: ${state.health}`;
  document.getElementById('h-guns').textContent = `Guns: ${state.guns}`;
  const carried = Object.values(state.inventory).reduce((a, b) => a + b, 0);
  document.getElementById('h-space').textContent = `Space: ${state.capacity - carried}`;

  // Market
  const tbody = document.getElementById('market-body');
  tbody.innerHTML = '';
  for (const good of GOOD_NAMES) {
    const tr = document.createElement('tr');
    if (priceHighlights[good] === 'spike') tr.className = 'spike';
    if (priceHighlights[good] === 'crash') tr.className = 'crash';

    const tdName = document.createElement('td');
    tdName.textContent = good;
    tr.appendChild(tdName);

    const tdPrice = document.createElement('td');
    tdPrice.textContent = formatMoney(prices[good]);
    tr.appendChild(tdPrice);

    const tdOwn = document.createElement('td');
    tdOwn.textContent = state.inventory[good];
    tr.appendChild(tdOwn);

    const tdBtns = document.createElement('td');
    tdBtns.className = 'qty-cell';

    const buyBtn = document.createElement('button');
    buyBtn.className = 'btn';
    buyBtn.textContent = 'B';
    buyBtn.addEventListener('click', () => openBuyModal(good));
    tdBtns.appendChild(buyBtn);

    if (state.inventory[good] > 0) {
      const sellBtn = document.createElement('button');
      sellBtn.className = 'btn';
      sellBtn.textContent = 'S';
      sellBtn.addEventListener('click', () => openSellModal(good));
      tdBtns.appendChild(sellBtn);
    }

    tr.appendChild(tdBtns);
    tbody.appendChild(tr);
  }

  // Panels
  document.getElementById('jet-panel').className = openPanel === 'jet' ? 'panel open' : 'panel';
  document.getElementById('bank-panel').className = openPanel === 'bank' ? 'panel open' : 'panel';
  document.getElementById('shark-panel').className = openPanel === 'shark' ? 'panel open' : 'panel';
}
```

- [ ] **Step 2: Update boot code to call render**

Replace the `// --- Boot ---` section:

```javascript
// --- Boot ---
let state = createState();
let prices = generatePrices();

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}

render();
```

- [ ] **Step 3: Verify market renders**

Open `http://localhost:8000`. Verify:
- Header shows Day 1/30, a location, Cash: $2,000, Debt: $5,500, etc.
- Market table shows all 6 goods with prices and "B" buttons
- All owned quantities show 0

- [ ] **Step 4: Commit**

```bash
git add web/index.html
git commit -m "feat(pwa): add render function with header and market display"
```

---

### Task 7: Buy and Sell Modals

**Files:**
- Modify: `web/index.html` (add modal handlers to `<script>`)

Wire up the buy/sell modals with quantity input, validation, and confirmation.

- [ ] **Step 1: Add buy modal logic**

Insert before `// --- Boot ---`:

```javascript
// --- Buy/Sell Modals ---
let activeBuyGood = null;
let activeSellGood = null;

function openBuyModal(good) {
  activeBuyGood = good;
  const price = prices[good];
  const maxAfford = price > 0 ? Math.floor(state.cash / price) : 0;
  const carried = Object.values(state.inventory).reduce((a, b) => a + b, 0);
  const maxCarry = state.capacity - carried;
  const maxQty = Math.min(maxAfford, maxCarry);

  document.getElementById('buy-title').textContent = `Buy ${good}`;
  document.getElementById('buy-info').textContent = `Price: ${formatMoney(price)} | Max: ${maxQty}`;
  document.getElementById('buy-amount').value = '';
  document.getElementById('buy-amount').max = maxQty;
  document.getElementById('buy-error').textContent = '';
  document.getElementById('buy-modal').classList.add('open');
  document.getElementById('buy-amount').focus();
}

function openSellModal(good) {
  activeSellGood = good;
  const price = prices[good];
  const have = state.inventory[good];

  document.getElementById('sell-title').textContent = `Sell ${good}`;
  document.getElementById('sell-info').textContent = `Price: ${formatMoney(price)} | Have: ${have}`;
  document.getElementById('sell-amount').value = '';
  document.getElementById('sell-amount').max = have;
  document.getElementById('sell-error').textContent = '';
  document.getElementById('sell-modal').classList.add('open');
  document.getElementById('sell-amount').focus();
}

document.getElementById('btn-buy-confirm').addEventListener('click', () => {
  const qty = parseInt(document.getElementById('buy-amount').value);
  if (!qty || qty <= 0) {
    document.getElementById('buy-error').textContent = 'Enter a number.';
    return;
  }
  const err = buy(state, activeBuyGood, qty, prices[activeBuyGood]);
  if (err) {
    document.getElementById('buy-error').textContent = err;
    return;
  }
  document.getElementById('buy-modal').classList.remove('open');
  showToast(`Bought ${qty} ${activeBuyGood}.`);
  render();
});

document.getElementById('btn-buy-cancel').addEventListener('click', () => {
  document.getElementById('buy-modal').classList.remove('open');
});

document.getElementById('btn-sell-confirm').addEventListener('click', () => {
  const qty = parseInt(document.getElementById('sell-amount').value);
  if (!qty || qty <= 0) {
    document.getElementById('sell-error').textContent = 'Enter a number.';
    return;
  }
  const err = sell(state, activeSellGood, qty, prices[activeSellGood]);
  if (err) {
    document.getElementById('sell-error').textContent = err;
    return;
  }
  const revenue = prices[activeSellGood] * qty;
  document.getElementById('sell-modal').classList.remove('open');
  showToast(`Sold ${qty} ${activeSellGood} for ${formatMoney(revenue)}.`);
  render();
});

document.getElementById('btn-sell-cancel').addEventListener('click', () => {
  document.getElementById('sell-modal').classList.remove('open');
});
```

- [ ] **Step 2: Add toast notification function**

Insert before the buy/sell modal code:

```javascript
// --- Toast Notifications ---
function showToast(message, duration = 2000) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}
```

- [ ] **Step 3: Verify buy/sell flow**

Open `http://localhost:8000`. Verify:
- Click "B" on a good → buy modal opens with correct price and max
- Enter a quantity, click BUY → modal closes, toast shows "Bought X ...", cash decreases, inventory increases
- Click "S" on a good you own → sell modal opens, sell works, cash increases
- Cancel buttons close modals
- Error messages show for invalid amounts

- [ ] **Step 4: Commit**

```bash
git add web/index.html
git commit -m "feat(pwa): add buy/sell modals with toast notifications"
```

---

### Task 8: Jet (Travel), Bank, and Loan Shark Panels

**Files:**
- Modify: `web/index.html` (add panel handlers to `<script>`)

Wire up the three action panels: Jet (travel to new location), Bank (deposit/withdraw), and Loan Shark (repay debt).

- [ ] **Step 1: Add panel toggle and Jet logic**

Insert before `// --- Boot ---`:

```javascript
// --- Action Panels ---
function togglePanel(name) {
  openPanel = openPanel === name ? null : name;
  render();
}

document.getElementById('btn-jet').addEventListener('click', () => {
  togglePanel('jet');
  if (openPanel === 'jet') {
    const dest = document.getElementById('jet-destinations');
    dest.innerHTML = '';
    const destinations = LOCATIONS.filter(l => l !== state.currentLocation);
    for (const loc of destinations) {
      const btn = document.createElement('button');
      btn.className = 'btn';
      btn.style.display = 'block';
      btn.style.width = '100%';
      btn.style.marginBottom = '4px';
      btn.textContent = loc;
      btn.addEventListener('click', () => travel(loc));
      dest.appendChild(btn);
    }
  }
});

function travel(location) {
  state.currentLocation = location;
  state.day += 1;
  applyInterest(state);
  prices = generatePrices();
  priceHighlights = {};
  openPanel = null;

  const events = rollEvents(state, prices);

  // Track price highlights
  for (const ev of events) {
    if (ev.type === 'price_spike') {
      const good = GOOD_NAMES.find(g => ev.message.includes(g));
      if (good) priceHighlights[good] = 'spike';
    }
    if (ev.type === 'price_crash') {
      const good = GOOD_NAMES.find(g => ev.message.includes(g));
      if (good) priceHighlights[good] = 'crash';
    }
  }

  render();
  processEvents(events);
}
```

- [ ] **Step 2: Add Bank panel logic**

Insert after the Jet code:

```javascript
document.getElementById('btn-bank').addEventListener('click', () => togglePanel('bank'));

document.getElementById('btn-deposit').addEventListener('click', () => {
  const amt = parseInt(document.getElementById('bank-amount').value);
  if (!amt || amt <= 0) { showToast('Enter a number.'); return; }
  const err = deposit(state, amt);
  if (err) { showToast(err); return; }
  document.getElementById('bank-amount').value = '';
  showToast(`Deposited ${formatMoney(amt)}.`);
  render();
});

document.getElementById('btn-withdraw').addEventListener('click', () => {
  const amt = parseInt(document.getElementById('bank-amount').value);
  if (!amt || amt <= 0) { showToast('Enter a number.'); return; }
  const err = withdraw(state, amt);
  if (err) { showToast(err); return; }
  document.getElementById('bank-amount').value = '';
  showToast(`Withdrew ${formatMoney(amt)}.`);
  render();
});
```

- [ ] **Step 3: Add Loan Shark panel logic**

Insert after the Bank code:

```javascript
document.getElementById('btn-shark').addEventListener('click', () => togglePanel('shark'));

document.getElementById('btn-repay').addEventListener('click', () => {
  const amt = parseInt(document.getElementById('shark-amount').value);
  if (!amt || amt <= 0) { showToast('Enter a number.'); return; }
  const err = repayDebt(state, amt);
  if (err) { showToast(err); return; }
  document.getElementById('shark-amount').value = '';
  showToast(`Repaid ${formatMoney(amt)}. Remaining: ${formatMoney(state.debt)}`);
  render();
});
```

- [ ] **Step 4: Verify all three panels**

Open `http://localhost:8000`. Verify:
- JET: click JET → list of 5 destinations appears. Click one → day advances, location changes, new prices appear. Panels close.
- BANK: click BANK → deposit/withdraw input appears. Deposit reduces cash, increases bank. Withdraw does the reverse.
- SHARK: click SHARK → repay input appears. Repay reduces cash and debt.
- Clicking an already-open panel button closes it.
- Price spike/crash highlights show red/green after travel.

- [ ] **Step 5: Commit**

```bash
git add web/index.html
git commit -m "feat(pwa): add travel, bank, and loan shark panels"
```

---

### Task 9: Event Processing — Offers, Combat, and Game Over

**Files:**
- Modify: `web/index.html` (add event processing and combat UI to `<script>`)

This wires up the event pipeline: toasts for passive events, modals for gun/coat offers, combat modal for cops, and game over screen.

- [ ] **Step 1: Add event processing function**

Insert before `// --- Boot ---`:

```javascript
// --- Event Processing ---
let pendingEvents = [];
let combatCops = 0;

function processEvents(events) {
  pendingEvents = [...events];
  processNextEvent();
}

function processNextEvent() {
  if (pendingEvents.length === 0) {
    checkGameOver();
    return;
  }

  const ev = pendingEvents.shift();

  if (ev.type === 'cops') {
    combatCops = ev.data;
    openCombatModal();
    return;
  }

  if (ev.type === 'gun_offer') {
    if (state.cash >= 400) {
      document.getElementById('offer-text').textContent = ev.message;
      document.getElementById('offer-modal').classList.add('open');
      document.getElementById('btn-offer-yes').onclick = () => {
        state.cash -= 400;
        state.guns += 1;
        document.getElementById('offer-modal').classList.remove('open');
        showToast('You bought a gun!');
        render();
        processNextEvent();
      };
      document.getElementById('btn-offer-no').onclick = () => {
        document.getElementById('offer-modal').classList.remove('open');
        processNextEvent();
      };
      return;
    } else {
      showToast("Can't afford a gun ($400).");
    }
  }

  if (ev.type === 'coat_offer') {
    if (state.cash >= 200) {
      document.getElementById('offer-text').textContent = ev.message;
      document.getElementById('offer-modal').classList.add('open');
      document.getElementById('btn-offer-yes').onclick = () => {
        state.cash -= 200;
        state.capacity += 10;
        document.getElementById('offer-modal').classList.remove('open');
        showToast('Trench coat! +10 carrying capacity.');
        render();
        processNextEvent();
      };
      document.getElementById('btn-offer-no').onclick = () => {
        document.getElementById('offer-modal').classList.remove('open');
        processNextEvent();
      };
      return;
    } else {
      showToast("Can't afford a trench coat ($200).");
    }
  }

  // Passive events: mugger, find_goods, price_spike, price_crash
  showToast(ev.message, 3000);
  setTimeout(() => processNextEvent(), 1500);
}
```

- [ ] **Step 2: Add combat modal logic**

Insert after processNextEvent:

```javascript
// --- Combat ---
function openCombatModal() {
  const modal = document.getElementById('combat-modal');
  const log = document.getElementById('combat-log');
  log.innerHTML = '';
  updateCombatUI();
  modal.classList.add('open');
}

function updateCombatUI() {
  document.getElementById('combat-info').textContent = `Cops: ${combatCops} | HP: ${state.health}`;
  const fightBtn = document.getElementById('btn-fight');
  const runBtn = document.getElementById('btn-run');
  const doneBtn = document.getElementById('btn-combat-done');
  const combatOver = combatCops <= 0 || state.health <= 0;

  fightBtn.style.display = combatOver ? 'none' : '';
  runBtn.style.display = combatOver ? 'none' : '';
  doneBtn.style.display = combatOver ? '' : 'none';
  fightBtn.disabled = state.guns <= 0;
}

function addCombatLog(msg) {
  const log = document.getElementById('combat-log');
  const p = document.createElement('p');
  p.textContent = '> ' + msg;
  p.style.margin = '4px 0';
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

document.getElementById('btn-fight').addEventListener('click', () => {
  const result = combatRound(state, combatCops, 'fight');
  combatCops = result.remaining;
  addCombatLog(result.message);
  updateCombatUI();
  render();
});

document.getElementById('btn-run').addEventListener('click', () => {
  const result = combatRound(state, combatCops, 'run');
  combatCops = result.remaining;
  addCombatLog(result.message);
  if (result.escaped) {
    combatCops = 0;
  }
  updateCombatUI();
  render();
});

document.getElementById('btn-combat-done').addEventListener('click', () => {
  document.getElementById('combat-modal').classList.remove('open');
  render();
  processNextEvent();
});
```

- [ ] **Step 3: Add game over check and modal**

Insert after combat code:

```javascript
// --- Game Over ---
function checkGameOver() {
  if (state.health > 0 && state.day <= 30) return;

  const score = state.cash + state.bank - state.debt;
  const title = state.health <= 0 ? "YOU'RE DEAD!" : "GAME OVER — 30 days are up!";

  document.getElementById('gameover-title').textContent = title;
  document.getElementById('gameover-score').textContent =
    `  Cash:  ${formatMoney(state.cash)}\n` +
    `  Bank:  ${formatMoney(state.bank)}\n` +
    `  Debt: -${formatMoney(state.debt)}\n` +
    `  ${'─'.repeat(20)}\n` +
    `  Score: ${formatMoney(score)}`;
  document.getElementById('gameover-modal').classList.add('open');
}

document.getElementById('btn-play-again').addEventListener('click', () => {
  document.getElementById('gameover-modal').classList.remove('open');
  state = createState();
  prices = generatePrices();
  priceHighlights = {};
  openPanel = null;
  render();
});
```

- [ ] **Step 4: Verify full event flow**

Open `http://localhost:8000`. Play through several turns:
- Travel repeatedly. Eventually events should trigger:
  - Toast messages for mugger, found goods, price spikes/crashes
  - Gun offer modal with YES/NO
  - Coat offer modal with YES/NO
  - Combat modal with FIGHT/RUN buttons, log messages, and dismiss
- Play until day 30 → game over screen shows score and Play Again works
- If health reaches 0 in combat → "YOU'RE DEAD!" game over

- [ ] **Step 5: Commit**

```bash
git add web/index.html
git commit -m "feat(pwa): add event processing, combat, offers, and game over"
```

---

### Task 10: Polish and Final Verification

**Files:**
- Modify: `web/index.html` (minor tweaks)
- Modify: `web/sw.js` (ensure cache version is correct)
- Modify: `CLAUDE.md` (add PWA run instructions)

- [ ] **Step 1: Add title screen**

Add a title overlay that shows on first load. Insert this HTML just inside `<body>`, before the header:

```html
<!-- Title screen -->
<div id="title-modal" class="modal-overlay open">
  <div class="modal" style="text-align: center;">
    <h2 style="font-size: 20px; margin-bottom: 8px;">DOPE WARS</h2>
    <p>Buy low. Sell high. Don't get killed.</p>
    <p style="margin-top: 12px; color: var(--dim);">30 days to make your fortune</p>
    <button class="btn" id="btn-start" style="margin-top: 16px;">START</button>
  </div>
</div>
```

Add this to the script, before `render()` in the boot section:

```javascript
document.getElementById('btn-start').addEventListener('click', () => {
  document.getElementById('title-modal').classList.remove('open');
});
```

- [ ] **Step 2: Disable main UI during modals**

Add a helper to prevent interaction with the market/actions while a modal is open. Add this CSS:

```css
body.modal-active #market,
body.modal-active #actions,
body.modal-active .panel {
  pointer-events: none;
  opacity: 0.3;
}
```

Update each modal open to add `document.body.classList.add('modal-active')` and each close to remove it. Add these two helper functions:

```javascript
function lockUI() { document.body.classList.add('modal-active'); }
function unlockUI() { document.body.classList.remove('modal-active'); }
```

Then add `lockUI()` calls when opening buy-modal, sell-modal, offer-modal, combat-modal, gameover-modal, and `unlockUI()` calls when closing them.

- [ ] **Step 3: Update CLAUDE.md with PWA instructions**

Add to the "Running" section in `CLAUDE.md`:

```markdown
### PWA (web version)

```bash
cd web && python3 -m http.server 8000
```

Open `http://localhost:8000` on your phone (same network) or desktop browser. On mobile, use "Add to Home Screen" to install as an app.
```

- [ ] **Step 4: Full playthrough test**

Open `http://localhost:8000`. Complete a full game:
1. Title screen → START
2. Buy some goods
3. Travel (JET) — verify day advances, interest applies, events fire
4. Sell goods at higher prices
5. Use bank to deposit/withdraw
6. Repay some debt
7. Handle combat encounter (fight and run)
8. Accept a gun offer, accept a coat offer
9. Play to day 30 → game over → Play Again
10. Verify on mobile viewport (DevTools device mode, ~375px wide)

- [ ] **Step 5: Commit**

```bash
git add web/index.html web/sw.js CLAUDE.md
git commit -m "feat(pwa): add title screen, UI polish, and docs"
```
