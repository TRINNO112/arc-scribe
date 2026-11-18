# ✦ ARC SCRIBE • BRAND IDENTITY & MATHEMATICAL DESIGN SYSTEM
### *The Arcane Novelist Atelier & Theatrical Enactment Studio*
**Document Version:** 1.0.0  
**Specification Level:** Definitive Engineering & Architectural Standard  
**Target Environment:** Local-First Web Audio, Desktop Command Deck & Mobile Smartphone Recording  
**File Location:** `d:\Trinno\arc-scribe\docs\BRAND_AND_DESIGN_SYSTEM.md`

---

## 1. Executive Philosophy & Brand DNA

Arc Scribe is not a generic voice transcription tool; it is a dedicated **Atelier for Novelist Duos and Playwrights**. Built specifically for two collaborators (often brothers or co-authors) acting out high-tension character dialogues in real time, the interface bridges two distinct worlds:

1. **The Theatrical Recording Chamber (Live Acoustic Performance):** Immediate, high-contrast, tactile, thumb-reachable, zero-cognitive-overload controls that never mis-trigger during heated enactment.
2. **The Arcane Editorial Atelier (Literary Scribing):** A distraction-free, print-inspired reading and editing environment where raw spoken drama crystallizes into polished novel prose.

### 1.1 Synthesis of Design Foundations (From `awesome-design-skills`)

Our design system extracts and harmonizes eight foundational design traditions:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                ARC SCRIBE DESIGN SYNTHESIS                             │
├────────────────────────────┬─────────────────────────────┬─────────────────────────────┤
│ 1. EDITORIAL & REFINED     │ 2. CLAUDE & PAPER           │ 3. DRAMATIC & NEOBRUTALISM  │
│ • Gelasio / Cinzel Serifs  │ • Warm Slate & Inkwell Base │ • Theatrical High-Contrast  │
│ • 65–75ch Line Length      │ • Disciplined Color Budget  │ • Crisp Hairline Borders    │
│ • 1.618 Golden Line Height │ • Tactile Manuscript Feel   │ • Zero Blurry Radial Blobs  │
├────────────────────────────┴─────────────────────────────┴─────────────────────────────┤
│ 4. STORYTELLING & BENTO                                                                │
│ • Narrative Flow: Spoken Enactment → Turn Diarization → Chapter Prose Draft            │
│ • Modular Bento Containers: Setup Deck | Recording Sanctuary | Output Studio           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

- **`editorial` & `refined`:** Sophisticated typographic hierarchy, generous leading, and magazine-grade prose rendering optimized for long-form reading comfort.
- **`claude` & `paper`:** A research-journal and parchment philosophy. The interface lives on a slate-and-ink continuum with an intentionally tiny chromatic budget: high-contrast typography and structural lines carry the visual weight rather than gratuitous decorations.
- **`dramatic` & `neobrutalism`:** Stage-lighting metaphor with tactile mechanical feedback. Interfaces feature crisp 1px borders, deep elevation contrast, and physically reassuring interactive states, completely rejecting nebulous, low-contrast neon radial blobs.
- **`storytelling` & `bento`:** A structured narrative workflow chunked into modular cards: Scene & Speaker Configuration (Left), Recording Deck (Center), and Multi-Tab Output Studio (Right).

---

## 2. Mathematical Design Ratios & Color Harmony

Every visual decision in Arc Scribe is governed by mathematical laws rather than arbitrary aesthetic whim.

### 2.1 The 60-30-10 Color Harmonization Rule

The canvas follows the classical interior and stage lighting ratio:

$$\text{Canvas Budget} = 60\% \text{ Base} + 30\% \text{ Structure} + 10\% \text{ Accent}$$

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE 60-30-10 CHROMATIC DISTRIBUTION                      │
├─────────────────────────────────────────────────┬──────────────────────────┬───────────┤
│ 60% DOMINANT CANVAS                             │ 30% STRUCTURAL INK       │ 10% ACCENT│
│ Deep Obsidian Inkwell & Void                    │ Slate Vellum & Surfaces  │ High-Intent│
│ #07090E / #0B0F19                               │ #151D2A / #1E293B / #334 │ Ember/Iris│
│ Reduces eye fatigue during dark night enactments│ Structural cards, borders│ Live State│
└─────────────────────────────────────────────────┴──────────────────────────┴───────────┘
```

1. **60% Dominant Base / Canvas (Obsidian Void):**
   - Palette: `slate-950` (`#07090E`) to `slate-900` (`#0F172A`).
   - Purpose: Absorbs ambient glare in dimly lit writing chambers, eliminates eye strain during nocturnal roleplay, and creates infinite visual depth.
2. **30% Structural Secondary / Surface & Architecture (Slate & Vellum):**
   - Palette: `slate-800` (`#1E293B`), `slate-700` (`#334155`), and `slate-200` (`#E2E8F0` text).
   - Purpose: Forms the physical cards, modular boundaries, subtle dividers, and readable text surfaces.
3. **10% High-Intent Chromatic Accents (Theatrical Punctuation):**
   - Palette:
     - **Theatrical Amber (`#F59E0B`):** Speaker 1 Anchor & Primary System Commitments.
     - **Arcane Amethyst (`#A78BFA`):** Speaker 2 Anchor & Counterpart Attributions.
     - **Theatrical Crimson (`#EF4444`):** Active Recording Pulse & Destructive Safeguards.
     - **Emerald Scribe (`#10B981`):** Acoustic Calibration Vault Lock & IndexedDB Sync.
   - Purpose: Strictly reserved for functional signaling. Frivolous background gradients and aimless glowing circles are strictly prohibited.

---

### 2.2 The Golden Ratio ($\phi = 1.6180339887...$) System

All scales in Arc Scribe—typography, vertical rhythm, grid proportions, and container geometries—are derived directly from $\phi$.

#### 2.2.1 Modular Typographic Scale

Using base font size $f_0 = 16\text{px}$ (1.000rem) with a Golden Ratio step ratio $r = \sqrt{\phi} \approx 1.272$ for sub-steps and $\phi \approx 1.618$ for major milestones:

$$f_n = f_0 \times r^n \quad \text{where } r \in \{1.2720, 1.6180\}$$

| Step | Token Name | Size (px) | Size (rem) | Ratio Formula | Mathematical Line-Height | Target Application |
|:---|:---|:---|:---|:---|:---|:---|
| **$f_{-2}$** | `--text-xs` | $9.88 \approx 10\text{px}$ | 0.625rem | $16 / \phi$ | $1.382$ ($14\text{px}$) | Audio sampling rate tags, Hz indicators |
| **$f_{-1}$** | `--text-sm` | $12.36 \approx 12\text{px}$ | 0.772rem | $16 / \sqrt{\phi}$ | $1.414$ ($17\text{px}$) | Speaker pills, timecodes, status badges |
| **$f_0$** | `--text-base` | **$16.00\text{px}$** | **1.000rem** | **Baseline Unit** | **$1.618$ ($26\text{px}$)** | **Prose Reader body, verbatim dialogue lines** |
| **$f_1$** | `--text-md` | $20.35 \approx 20\text{px}$ | 1.272rem | $16 \times \sqrt{\phi}$ | $1.414$ ($28\text{px}$) | Card headers, form input values |
| **$f_2$** | `--text-lg` | $25.89 \approx 26\text{px}$ | 1.618rem | $16 \times \phi$ | $1.272$ ($33\text{px}$) | Section headers, panel titles |
| **$f_3$** | `--text-xl` | $32.93 \approx 33\text{px}$ | 2.058rem | $16 \times \phi \times \sqrt{\phi}$ | $1.236$ ($41\text{px}$) | Chapter title, modal headlines |
| **$f_4$** | `--text-2xl` | $41.89 \approx 42\text{px}$ | 2.618rem | $16 \times \phi^2$ | $1.168$ ($49\text{px}$) | Studio brand crest typography |
| **$f_5$** | `--text-hero`| $53.28 \approx 54\text{px}$ | 3.375rem | $16 \times \phi^{2.5}$ | $1.000$ ($54\text{px}$) | Theatrical countdown / Live recording timer |

#### 2.2.2 Fibonacci Spatial Scale (8pt Baseline Harmonized)

Spacings are bound to Fibonacci subdivisions to preserve natural optical rhythm:

$$\text{Spacing Token} \in \{2\text{px}, 4\text{px}, 8\text{px}, 13\text{px}, 21\text{px}, 34\text{px}, 55\text{px}, 89\text{px}\}$$

- `--space-1` ($2\text{px}$): Hairline borders, active button depression offset.
- `--space-2` ($4\text{px}$): Sub-badge padding, tight icon margins.
- `--space-3` ($8\text{px}$): Standard inline component spacing, status dot gaps.
- `--space-4` ($13\text{px} \approx 12\text{px}$): Form input vertical padding, card inner margins.
- `--space-5` ($21\text{px} \approx 20\text{px}$): Panel interior padding, button lateral padding.
- `--space-6` ($34\text{px} \approx 32\text{px}$): Major section gutters, grid gaps.
- `--space-7` ($55\text{px} \approx 56\text{px}$): Hero component isolation, mobile deck bottom clearance.
- `--space-8` ($89\text{px} \approx 88\text{px}$): Global layout boundary padding on ultrawide displays.

#### 2.2.3 Studio Layout Grid Golden Ratios

On desktop ($W = 1480\text{px}$ max), the 3-panel layout partitions according to reciprocal Golden sections:

$$\frac{\text{Center Sanctuary } (565\text{px}) + \text{Output Studio } (565\text{px})}{\text{Command Deck } (350\text{px})} = \frac{1130}{350} \approx 3.23 \approx 2 \times 1.618$$

$$\text{Viewport Reading Aspect Ratio} = \frac{\text{Width}}{\text{Height}} = 1.618 : 1 \quad \text{(Golden Window)}$$

---

### 2.3 Mathematical WCAG 2.2 AA / AAA Contrast Verification

WCAG 2.2 contrast compliance is evaluated using exact relative luminance ($L$):

$$L = 0.2126 \cdot R_{\text{lin}} + 0.7152 \cdot G_{\text{lin}} + 0.0722 \cdot B_{\text{lin}}$$

$$\text{Where } C_{\text{lin}} = \begin{cases} \frac{C_{\text{sRGB}}}{12.92} & \text{if } C_{\text{sRGB}} \le 0.04045 \\ \left(\frac{C_{\text{sRGB}} + 0.055}{1.055}\right)^{2.4} & \text{if } C_{\text{sRGB}} > 0.04045 \end{cases}$$

$$\text{Contrast Ratio (CR)} = \frac{L_1 + 0.05}{L_2 + 0.05} \quad (L_1 > L_2)$$

#### Rigorous Contrast Ratio Verification Table

| Foreground Token | Hex | Relative Lum ($L_1$) | Background Surface | BG Lum ($L_2$) | Computed Ratio | WCAG 2.2 AA (4.5:1 / 3:1) | WCAG 2.2 AAA (7:1 / 4.5:1) |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Text Primary** | `#F1F5F9` | $0.898$ | Canvas Void (`#07090E`) | $0.0055$ | **17.97 : 1** | **PASS** (Normal Text) | **PASS** (Normal Text) |
| **Text Primary** | `#F1F5F9` | $0.898$ | Surface Card (`#161D2B`) | $0.0132$ | **15.40 : 1** | **PASS** (Normal Text) | **PASS** (Normal Text) |
| **Text Muted** | `#94A3B8` | $0.364$ | Canvas Void (`#07090E`) | $0.0055$ | **7.68 : 1** | **PASS** (Normal Text) | **PASS** (Normal Text) |
| **Text Muted** | `#94A3B8` | $0.364$ | Surface Card (`#161D2B`) | $0.0132$ | **6.58 : 1** | **PASS** (Normal Text) | **PASS** (Large/UI) |
| **Amber (Speaker 1)** | `#F59E0B` | $0.435$ | Canvas Void (`#07090E`) | $0.0055$ | **9.16 : 1** | **PASS** (Normal Text) | **PASS** (Normal Text) |
| **Amber (Speaker 1)** | `#F59E0B` | $0.435$ | Surface Card (`#161D2B`) | $0.0132$ | **7.86 : 1** | **PASS** (Normal Text) | **PASS** (Normal Text) |
| **Amethyst (Spk 2)** | `#A78BFA` | $0.334$ | Canvas Void (`#07090E`) | $0.0055$ | **7.23 : 1** | **PASS** (Normal Text) | **PASS** (Normal Text) |
| **Amethyst (Spk 2)** | `#A78BFA` | $0.334$ | Surface Card (`#161D2B`) | $0.0132$ | **6.21 : 1** | **PASS** (Normal Text) | **PASS** (Large/UI) |
| **Crimson (Rec)** | `#EF4444` | $0.239$ | Canvas Void (`#07090E`) | $0.0055$ | **5.23 : 1** | **PASS** (Normal Text) | **PASS** (Large/UI) |
| **Emerald (Valid)** | `#10B981` | $0.392$ | Canvas Void (`#07090E`) | $0.0055$ | **8.18 : 1** | **PASS** (Normal Text) | **PASS** (Normal Text) |

*All foundational body copy text exceeds WCAG 2.2 AAA standard (7.0:1). Interactive controls and status tags strictly surpass AA thresholds.*

---

## 3. Comprehensive Color Coordinate Architecture (50–950 Ramps)

Every palette is mathematically expressed across all color spaces: **Hexadecimal, sRGB HSL, and modern Perceptually Uniform OKLCH** (`oklch(Lightness Chroma Hue)`).

### 3.1 Palette 1: Slate Canvas & Obsidian Inkwell (60% Base / 30% Structural)
*Neutral backbone providing deep manuscript contrast without eye fatigue.*

| Step | Hex | HSL Coordinates | OKLCH Coordinates | Semantic System Token | Application Rules |
|:---|:---|:---|:---|:---|:---|
| **50** | `#F8FAFC` | `hsl(210, 40%, 98%)` | `oklch(0.984 0.003 247.9)` | `--color-slate-50` | Highlight text, selected prose phrases |
| **100** | `#F1F5F9` | `hsl(210, 40%, 96%)` | `oklch(0.968 0.007 247.9)` | `--color-slate-100` | Primary readable prose & dialogue text |
| **200** | `#E2E8F0` | `hsl(214, 32%, 91%)` | `oklch(0.929 0.013 255.5)` | `--color-slate-200` | High-contrast secondary labels |
| **300** | `#CBD5E1` | `hsl(213, 27%, 84%)` | `oklch(0.869 0.020 252.9)` | `--color-slate-300` | Secondary metadata text |
| **400** | `#94A3B8` | `hsl(215, 20%, 65%)` | `oklch(0.711 0.035 256.8)` | `--color-slate-400` | Muted timecodes, inactive tab icons |
| **500** | `#64748B` | `hsl(215, 16%, 47%)` | `oklch(0.554 0.041 257.4)` | `--color-slate-500` | Subdued placeholder text |
| **600** | `#475569` | `hsl(215, 19%, 35%)` | `oklch(0.446 0.037 257.3)` | `--color-slate-600` | Subtle hairline dividers |
| **700** | `#334155` | `hsl(215, 25%, 27%)` | `oklch(0.372 0.039 257.3)` | `--color-slate-700` | Primary component borders |
| **800** | `#1E293B` | `hsl(217, 33%, 17%)` | `oklch(0.279 0.037 260.0)` | `--color-slate-800` | Elevated card surfaces, modal headers |
| **900** | `#0F172A` | `hsl(222, 47%, 11%)` | `oklch(0.208 0.040 265.8)` | `--color-slate-900` | Studio panel containers, deep recessed wells |
| **950** | `#07090E` | `hsl(223, 33%, 4%)` | `oklch(0.140 0.012 265.8)` | `--color-slate-950` | Primary viewport background (Canvas Void) |

---

### 3.2 Palette 2: Theatrical Amber (Speaker 1 Anchor & Primary Action)
*Warm, resonant theatrical lantern flame. Identifies Author 1 / Protagonist.*

| Step | Hex | HSL Coordinates | OKLCH Coordinates | Semantic System Token | Application Rules |
|:---|:---|:---|:---|:---|:---|
| **50** | `#FFFBEB` | `hsl(48, 100%, 96%)` | `oklch(0.987 0.021 95.3)` | `--color-amber-50` | Amber badge foreground in light mode |
| **100** | `#FEF3C7` | `hsl(48, 96%, 89%)` | `oklch(0.962 0.058 95.6)` | `--color-amber-100` | Active selection text in amber blocks |
| **200** | `#FDE68A` | `hsl(48, 97%, 77%)` | `oklch(0.924 0.115 95.7)` | `--color-amber-200` | Speaker 1 hover state label |
| **300** | `#FCD34D` | `hsl(46, 97%, 65%)` | `oklch(0.879 0.153 91.6)` | `--color-amber-300` | Speaker 1 character name highlights |
| **400** | `#FBBF24` | `hsl(43, 96%, 56%)` | `oklch(0.837 0.164 84.4)` | `--color-amber-400` | Speaker 1 pill border & icon glow |
| **500** | `#F59E0B` | `hsl(38, 92%, 50%)` | `oklch(0.769 0.165 70.1)` | `--color-amber-500` | **Core Brand Accent & Speaker 1 Spine** |
| **600** | `#D97706` | `hsl(32, 95%, 44%)` | `oklch(0.666 0.157 58.3)` | `--color-amber-600` | Primary CTA button background |
| **700** | `#B45309` | `hsl(26, 90%, 37%)` | `oklch(0.555 0.146 49.0)` | `--color-amber-700` | Primary CTA active pressed state |
| **800** | `#92400E` | `hsl(23, 82%, 31%)` | `oklch(0.473 0.125 46.2)` | `--color-amber-800` | Subdued amber card border |
| **900** | `#78350F` | `hsl(22, 78%, 26%)` | `oklch(0.414 0.105 45.9)` | `--color-amber-900` | Speaker 1 card background wash (10% alpha) |
| **950** | `#451A03` | `hsl(21, 92%, 14%)` | `oklch(0.279 0.074 45.6)` | `--color-amber-950` | Deepest amber tint layer |

---

### 3.3 Palette 3: Arcane Amethyst (Speaker 2 Anchor & Counterpart Action)
*Deep, contemplative arcane violet. Identifies Author 2 / Counterpart.*

| Step | Hex | HSL Coordinates | OKLCH Coordinates | Semantic System Token | Application Rules |
|:---|:---|:---|:---|:---|:---|
| **50** | `#F5F3FF` | `hsl(250, 100%, 98%)` | `oklch(0.969 0.016 293.8)`| `--color-amethyst-50` | Amethyst badge light text |
| **100** | `#EDE9FE` | `hsl(251, 91%, 95%)` | `oklch(0.943 0.028 294.6)`| `--color-amethyst-100`| Highlighted speaker 2 phrase |
| **200** | `#DDD6FE` | `hsl(250, 95%, 92%)` | `oklch(0.894 0.055 293.3)`| `--color-amethyst-200`| Speaker 2 secondary label |
| **300** | `#C4B5FD` | `hsl(252, 95%, 85%)` | `oklch(0.811 0.101 293.6)`| `--color-amethyst-300`| Speaker 2 character name highlights |
| **400** | `#A78BFA` | `hsl(255, 92%, 76%)` | `oklch(0.709 0.159 293.5)`| `--color-amethyst-400`| **Speaker 2 Core Pill & Card Spine** |
| **500** | `#8B5CF6` | `hsl(258, 90%, 66%)` | `oklch(0.606 0.219 292.7)`| `--color-amethyst-500`| Speaker 2 active highlight border |
| **600** | `#7C3AED` | `hsl(262, 83%, 58%)` | `oklch(0.541 0.247 293.0)`| `--color-amethyst-600`| Counterpart CTA button background |
| **700** | `#6D28D9` | `hsl(263, 70%, 50%)` | `oklch(0.491 0.241 292.6)`| `--color-amethyst-700`| Counterpart button active pressed state |
| **800** | `#5B21B6` | `hsl(263, 69%, 42%)` | `oklch(0.432 0.211 292.8)`| `--color-amethyst-800`| Subdued amethyst card boundary |
| **900** | `#4C1D95` | `hsl(264, 67%, 35%)` | `oklch(0.380 0.178 293.7)`| `--color-amethyst-900`| Speaker 2 card background wash (10% alpha) |
| **950** | `#2E1065` | `hsl(261, 73%, 23%)` | `oklch(0.283 0.135 291.1)`| `--color-amethyst-950`| Deepest amethyst tint layer |

---

### 3.4 Palette 4: Theatrical Crimson (Recording Pulse & Destructive Safeguards)
*High-salience urgency signal. Dedicated exclusively to active audio recording.*

| Step | Hex | HSL Coordinates | OKLCH Coordinates | Semantic System Token | Application Rules |
|:---|:---|:---|:---|:---|:---|
| **50** | `#FEF2F2` | `hsl(0, 86%, 97%)` | `oklch(0.971 0.013 17.4)` | `--color-crimson-50` | Emergency dialog background light |
| **100** | `#FEE2E2` | `hsl(0, 93%, 94%)` | `oklch(0.936 0.031 17.7)` | `--color-crimson-100` | Warning banner text |
| **200** | `#FECACA` | `hsl(0, 96%, 89%)` | `oklch(0.885 0.059 18.3)` | `--color-crimson-200` | Alert border secondary |
| **300** | `#FCA5A5` | `hsl(0, 94%, 82%)` | `oklch(0.808 0.103 19.6)` | `--color-crimson-300` | Recording badge pulse ring |
| **400** | `#F87171` | `hsl(0, 91%, 71%)` | `oklch(0.711 0.166 22.2)` | `--color-crimson-400` | Audio visualizer clipping warning bar |
| **500** | `#EF4444` | `hsl(0, 84%, 60%)` | `oklch(0.637 0.208 25.3)` | `--color-crimson-500` | **Active Recording State & Live Timer** |
| **600** | `#DC2626` | `hsl(0, 72%, 51%)` | `oklch(0.577 0.215 27.3)` | `--color-crimson-600` | Stop recording button background |
| **700** | `#B91C1C` | `hsl(0, 74%, 42%)` | `oklch(0.505 0.190 27.5)` | `--color-crimson-700` | Destructive button active pressed state |
| **800** | `#991B1B` | `hsl(0, 70%, 35%)` | `oklch(0.444 0.161 26.9)` | `--color-crimson-800` | Recording border perimeter line |
| **900** | `#7F1D1D` | `hsl(0, 63%, 31%)` | `oklch(0.396 0.133 25.7)` | `--color-crimson-900` | Theatrical record deck overlay tint |
| **950** | `#450A0A` | `hsl(0, 75%, 15%)` | `oklch(0.258 0.089 26.0)` | `--color-crimson-950` | Recessed audio clipping channel |

---

### 3.5 Palette 5: Emerald Scribe (System Sync & Calibration Lock)
*Precision verification signal. Confirms speaker enrollment & local storage safety.*

| Step | Hex | HSL Coordinates | OKLCH Coordinates | Semantic System Token | Application Rules |
|:---|:---|:---|:---|:---|:---|
| **50** | `#ECFDF5` | `hsl(152, 81%, 96%)` | `oklch(0.979 0.021 166.1)`| `--color-emerald-50` | Success banner light |
| **100** | `#D1FAE5` | `hsl(149, 80%, 90%)` | `oklch(0.950 0.051 163.1)`| `--color-emerald-100`| IndexedDB backup confirmed pill |
| **200** | `#A7F3D0` | `hsl(152, 76%, 80%)` | `oklch(0.905 0.089 164.2)`| `--color-emerald-200`| Safe storage badge text |
| **300** | `#6EE7B7` | `hsl(156, 72%, 67%)` | `oklch(0.845 0.130 165.0)`| `--color-emerald-300`| Calibration progress indicator bar |
| **400** | `#34D399` | `hsl(158, 64%, 52%)` | `oklch(0.773 0.153 163.2)`| `--color-emerald-400`| Gemini API online status indicator |
| **500** | `#10B981` | `hsl(160, 84%, 39%)` | `oklch(0.696 0.149 162.5)`| `--color-emerald-500`| **Speaker Calibrated & Vault Locked** |
| **600** | `#059669` | `hsl(161, 94%, 30%)` | `oklch(0.596 0.127 163.2)`| `--color-emerald-600`| Export ready action badge |
| **700** | `#047857` | `hsl(163, 94%, 24%)` | `oklch(0.508 0.105 165.6)`| `--color-emerald-700`| Calibration completed card border |
| **800** | `#065F46` | `hsl(163, 88%, 20%)` | `oklch(0.432 0.086 166.9)`| `--color-emerald-800`| Deep status background container |
| **900** | `#064E3B` | `hsl(164, 86%, 16%)` | `oklch(0.378 0.073 168.9)`| `--color-emerald-900`| Scribe success pill wash |
| **950** | `#022C22` | `hsl(166, 91%, 9%)` | `oklch(0.262 0.049 172.6)`| `--color-emerald-950`| Sibling enrollment verified base |

---

## 4. Laws of UX Grounding & Interaction Architecture

The UX of Arc Scribe is engineered specifically for active authors engaged in passionate, physical performance where attention is divided between creative immersion and recording mechanics.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              LAWS OF UX COGNITIVE MAPPING                              │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ FITTS'S LAW              │ HICK'S LAW                  │ MILLER'S LAW & CHUNKING       │
│ • Large 56px Touch Zones │ • 3-Field Instant Setup     │ • 5–7 Line Dialogue Turns     │
│ • Primary Thumb Sector   │ • Pre-Populated Defaults    │ • 3–5 Narrative Scene Beats   │
│ • Isolated Pause Control │ • Modal Vault Progressive   │ • Integrated Turn Anatomy     │
├──────────────────────────┴─────────────────────────────┴───────────────────────────────┤
│ VON RESTORFF EFFECT (ISOLATION PRINCIPLE)                                              │
│ • Active Recording dims background UI by 40%                                           │
│ • Live crimson timer & audio pulse creates unmistakable recording salience             │
│ • Zero "Did I hit record?" catastrophic anxiety                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Fitts's Law ($T = a + b \log_2(1 + D/W)$)

In physical enactment, authors pace across the room, gesticulate, and hold their mobile phone with one hand. Fitts's Law dictates that target acquisition time is a function of distance ($D$) and target size ($W$).

1. **Massive Primary Touch Targets:**
   - The primary `Start Enactment` / `Stop & Scribe` button has a minimum height of **$56\text{px}$** and full container width on mobile ($W \ge 320\text{px}$), far exceeding the standard $48\text{px}$ touch target requirement.
2. **Thumb-Zone Optimization (Bottom 35% Viewport):**
   - All critical recording controls are positioned in the bottom $35\%$ of the mobile viewport, within the natural sweep radius of the user's thumb.
3. **Accidental Press Elimination via Spatial Distance ($D$):**
   - Destructive actions (`Reset Take`, `Discard Audio`) are separated from the primary recording button by a minimum distance $D \ge 34\text{px}$ and require an explicit double-tap confirmation pattern.

```css
/* Fitts's Law Enforced Mobile Action Button */
.theatrical-controls .record-btn {
  min-height: 56px;
  min-width: 160px;
  padding: 16px 28px;
  touch-action: manipulation;
  border-radius: var(--radius-md);
  user-select: none;
}
```

---

### 4.2 Hick's Law ($T = b \log_2(n + 1)$)

Hick's Law states that decision time increases logarithmically with the number and complexity of choices ($n$). A writer about to enact a dramatic fight scene must not face a wall of 20 form inputs.

1. **Three-Field Frictionless Setup:**
   - The setup deck surfaces only 3 primary decisions before recording:
     1. Scene / Chapter Title (`#arcTitleInput`)
     2. Setting Context (`#sceneContextInput`)
     3. Two Character Identity Cards (`#spk1Char`, `#spk2Char`)
2. **Smart Defaults Over Empty States:**
   - All fields initialize with evocative, pre-filled scenario defaults ("The Midnight Confrontation", "Lord Vane", "Ethan") so the author can literally click `Start Enactment` in under 3 seconds.
3. **Progressive Disclosure:**
   - Advanced settings (Acoustic Noise Suppress Bypass, Gemini API Model Selection, Sibling Audio Formant Calibration) are housed inside dedicated, non-intrusive modal vaults opened only when needed.

---

### 4.3 Miller's Law & Narrative Chunking ($7 \pm 2$)

Working memory holds between 5 and 9 items. Unprocessed speech transcripts quickly degrade into an incomprehensible wall of text.

1. **Dialogue Turn Chunking:**
   - Raw audio stream is segmented into discreet character turns. Each card bundles speaker identity, emotional inflection, spoken dialogue, and physical stage action into a single cognitive chunk.
2. **Scene Beats Structuring (Rule of 3–5):**
   - The dramatic progression is automatically analyzed into 3 to 5 narrative beats:
     - Beat 1: *Status Quo & Spatial Entry*
     - Beat 2: *Inciting Friction / Disputed Claim*
     - Beat 3: *The Escalation / Rising Tension*
     - Beat 4: *The Dramatic Climax / Revelation*
     - Beat 5: *Lingering Consequence / Transition*

---

### 4.4 Von Restorff Effect (Isolation Principle)

When multiple similar stimuli are present, the one that differs from the rest will be remembered and noticed. In audio recording, the most catastrophic failure is an author believing they are recording when they are not.

1. **State Isolation Protocol:**
   - When recording begins:
     - Background studio panels drop from $100\%$ to $60\%$ opacity with a $300\text{ms}$ smooth transition (`--ease-spring`).
     - Ambient decorative lighting dims completely.
     - The visualizer container illuminates with a razor-sharp $2\text{px}$ `crimson-500` perimeter border.
     - The high-contrast recording timer flashes a high-salience crimson dot at exactly $1.0\text{Hz}$.
2. **Zero Ambiguity:**
   - The user cannot mistake standby for active recording, even from 10 feet away across the studio floor.

---

### 4.5 Doherty Threshold (<400ms Feedback) & Postel's Law

1. **Instantaneous Acoustic Feedback (<16ms):**
   - Web Audio API canvas visualizer renders frequency spectrum data at $60\text{fps}$ (<16.6ms per frame), confirming immediately that the smartphone microphone is capturing sound.
2. **Resilient Local Persistence (Postel's Law - Be liberal in what you accept, conservative in what you send):**
   - Audio chunks stream into browser `IndexedDB` every 3000ms. If the smartphone browser closes or Wi-Fi drops, the local take is preserved and can be re-transcribed with zero data loss.

---

## 5. Concrete Component Anatomy & Anti-Patterns

### 5.1 Screenplay Dialogue Cards (Speaker 1 vs Speaker 2 Distinction)

#### The Anti-Pattern (Forbidden)
- ❌ **Fuzzy Glowing Blobs:** Blurry `box-shadow: 0 0 40px rgba(...)` that washes out text and looks like a generic web3 template.
- ❌ **Generic Chat Bubbles:** Rounded speech balloons that look like WhatsApp or SMS messages, destroying the theatrical stage-script atmosphere.
- ❌ **Low-Contrast Gray Pills:** Unreadable gray-on-dark badges that fail WCAG 2.2 AA.

#### The Scribe Architecture (Required)
- ✅ **Calibrated Architectural Spine:** A razor-sharp $2\text{px}$ vertical border line on the card's leading edge:
  - Speaker 1: `border-left: 2px solid var(--color-amber-500)`
  - Speaker 2: `border-left: 2px solid var(--color-amethyst-400)`
- ✅ **Editorial Monospace Metadata:** Speaker tag and timecode rendered in uppercase `JetBrains Mono` at $12\text{px}$ with $+1.2\text{px}$ tracking.
- ✅ **Emotional Inflection Brackets:** Vocal instructions formatted in italic brackets `[whispering venomously]` in distinct muted text.
- ✅ **Stage Movement Quotes:** Physical gestures formatted as distinct indented blockquotes.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ SCREENPLAY DIALOGUE CARD ANATOMY                                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ▌ 🎭  SPEAKER 1 (LORD VANE)                                      [02:14]  [Cold & Low] │
│ ▌     [draws blade slowly from beneath velvet cloak]                                   │
│ ▌     "You came alone. Either bravery has stripped your reason, or you believe         │
│ ▌      my mercy extends beyond these walls."                                           │
└────────────────────────────────────────────────────────────────────────────────────────┘
  ▲
  2px Solid Spine (Amber for Speaker 1, Amethyst for Speaker 2)
```

```css
/* Screenplay Dialogue Card Drop-In Implementation */
.dialogue-turn-card {
  position: relative;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: var(--space-4) var(--space-5);
  margin-bottom: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  transition: border-color var(--duration-fast) var(--ease-spring);
}

.dialogue-turn-card.speaker-1 {
  border-left: 3px solid var(--color-amber-500);
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.04) 0%, transparent 60%);
}

.dialogue-turn-card.speaker-2 {
  border-left: 3px solid var(--color-amethyst-400);
  background: linear-gradient(90deg, rgba(167, 139, 250, 0.04) 0%, transparent 60%);
}

.turn-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.turn-speaker-badge {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.speaker-1 .turn-speaker-badge { color: var(--color-amber-400); }
.speaker-2 .turn-speaker-badge { color: var(--color-amethyst-300); }

.turn-inflection {
  font-family: var(--font-sans);
  font-style: italic;
  font-size: var(--text-sm);
  color: var(--color-slate-400);
}

.turn-stage-direction {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-slate-400);
  padding-left: var(--space-3);
  border-left: 1px solid var(--color-slate-700);
  margin: var(--space-1) 0;
}

.turn-dialogue-body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--line-height-dialogue);
  color: var(--color-slate-100);
}
```

---

### 5.2 Novel Chapter Prose Reader (Distraction-Free Literary Layout)

The prose reader converts spoken audio into finished, immersive fiction prose formatted to match professional trade paperbacks and digital reading terminals.

#### Typographic Architecture Rules
1. **Optimal Reading Measure (Line Length):**
   - The prose container is hard-bounded to **$65\text{ch} - 75\text{ch}$** (`max-width: 68ch; margin: 0 auto;`). Eye-tracking studies prove that lines exceeding 80 characters cause reader disorientation when returning to the next line.
2. **Golden Line-Height:**
   - Body prose strictly enforces `line-height: 1.618`.
3. **Drop Cap Geometry:**
   - Chapter openings utilize a 3-line drop cap styled in `Cinzel` serif, spanning exactly $3 \times 26\text{px} = 78\text{px}$ line height with zero top overhang.
4. **Paragraph Pacing:**
   - Fiction paragraphs utilize classical editorial styling: zero bottom margin between continuous dialogue and standard $1.5\text{em}$ first-line indent, or modern editorial paragraph blocks with $1.618\text{em}$ inter-paragraph spacing.

```css
/* Novel Chapter Prose Reader Implementation */
.prose-reader-container {
  max-width: 68ch;
  margin: 0 auto;
  padding: var(--space-6) var(--space-4);
  font-family: var(--font-serif);
  font-size: var(--text-base);
  line-height: var(--line-height-golden);
  color: var(--color-slate-100);
  letter-spacing: 0.01em;
  background: var(--bg-surface-recessed);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.prose-reader-container p {
  margin-bottom: 1.618em;
  text-align: justify;
  text-justify: inter-word;
  hyphens: auto;
}

.prose-reader-container p:first-of-type::first-letter {
  float: left;
  font-family: var(--font-serif);
  font-size: 3.85rem;
  line-height: 0.8;
  padding-top: 4px;
  padding-right: 12px;
  padding-bottom: 2px;
  color: var(--color-amber-400);
  font-weight: 800;
}
```

---

### 5.3 Mobile Theatrical Recording Deck (Tactile, High-Contrast)

Built for high-heat roleplay in mobile browsers (Android Chrome & iOS Safari).

#### Key Specifications
1. **Tactile Mechanical Feedback:**
   - Buttons employ a 1px crisp inset border and a mechanical 2px physical depression offset (`transform: translateY(2px)`) on active touch, giving writers tangible confirmation through glass.
2. **High-Contrast Frequency Visualizer:**
   - The canvas waveform uses crisp 2px vertical frequency columns with $2\text{px}$ gaps in `amber-500` or `crimson-500`, completely avoiding mushy radial blurred blobs.
3. **Screen WakeLock Shield:**
   - Visible lock status badge at top right indicates that the phone display will not sleep or interrupt an ongoing take.

```css
/* Tactile Mechanical Recording Button */
.record-btn {
  background: linear-gradient(180deg, var(--color-crimson-500) 0%, var(--color-crimson-600) 100%);
  border: 1px solid var(--color-crimson-400);
  box-shadow: 0 4px 0 var(--color-crimson-800), 0 8px 16px rgba(0, 0, 0, 0.4);
  color: #ffffff;
  font-family: var(--font-sans);
  font-weight: 700;
  border-radius: var(--radius-md);
  transition: transform var(--duration-instant), box-shadow var(--duration-instant);
}

.record-btn:active {
  transform: translateY(3px);
  box-shadow: 0 1px 0 var(--color-crimson-800), 0 2px 4px rgba(0, 0, 0, 0.4);
}
```

---

### 5.4 Sibling Voice Calibration Vault

Because two brothers sharing vocal genetics exhibit closely matching pitch and formant resonance, the calibration vault isolates speaker identities prior to recording.

#### Key Specifications
1. **Guided Dual-Card Enrollment:**
   - Two parallel acoustic enrollment chambers (Speaker 1 vs Speaker 2).
2. **15-Second Acoustic Countdown Ring:**
   - Visual SVG arc tracking exactly 15.0 seconds of baseline speech.
3. **Four Distinct Verification States:**
   - `Uncalibrated` (Muted Slate `#64748B`)
   - `Recording Acoustic Sample` (Crimson Pulse `#EF4444`)
   - `Extracting Formant Resonance` (Amber Computing `#F59E0B`)
   - `Vault Locked & Verified` (Emerald Scribe `#10B981`)

---

## 6. Complete Drop-In CSS Custom Properties (`:root`)

This block can be dropped directly into `d:\Trinno\arc-scribe\static\style.css` to align the entire application with this specification.

```css
/* ==========================================================================
   ARC SCRIBE • MATHEMATICAL DESIGN SYSTEM SPECIFICATION V1.0.0
   Derived from Golden Ratio (phi=1.618), 60-30-10 Rule, & WCAG 2.2 AAA
   ========================================================================== */

:root {
  /* ------------------------------------------------------------------------
     1. COLOR PALETTES: SLATE CANVAS (60% BASE & 30% STRUCTURAL)
     ------------------------------------------------------------------------ */
  --color-slate-50:  #F8FAFC; /* oklch(0.984 0.003 247.9) */
  --color-slate-100: #F1F5F9; /* oklch(0.968 0.007 247.9) */
  --color-slate-200: #E2E8F0; /* oklch(0.929 0.013 255.5) */
  --color-slate-300: #CBD5E1; /* oklch(0.869 0.020 252.9) */
  --color-slate-400: #94A3B8; /* oklch(0.711 0.035 256.8) */
  --color-slate-500: #64748B; /* oklch(0.554 0.041 257.4) */
  --color-slate-600: #475569; /* oklch(0.446 0.037 257.3) */
  --color-slate-700: #334155; /* oklch(0.372 0.039 257.3) */
  --color-slate-800: #1E293B; /* oklch(0.279 0.037 260.0) */
  --color-slate-900: #0F172A; /* oklch(0.208 0.040 265.8) */
  --color-slate-950: #07090E; /* oklch(0.140 0.012 265.8) - CANVAS VOID */

  /* Semantic Canvas Surfacing */
  --bg-canvas:            var(--color-slate-950);
  --bg-surface-recessed:  #0C0F17;
  --bg-surface:           #121722;
  --bg-surface-elevated:  #182030;
  --bg-surface-overlay:   rgba(18, 23, 34, 0.85);

  /* Hairlines & Structural Borders */
  --border-subtle:        rgba(255, 255, 255, 0.08);
  --border-medium:        rgba(255, 255, 255, 0.16);
  --border-focus:         var(--color-amber-400);

  /* ------------------------------------------------------------------------
     2. COLOR PALETTES: THEATRICAL AMBER (10% ACCENT - SPEAKER 1)
     ------------------------------------------------------------------------ */
  --color-amber-50:  #FFFBEB; /* oklch(0.987 0.021 95.3) */
  --color-amber-100: #FEF3C7; /* oklch(0.962 0.058 95.6) */
  --color-amber-200: #FDE68A; /* oklch(0.924 0.115 95.7) */
  --color-amber-300: #FCD34D; /* oklch(0.879 0.153 91.6) */
  --color-amber-400: #FBBF24; /* oklch(0.837 0.164 84.4) */
  --color-amber-500: #F59E0B; /* oklch(0.769 0.165 70.1) - CORE ACCENT */
  --color-amber-600: #D97706; /* oklch(0.666 0.157 58.3) */
  --color-amber-700: #B45309; /* oklch(0.555 0.146 49.0) */
  --color-amber-800: #92400E; /* oklch(0.473 0.125 46.2) */
  --color-amber-900: #78350F; /* oklch(0.414 0.105 45.9) */
  --color-amber-950: #451A03; /* oklch(0.279 0.074 45.6) */

  /* ------------------------------------------------------------------------
     3. COLOR PALETTES: ARCANE AMETHYST (10% ACCENT - SPEAKER 2)
     ------------------------------------------------------------------------ */
  --color-amethyst-50:  #F5F3FF; /* oklch(0.969 0.016 293.8) */
  --color-amethyst-100: #EDE9FE; /* oklch(0.943 0.028 294.6) */
  --color-amethyst-200: #DDD6FE; /* oklch(0.894 0.055 293.3) */
  --color-amethyst-300: #C4B5FD; /* oklch(0.811 0.101 293.6) */
  --color-amethyst-400: #A78BFA; /* oklch(0.709 0.159 293.5) - SPEAKER 2 CORE */
  --color-amethyst-500: #8B5CF6; /* oklch(0.606 0.219 292.7) */
  --color-amethyst-600: #7C3AED; /* oklch(0.541 0.247 293.0) */
  --color-amethyst-700: #6D28D9; /* oklch(0.491 0.241 292.6) */
  --color-amethyst-800: #5B21B6; /* oklch(0.432 0.211 292.8) */
  --color-amethyst-900: #4C1D95; /* oklch(0.380 0.178 293.7) */
  --color-amethyst-950: #2E1065; /* oklch(0.283 0.135 291.1) */

  /* ------------------------------------------------------------------------
     4. COLOR PALETTES: THEATRICAL CRIMSON (RECORDING PULSE)
     ------------------------------------------------------------------------ */
  --color-crimson-500: #EF4444; /* oklch(0.637 0.208 25.3) - ACTIVE RECORDING */
  --color-crimson-600: #DC2626; /* oklch(0.577 0.215 27.3) */
  --color-crimson-700: #B91C1C; /* oklch(0.505 0.190 27.5) */
  --color-crimson-800: #991B1B; /* oklch(0.444 0.161 26.9) */

  /* ------------------------------------------------------------------------
     5. COLOR PALETTES: EMERALD SCRIBE (CALIBRATION & SAFE STORAGE)
     ------------------------------------------------------------------------ */
  --color-emerald-400: #34D399; /* oklch(0.773 0.153 163.2) */
  --color-emerald-500: #10B981; /* oklch(0.696 0.149 162.5) - VAULT LOCKED */
  --color-emerald-700: #047857; /* oklch(0.508 0.105 165.6) */

  /* ------------------------------------------------------------------------
     6. MATHEMATICAL TYPOGRAPHY SCALE (GOLDEN RATIO DERIVED)
     ------------------------------------------------------------------------ */
  --font-serif: 'Cinzel', 'Gelasio', Georgia, serif;
  --font-sans:  'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono:  'JetBrains Mono', 'Ubuntu Mono', monospace;

  --text-xs:    0.625rem;  /* 10px - 16 / 1.618 */
  --text-sm:    0.772rem;  /* 12.36px - 16 / sqrt(phi) */
  --text-base:  1.000rem;  /* 16px - Baseline */
  --text-md:    1.272rem;  /* 20.35px - 16 * sqrt(phi) */
  --text-lg:    1.618rem;  /* 25.89px - 16 * phi */
  --text-xl:    2.058rem;  /* 32.93px - 16 * phi * sqrt(phi) */
  --text-2xl:   2.618rem;  /* 41.89px - 16 * phi^2 */
  --text-hero:  3.375rem;  /* 54px - Theatrical Timer */

  --line-height-golden:   1.618;
  --line-height-dialogue: 1.500;
  --line-height-dense:    1.272;
  --line-height-flat:     1.000;

  /* ------------------------------------------------------------------------
     7. FIBONACCI SPACING TOKENS (8PT HARMONIZED)
     ------------------------------------------------------------------------ */
  --space-1: 2px;
  --space-2: 4px;
  --space-3: 8px;
  --space-4: 13px;
  --space-5: 21px;
  --space-6: 34px;
  --space-7: 55px;
  --space-8: 89px;

  /* ------------------------------------------------------------------------
     8. GEOMETRY, ELEVATION & MECHANICAL PRESS TOKENS
     ------------------------------------------------------------------------ */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 13px;
  --radius-lg: 21px;
  --radius-full: 9999px;

  --shadow-subtle:   0 1px 3px rgba(0, 0, 0, 0.4);
  --shadow-elevated: 0 8px 24px rgba(0, 0, 0, 0.6);
  --shadow-modal:    0 24px 64px rgba(0, 0, 0, 0.85);

  /* ------------------------------------------------------------------------
     9. INTERACTION TIMINGS & SPRINGS (DOHERTY THRESHOLD <400MS)
     ------------------------------------------------------------------------ */
  --duration-instant: 100ms;
  --duration-fast:    200ms;
  --duration-base:    300ms;
  --ease-spring:      cubic-bezier(0.16, 1, 0.3, 1);
  --ease-mechanical:  cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 7. Design System QA & Enforcement Gate

Before any pull request, refactor, or UI feature merges into Arc Scribe, it must satisfy all 12 points of this QA Gate:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              ARC SCRIBE 12-POINT PRE-SHIP GATE                         │
├────┬─────────────────────────────┬─────────────────────────────────────────────────────┤
│ 01 │ WCAG 2.2 AAA Contrast       │ Body text ≥ 7:1 against background; UI ≥ 3:1.        │
│ 02 │ Golden Line Height          │ Prose reader strictly enforces line-height: 1.618.  │
│ 03 │ Reading Measure Rule        │ Prose container locked between 65ch and 75ch.       │
│ 04 │ Fitts's Law Touch Target    │ Mobile record buttons meet min-height 56px.         │
│ 05 │ Spatial Distance Guard      │ Destructive/Pause separated by ≥ 34px from record.  │
│ 06 │ Hick's Law Setup Ceiling    │ Max 3 core inputs before enactment can trigger.     │
│ 07 │ Miller's Chunking Rule      │ Transcripts grouped into turns & 3-5 scene beats.   │
│ 08 │ Von Restorff Isolation      │ Active record dims background UI & pulses crimson.  │
│ 09 │ No Blurry Neon Blobs        │ Zero decorative radial blur glow divs.               │
│ 10 │ Doherty Latency Threshold   │ Canvas visualizer renders at 60fps (<16.6ms).       │
│ 11 │ Sibling Speaker Distinction │ Distinct 2px spine borders (Amber vs Amethyst).     │
│ 12 │ Local-First Postel Guard    │ Audio slices committed to IndexedDB every 3000ms.   │
└────┴─────────────────────────────┴─────────────────────────────────────────────────────┘
```

---
*Signed and Approved for Implementation in Arc Scribe Atelier.*  
*Brand Identity & Mathematical Design Systems Researcher.*
