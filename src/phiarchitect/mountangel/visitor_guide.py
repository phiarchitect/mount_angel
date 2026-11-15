"""Build the interactive & print-ready Visitor Wayfinding Studio (`docs/visitor-guide.html`).

Combines CSS-variable-driven parametric SVGs from ``phiarchitect.mountangel.wayfinding``
with a live style-honing workbench supporting:
  - 4 Layout Views: All Pieces, 4"x9" Rack Card Spread, 24"x36" Lobby Posters, Lobby Wall Mockup
  - 4 Abbey & Model Palettes (all with architectural Red Poché): Abbey & Model (Plaster,
    Buff-Brick & Birch), Warm Buff-Brick, White Plaster, and Dark Studio
  - 3 Typography Voices, 3 Red Poché Styles, 3 Media Modes, Line Weight & Zoom Sliders
  - Bidirectional interactive Pin 1–12 highlighting across all floor plans and directories
  - Clean @media print stylesheet for 4"x9" Rack Cards and 24"x36" Posters
"""

from __future__ import annotations

from pathlib import Path

from .wayfinding import build_all_wayfinding_svgs


def render_visitor_guide_html() -> str:
    """Render the complete self-contained HTML string for `docs/visitor-guide.html`."""
    svgs = build_all_wayfinding_svgs()

    directory_items = [
        (
            "1",
            "+2'-0\"",
            "Restrooms &amp; 32-Batten Wood Screen",
            "Lobby West",
            "Floor-to-ceiling vertical wood battens screen the Men's &amp; Women's restroom alcove without breaking the Lobby's serene plaster plane.",
            "south_entry",
        ),
        (
            "2",
            "+2'-0\"",
            "Rare Book &amp; Lecture Auditorium",
            "Lobby East · Rm 327",
            "Splayed acoustic walls, sweeping curved AV projection booth, quarter-circle SE birch stage, and Aalto's 3-wave undulating ceiling.",
            "auditorium_cutaway",
        ),
        (
            "3",
            "0'-0\"",
            "Public Catalogue &amp; Squiggle Walls",
            "Entry West · Rm 320",
            "Framed by two Aalto signatures: a 28°-canted vertical wood-fin screen wall and a sinuous S-curved plaster partition.",
            "cutaway_axon",
        ),
        (
            "4",
            "0'-0\"",
            "Control Desk &amp; Slatted Ceiling",
            "Central Peninsula",
            "Curved birch circulation desk beneath a 2-tier radial 1&quot;×1&quot; hemlock ceiling sector pierced by circular skylight oculi.",
            "control_glass_wall",
        ),
        (
            "5",
            "0'-0\"",
            "Glazed Offices &amp; Media Lounge",
            "East Throat · Rms 344–346",
            "14-bay birch-framed glass partition over a black-capped white wainscot, leading to the Periodical Lounge's Mt. Hood picture window.",
            "lounge_mthood",
        ),
        (
            "6",
            "0'-0\"",
            "Reading Well Counter &amp; Lamps",
            "Well Rim",
            "Semicircular matte-black linoleum study counter with Artek stools and 16 custom white angled-arm mushroom reading lamps.",
            "mezzanine_pov",
        ),
        (
            "7",
            "0'-0\"",
            "15 Radiating Birch Bookstacks",
            "Main North Fan",
            "Variable-length (16.3'–20.0') Aalto birch bookcases with recessed linoleum plinths and 5-batten vertical directory stanchions.",
            "section_plan_l3",
        ),
        (
            "8",
            "0'-0\"",
            "H-Column D Mt. Hood Window",
            "NE Perimeter · 65.7°",
            "Eye-level square aperture punched between the tapered legs of irregular H-Column D, framing Mt. Hood across the Pudding River valley.",
            "alcove_mthood",
        ),
        (
            "9",
            "+2'-0\"",
            "Cataloging &amp; Technical Wing",
            "West Wing · Staff",
            "Monastic cataloging, acquisitions, and bindery workrooms lit from above by perforated conical rooftop skylights.",
            "hillside_hero",
        ),
        (
            "10",
            "-4'-6\"",
            "Mezzanine Reference Gallery",
            "Via Well Stairs",
            "Reached by radial U-turn switchback stairs; pairs a curved inner Reference Bookwall with cantilevered outer linoleum study stations.",
            "sunken_well",
        ),
        (
            "11",
            "-12'-6\"",
            "Level 2 Stacks &amp; Study Carrels",
            "Lower North Fan",
            "Double ring of radial bookstacks, 20 perimeter carrel alcoves, and view windows shaded by exterior hemlock sun louvers.",
            "section_well",
        ),
        (
            "12",
            "-26'-6\"",
            "Level 1 Archival Base Deck",
            "Bluff Toe · Staff",
            "Deepest terraced stack deck anchored into the northern hillside behind Aalto's five-chord concrete retaining wall.",
            "h_columns_north",
        ),
    ]

    rack_dir_html = "\n".join(
        f"""              <div class="rc-dir-item" data-pin-link="{num}" tabindex="0">
                <span class="rc-pin-badge">{num}</span>
                <div class="rc-dir-copy">
                  <strong>{title}</strong>
                  <span>{loc} &middot; {elev}</span>
                </div>
              </div>"""
        for num, elev, title, loc, _desc, _cam in directory_items
    )

    poster_dir_html = "\n".join(
        f"""              <div class="ps-dir-card" data-pin-link="{num}" tabindex="0">
                <div class="ps-dir-top">
                  <span class="ps-pin-badge">{num}</span>
                  <div class="ps-dir-head">
                    <strong>{title}</strong>
                    <span class="ps-dir-meta">{loc} &middot; EL. {elev}</span>
                  </div>
                  <a href="library-3d.html?cam={cam}" class="ps-3d-chip" title="Open coordinated view in Interactive 3D">3D &#8599;</a>
                </div>
                <p>{desc}</p>
              </div>"""
        for num, elev, title, loc, desc, cam in directory_items
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Visitor Rack Card &amp; Lobby Orientation Posters — Mount Angel Abbey Library (Alvar Aalto, 1970)</title>
  <link rel="icon" href="favicon.ico" sizes="any">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="suite.css">
  <style>
    /* =========================================================================
       1. STUDIO SHELL & GLOBAL RESET
       ========================================================================= */
    :root {{
      --ws-bg: #0b0f17;
      --ws-panel: #121926;
      --ws-panel-2: #182233;
      --ws-border: rgba(148, 163, 184, 0.18);
      --ws-gold: #d97706;
      --ws-gold-bright: #f59e0b;
      --ws-cyan: #06b6d4;
      --ws-text: #f3f4f6;
      --ws-muted: #9ca3af;
      --ui-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --ui-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

      /* Live Style-Honing Multipliers */
      --stroke-scale: 1;
      --board-zoom: 1;
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html {{
      scroll-behavior: smooth;
      background: var(--ws-bg);
      color: var(--ws-text);
      font-family: var(--ui-sans);
      line-height: 1.5;
    }}

    body {{
      min-height: 100vh;
      background:
        radial-gradient(circle at 14% 6%, rgba(217, 119, 6, 0.08), transparent 38%),
        radial-gradient(circle at 86% 14%, rgba(6, 182, 212, 0.07), transparent 40%),
        var(--ws-bg);
      overflow-x: hidden;
    }}

    /* =========================================================================
       2. SUITE NAVIGATION HEADER
       ========================================================================= */
    .top-nav {{
      position: sticky;
      top: 0;
      z-index: 200;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 11px 26px;
      background: rgba(11, 15, 23, 0.90);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--ws-border);
      flex-wrap: wrap;
    }}

    .brand {{
      display: flex;
      flex-direction: column;
      text-decoration: none;
      color: var(--ws-text);
    }}
    .brand-title {{
      font-size: 0.95rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}
    .brand-sub {{
      font-size: 0.71rem;
      color: var(--ws-gold-bright);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-family: var(--ui-mono);
    }}

    .suite-btns {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .nav-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 13px;
      border-radius: 7px;
      font-size: 0.78rem;
      font-weight: 600;
      text-decoration: none;
      border: 1px solid var(--ws-border);
      background: rgba(30, 41, 59, 0.65);
      color: #e5e7eb;
      transition: all 0.16s ease;
    }}
    .nav-btn:hover {{
      border-color: rgba(245, 158, 11, 0.55);
      color: #fff;
    }}
    .nav-btn.active {{
      background: rgba(217, 119, 6, 0.20);
      border-color: rgba(245, 158, 11, 0.65);
      color: #fde68a;
    }}
    .nav-btn.primary {{
      background: linear-gradient(135deg, #d97706, #b45309);
      border-color: #f59e0b;
      color: #fff;
    }}

    /* =========================================================================
       3. STUDIO INTRO & STICKY STYLE-HONING WORKBENCH
       ========================================================================= */
    .studio-header {{
      max-width: 1460px;
      margin: 0 auto;
      padding: 28px 28px 14px;
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 24px;
      flex-wrap: wrap;
    }}
    .studio-eyebrow {{
      font-family: var(--ui-mono);
      font-size: 0.73rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--ws-gold-bright);
      margin-bottom: 6px;
    }}
    .studio-header h1 {{
      font-family: 'Iowan Old Style', 'Palatino Linotype', Georgia, serif;
      font-size: clamp(1.65rem, 2.6vw, 2.35rem);
      font-weight: 600;
      color: #fafaf9;
      line-height: 1.15;
    }}
    .studio-header p {{
      margin-top: 6px;
      max-width: 760px;
      font-size: 0.90rem;
      color: var(--ws-muted);
    }}
    .studio-quick-actions {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .print-btn {{
      cursor: pointer;
      padding: 8px 14px;
      border-radius: 8px;
      border: 1px solid rgba(245, 158, 11, 0.45);
      background: rgba(217, 119, 6, 0.15);
      color: #fde68a;
      font-size: 0.79rem;
      font-weight: 600;
      font-family: var(--ui-sans);
      transition: all 0.15s ease;
    }}
    .print-btn:hover {{
      background: rgba(217, 119, 6, 0.30);
      color: #fff;
    }}

    .workbench-wrap {{
      position: sticky;
      top: 62px;
      z-index: 160;
      max-width: 1460px;
      margin: 6px auto 24px;
      padding: 0 28px;
    }}
    .workbench {{
      background: rgba(18, 25, 38, 0.94);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(245, 158, 11, 0.28);
      border-radius: 14px;
      padding: 12px 16px;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .wb-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
    }}
    .wb-row-secondary {{
      padding-top: 9px;
      border-top: 1px solid rgba(148, 163, 184, 0.14);
    }}
    .workbench.collapsed .wb-row-secondary {{
      display: none;
    }}
    .wb-group {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .wb-lbl {{
      font-family: var(--ui-mono);
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.09em;
      color: var(--ws-muted);
      font-weight: 600;
    }}
    .pill-bar {{
      display: inline-flex;
      background: rgba(8, 12, 20, 0.65);
      border: 1px solid var(--ws-border);
      border-radius: 9px;
      padding: 2px;
      gap: 2px;
      flex-wrap: wrap;
    }}
    .wb-pill {{
      border: none;
      background: transparent;
      color: #cbd5e1;
      font-family: var(--ui-sans);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 5px 11px;
      border-radius: 7px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .wb-pill:hover {{
      color: #fff;
      background: rgba(255, 255, 255, 0.06);
    }}
    .wb-pill.active {{
      background: #eab308;
      color: #0b0f17;
      font-weight: 700;
    }}
    .swatch-dot {{
      width: 11px;
      height: 11px;
      border-radius: 50%;
      border: 1px solid rgba(255, 255, 255, 0.45);
      display: inline-block;
    }}
    .wb-select {{
      background: rgba(8, 12, 20, 0.75);
      color: #f3f4f6;
      border: 1px solid var(--ws-border);
      border-radius: 7px;
      padding: 5px 9px;
      font-size: 0.75rem;
      font-family: var(--ui-sans);
      cursor: pointer;
    }}
    .wb-slider-group {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.74rem;
      color: #d1d5db;
    }}
    .wb-slider-group input[type="range"] {{
      width: 78px;
      accent-color: #eab308;
      cursor: pointer;
    }}
    .wb-check {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 0.74rem;
      color: #d1d5db;
      cursor: pointer;
      user-select: none;
      padding: 3px 7px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(148, 163, 184, 0.14);
    }}
    .wb-check input {{
      accent-color: #eab308;
      cursor: pointer;
    }}
    .wb-collapse-btn {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--ws-border);
      color: #cbd5e1;
      border-radius: 7px;
      padding: 5px 10px;
      font-size: 0.73rem;
      cursor: pointer;
      font-family: var(--ui-mono);
    }}

    /* =========================================================================
       4. PRINT PALETTE THEMES & TYPOGRAPHY VOICES (APPLIED TO .print-stage)
       ========================================================================= */
    .print-stage {{
      /* Default Theme: vellum (Abbey & Model — Plaster, Buff-Brick, Birch & Red Poché) */
      --paper: #f5efe4;
      --paper-alt: #e7dbc7;
      --paper-card: #fbf8f2;
      --ink: #231f1b;
      --ink-soft: #3f3831;
      --muted: #6c6155;
      --rule: rgba(35, 31, 27, 0.20);
      --rule-strong: rgba(35, 31, 27, 0.58);
      --poche: #a42d21;
      --poche-stroke: #5e170f;
      --accent: #a42d21;
      --accent-soft: rgba(164, 45, 33, 0.13);
      --brick-ctx: #d7c19e;
      --birch: #c48b45;
      --birch-fill: rgba(196, 139, 69, 0.36);
      --sky: #3174ab;
      --gold: #c88322;
      --meadow: rgba(95, 125, 79, 0.16);
      --earth: #cfc1ab;
      --earth-hatch: rgba(72, 57, 41, 0.20);
      --zone-public: rgba(200, 131, 34, 0.16);
      --zone-quiet: rgba(49, 116, 171, 0.10);
      --zone-lounge: rgba(95, 125, 79, 0.16);
      --zone-aud: rgba(164, 45, 33, 0.14);
      --zone-staff: rgba(35, 31, 27, 0.08);
      --zone-well: rgba(49, 116, 171, 0.19);
      --pin-fg: #ffffff;

      /* Default Voice: editorial */
      --f-display: 'Iowan Old Style', 'Palatino Linotype', 'Book Antiqua', Georgia, serif;
      --f-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      --f-tech: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;

      max-width: 1460px;
      margin: 0 auto;
      padding: 4px 28px 80px;
      transform-origin: top center;
    }}

    /* Theme 2: Warm Buff-Brick & Oxide Red Poché */
    .print-stage[data-print-theme="brick"] {{
      --paper: #ece0cb;
      --paper-alt: #dccba9;
      --paper-card: #f6efe2;
      --ink: #241d17;
      --ink-soft: #40352c;
      --muted: #68594b;
      --rule: rgba(36, 29, 23, 0.22);
      --rule-strong: rgba(36, 29, 23, 0.62);
      --poche: #98261b;
      --poche-stroke: #54140d;
      --accent: #98261b;
      --accent-soft: rgba(152, 38, 27, 0.14);
      --brick-ctx: #cdb38b;
      --birch: #b97e35;
      --birch-fill: rgba(185, 126, 53, 0.36);
      --sky: #2b6c9e;
      --gold: #bd7818;
      --meadow: rgba(88, 118, 72, 0.17);
      --earth: #c3b193;
      --earth-hatch: rgba(66, 50, 34, 0.22);
      --zone-public: rgba(189, 120, 24, 0.16);
      --zone-quiet: rgba(43, 108, 158, 0.10);
      --zone-lounge: rgba(88, 118, 72, 0.16);
      --zone-aud: rgba(152, 38, 27, 0.14);
      --zone-staff: rgba(36, 29, 23, 0.08);
      --zone-well: rgba(43, 108, 158, 0.18);
      --pin-fg: #ffffff;
    }}

    /* Theme 3: Aalto White Plaster & Vermilion Poché */
    .print-stage[data-print-theme="swiss"] {{
      --paper: #faf9f5;
      --paper-alt: #efece3;
      --paper-card: #ffffff;
      --ink: #1a1918;
      --ink-soft: #32302d;
      --muted: #656059;
      --rule: rgba(26, 25, 24, 0.18);
      --rule-strong: #1a1918;
      --poche: #b02e21;
      --poche-stroke: #631810;
      --accent: #b02e21;
      --accent-soft: rgba(176, 46, 33, 0.11);
      --brick-ctx: #dfd0b6;
      --birch: #c68d44;
      --birch-fill: rgba(198, 141, 68, 0.32);
      --sky: #286da8;
      --gold: #cf831b;
      --meadow: rgba(95, 125, 79, 0.13);
      --earth: #ded7c9;
      --earth-hatch: rgba(65, 55, 43, 0.18);
      --zone-public: rgba(207, 131, 27, 0.13);
      --zone-quiet: rgba(40, 109, 168, 0.08);
      --zone-lounge: rgba(95, 125, 79, 0.13);
      --zone-aud: rgba(176, 46, 33, 0.12);
      --zone-staff: rgba(26, 25, 24, 0.06);
      --zone-well: rgba(40, 109, 168, 0.16);
      --pin-fg: #ffffff;
    }}

    /* Theme 4: Dark Studio (Matches 3D Model UI + Red Poché) */
    .print-stage[data-print-theme="basalt"] {{
      --paper: #151921;
      --paper-alt: #10131a;
      --paper-card: #1c212b;
      --ink: #f2ede2;
      --ink-soft: #d5cdbe;
      --muted: #9d9486;
      --rule: rgba(242, 237, 226, 0.18);
      --rule-strong: rgba(242, 237, 226, 0.58);
      --poche: #c43c2d;
      --poche-stroke: #7a1f16;
      --accent: #d4553d;
      --accent-soft: rgba(212, 85, 61, 0.18);
      --brick-ctx: #6c5a43;
      --birch: #d59c55;
      --birch-fill: rgba(213, 156, 85, 0.32);
      --sky: #58add8;
      --gold: #e59f3c;
      --meadow: rgba(95, 128, 78, 0.22);
      --earth: #27221d;
      --earth-hatch: rgba(213, 195, 168, 0.14);
      --zone-public: rgba(229, 159, 60, 0.15);
      --zone-quiet: rgba(88, 173, 216, 0.11);
      --zone-lounge: rgba(95, 128, 78, 0.16);
      --zone-aud: rgba(196, 60, 45, 0.18);
      --zone-staff: rgba(242, 237, 226, 0.07);
      --zone-well: rgba(88, 173, 216, 0.20);
      --pin-fg: #ffffff;
    }}

    /* Font Voices */
    .print-stage[data-font-voice="modernist"] {{
      --f-display: 'Avenir Next', 'Futura', 'Inter', -apple-system, sans-serif;
      --f-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    .print-stage[data-font-voice="technical"] {{
      --f-display: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
      --f-body: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    }}

    /* =========================================================================
       5. PARAMETRIC SVG STYLING (ALL DRIVEN BY CSS VARIABLES!)
       ========================================================================= */
    .wf-svg {{
      width: 100%;
      height: auto;
      display: block;
      user-select: none;
    }}

    /* Zone Tints */
    .zone-public {{ fill: var(--zone-public); stroke: none; }}
    .zone-quiet {{ fill: var(--zone-quiet); stroke: none; }}
    .zone-lounge {{ fill: var(--zone-lounge); stroke: none; }}
    .zone-auditorium {{ fill: var(--zone-aud); stroke: none; }}
    .zone-staff {{ fill: var(--zone-staff); stroke: none; }}
    .zone-well {{ fill: var(--zone-well); stroke: none; }}

    /* Plaza & Pergolas */
    .wf-plaza {{ fill: var(--paper-alt); stroke: var(--rule); stroke-width: calc(0.8px * var(--stroke-scale)); }}
    .wf-pergola {{ fill: none; stroke: var(--muted); stroke-width: calc(0.9px * var(--stroke-scale)); stroke-dasharray: 2 2; }}
    .wf-pergola-grid {{ stroke: var(--rule); stroke-width: calc(0.7px * var(--stroke-scale)); }}
    .wf-canopy-marquee {{ fill: var(--paper-card); stroke: var(--ink-soft); stroke-width: calc(1.1px * var(--stroke-scale)); }}

    /* Regulating Geometry */
    .wf-reg-ray {{ stroke: var(--accent); stroke-opacity: 0.36; stroke-width: calc(0.75px * var(--stroke-scale)); stroke-dasharray: 4 3; }}
    .wf-reg-ray-alt {{ stroke: var(--sky); stroke-opacity: 0.34; stroke-width: calc(0.7px * var(--stroke-scale)); stroke-dasharray: 3 3; }}
    .wf-reg-arc {{ fill: none; stroke: var(--sky); stroke-opacity: 0.38; stroke-width: calc(0.75px * var(--stroke-scale)); stroke-dasharray: 3 3; }}
    .wf-wp-dot {{ fill: var(--accent); stroke: var(--paper); stroke-width: 1.1px; }}

    /* Millwork, Bookcases, Stairs, Skylights */
    .wf-well-void {{ fill: var(--paper); fill-opacity: 0.55; stroke: var(--ink-soft); stroke-width: calc(1.1px * var(--stroke-scale)); }}
    .wf-mezz-curve {{ fill: none; stroke: var(--ink-soft); stroke-width: calc(1.0px * var(--stroke-scale)); stroke-dasharray: 3 2; }}
    .wf-mezz-desk {{ fill: none; stroke: var(--birch); stroke-width: calc(1.2px * var(--stroke-scale)); }}
    .wf-stair {{ fill: var(--paper-card); stroke: var(--ink-soft); stroke-width: calc(0.9px * var(--stroke-scale)); }}
    .wf-stair-tread {{ fill: none; stroke: var(--muted); stroke-width: calc(0.75px * var(--stroke-scale)); }}
    .wf-workbench {{ fill: var(--ink-soft); fill-opacity: 0.80; stroke: var(--ink); stroke-width: calc(0.7px * var(--stroke-scale)); }}
    .wf-lamp-dot {{ fill: var(--gold); stroke: var(--ink); stroke-width: 0.5px; }}
    .wf-bookcase {{ fill: var(--birch-fill); stroke: var(--birch); stroke-width: calc(0.95px * var(--stroke-scale)); }}
    .wf-shelf-line {{ stroke: var(--birch); stroke-opacity: 0.65; stroke-width: calc(0.6px * var(--stroke-scale)); }}
    .wf-control-desk {{ fill: var(--birch-fill); stroke: var(--ink); stroke-width: calc(1.05px * var(--stroke-scale)); }}
    .wf-control-desk-line {{ fill: none; stroke: var(--birch); stroke-width: calc(1.5px * var(--stroke-scale)); }}
    .wf-ceiling-halo {{ fill: none; stroke: var(--birch); stroke-opacity: 0.65; stroke-width: calc(0.85px * var(--stroke-scale)); stroke-dasharray: 2 2.5; }}
    .wf-carrel {{ fill: none; stroke: var(--birch); stroke-width: calc(0.85px * var(--stroke-scale)); }}
    .wf-table {{ fill: var(--paper-card); stroke: var(--birch); stroke-width: calc(0.9px * var(--stroke-scale)); }}
    .wf-stage {{ fill: var(--birch-fill); stroke: var(--ink-soft); stroke-width: calc(1.0px * var(--stroke-scale)); }}
    .wf-seat-arc {{ fill: none; stroke: var(--muted); stroke-opacity: 0.72; stroke-width: calc(0.85px * var(--stroke-scale)); stroke-dasharray: 5 2; }}
    .wf-wood-screen {{ stroke: var(--birch); stroke-width: calc(3.0px * var(--stroke-scale)); stroke-dasharray: 1.6 1.4; }}
    .wf-wood-fin {{ fill: var(--birch); stroke: none; }}
    .wf-skylight-overhead {{ fill: var(--sky); fill-opacity: 0.10; stroke: var(--sky); stroke-opacity: 0.48; stroke-width: calc(0.8px * var(--stroke-scale)); stroke-dasharray: 3 2; }}
    .wf-skylight-circle {{ fill: var(--gold); fill-opacity: 0.12; stroke: var(--gold); stroke-opacity: 0.62; stroke-width: calc(0.8px * var(--stroke-scale)); stroke-dasharray: 2 1.8; }}

    /* Walls & Structural Poché */
    .wf-wall-int {{ fill: none; stroke: var(--ink-soft); stroke-width: calc(1.2px * var(--stroke-scale)); stroke-linecap: round; }}
    .wf-wall-int-bold {{ fill: none; stroke: var(--ink); stroke-width: calc(1.7px * var(--stroke-scale)); stroke-linecap: round; stroke-linejoin: round; }}
    .wf-glass-wall {{ stroke: var(--sky); stroke-width: calc(1.8px * var(--stroke-scale)); }}
    .wf-mullion-dot {{ fill: var(--birch); }}
    .wf-glass-vestibule {{ fill: var(--sky); fill-opacity: 0.10; stroke: var(--sky); stroke-width: calc(1.3px * var(--stroke-scale)); }}
    .wf-wall-ext {{ fill: none; stroke: var(--ink); stroke-width: calc(2.2px * var(--stroke-scale)); stroke-linejoin: miter; }}
    .wf-poche-solid {{ fill: var(--poche); stroke: var(--poche-stroke); stroke-width: calc(0.75px * var(--stroke-scale)); }}
    .wf-col-dot {{ fill: var(--poche); }}
    .wf-vista-arrow {{ stroke: var(--accent); stroke-width: calc(1.35px * var(--stroke-scale)); stroke-dasharray: 4 2.5; }}
    .wf-vista-lbl {{ fill: var(--accent); font-family: var(--f-tech); font-size: 8.5px; font-weight: 700; letter-spacing: 0.05em; }}

    /* Cross-Section & Detail Specific */
    .wf-earth {{ fill: var(--earth); stroke: none; }}
    .wf-earth-hatch {{ pointer-events: none; }}
    .wf-earth-hatch-stroke {{ stroke: var(--earth-hatch); stroke-width: 1.45px; }}
    .wf-grade-line {{ fill: none; stroke: var(--ink); stroke-width: calc(1.8px * var(--stroke-scale)); }}
    .wf-aud-ghost {{ fill: var(--paper-alt); fill-opacity: 0.65; stroke: var(--muted); stroke-opacity: 0.45; stroke-width: calc(0.85px * var(--stroke-scale)); stroke-dasharray: 4 3; }}
    .wf-ghost-lbl {{ fill: var(--muted); font-family: var(--f-tech); font-size: 7.5px; letter-spacing: 0.06em; }}
    .wf-ray-sky {{ fill: none; stroke: var(--sky); stroke-width: calc(1.3px * var(--stroke-scale)); stroke-dasharray: 4 2.5; }}
    .wf-ray-sun {{ fill: none; stroke: var(--gold); stroke-width: calc(1.3px * var(--stroke-scale)); stroke-dasharray: 3.5 2.5; }}
    .wf-datum-line {{ stroke: var(--rule); stroke-width: calc(0.75px * var(--stroke-scale)); stroke-dasharray: 2.5 2.5; }}
    .wf-datum-lbl {{ fill: var(--muted); font-family: var(--f-tech); font-size: 8.4px; font-weight: 600; letter-spacing: 0.04em; }}
    .wf-glass-elev {{ stroke: var(--sky); stroke-width: calc(1.8px * var(--stroke-scale)); }}
    .wf-batten-line {{ stroke: var(--birch); stroke-width: calc(1.2px * var(--stroke-scale)); }}
    .wf-slat-ceiling {{ stroke: var(--birch); stroke-width: calc(2.4px * var(--stroke-scale)); stroke-dasharray: 2.2 1.4; }}
    .wf-rail-line {{ stroke: var(--ink-soft); stroke-width: calc(0.85px * var(--stroke-scale)); }}
    .wf-col-elev {{ fill: var(--paper-card); stroke: var(--ink-soft); stroke-width: calc(0.85px * var(--stroke-scale)); }}
    .wf-lamp-stem {{ stroke: var(--ink); stroke-width: calc(1.25px * var(--stroke-scale)); stroke-linecap: round; }}
    .wf-lamp-dome {{ fill: var(--paper-card); stroke: var(--ink); stroke-width: calc(1.15px * var(--stroke-scale)); }}
    .wf-louver-tick {{ stroke: var(--birch); stroke-width: calc(1.2px * var(--stroke-scale)); }}
    .wf-skylight-glass {{ stroke: var(--sky); stroke-width: calc(2.4px * var(--stroke-scale)); }}
    .wf-lantern-cap {{ fill: var(--paper-card); stroke: var(--ink); stroke-width: calc(1.15px * var(--stroke-scale)); }}
    .wf-throat-line {{ fill: none; stroke: var(--ink-soft); stroke-width: calc(0.95px * var(--stroke-scale)); }}
    .wf-truss-web {{ fill: none; stroke: var(--muted); stroke-opacity: 0.55; stroke-width: calc(0.9px * var(--stroke-scale)); }}
    .wf-poche-cut {{ fill: var(--poche); stroke: var(--poche-stroke); stroke-width: calc(1.05px * var(--stroke-scale)); stroke-linejoin: round; }}
    .wf-hatch-stroke {{ stroke: var(--poche); stroke-width: 1.35px; }}
    .wf-figure {{ fill: var(--accent); fill-opacity: 0.85; }}
    .wf-leader {{ stroke: var(--ink-soft); stroke-opacity: 0.65; stroke-width: calc(0.8px * var(--stroke-scale)); }}
    .wf-leader-dot {{ fill: var(--accent); }}
    .wf-callout-lbl {{ fill: var(--ink); font-family: var(--f-tech); font-size: 9.0px; font-weight: 700; letter-spacing: 0.04em; }}
    .wf-room-tag {{ fill: var(--ink-soft); fill-opacity: 0.78; font-family: var(--f-tech); font-size: 8.2px; font-weight: 700; letter-spacing: 0.07em; }}

    /* Poché Mode Switching */
    .print-stage[data-poche-mode="hatch"] .wf-poche-cut,
    .print-stage[data-poche-mode="hatch"] .wf-poche-solid {{
      fill: url(#wfDiagHatch);
      stroke: var(--poche);
    }}
    .print-stage[data-poche-mode="outline"] .wf-poche-cut,
    .print-stage[data-poche-mode="outline"] .wf-poche-solid {{
      fill: var(--paper-alt);
      stroke: var(--poche);
    }}

    /* Pins, YAH Beacon, Compass, Scalebar & Campus Map */
    .wf-yah-pulse {{ fill: var(--accent); fill-opacity: 0.24; }}
    .wf-yah-core {{ fill: var(--accent); stroke: var(--paper); stroke-width: 1.5px; }}
    .wf-yah-star {{ fill: var(--pin-fg); font-size: 8.5px; font-weight: 800; }}
    .wf-yah-lbl {{ fill: var(--accent); font-family: var(--f-tech); font-size: 8.5px; font-weight: 800; letter-spacing: 0.07em; }}

    .wf-pin {{ cursor: pointer; transition: transform 0.15s ease; }}
    .wf-pin-bg {{ fill: var(--ink); stroke: var(--paper); stroke-width: 1.4px; transition: all 0.15s ease; }}
    .wf-pin-txt {{ fill: var(--paper); font-family: var(--f-tech); font-size: 8.6px; font-weight: 800; pointer-events: none; }}
    .wf-pin.is-active .wf-pin-bg,
    .wf-pin:hover .wf-pin-bg {{
      fill: var(--accent);
      r: 10.2px;
      stroke-width: 2px;
    }}
    .wf-pin.is-active .wf-pin-txt,
    .wf-pin:hover .wf-pin-txt {{
      fill: var(--pin-fg);
    }}

    .wf-compass-ring {{ fill: var(--paper-card); stroke: var(--ink-soft); stroke-width: 1px; }}
    .wf-compass-needle {{ fill: var(--accent); }}
    .wf-compass-lbl {{ fill: var(--ink); font-family: var(--f-tech); font-size: 8.5px; font-weight: 800; }}
    .wf-scale-line {{ stroke: var(--ink); stroke-width: 1.2px; }}
    .wf-scale-lbl {{ fill: var(--ink-soft); font-family: var(--f-tech); font-size: 8.2px; font-weight: 700; letter-spacing: 0.04em; }}
    .wf-tech-lbl {{ fill: var(--muted); font-family: var(--f-tech); font-size: 8.0px; font-weight: 600; letter-spacing: 0.04em; }}
    .wf-panel-divider {{ stroke: var(--rule-strong); stroke-width: 1px; stroke-dasharray: 3 3; }}
    .wf-subplan-kicker {{ fill: var(--ink); font-family: var(--f-tech); font-size: 10.8px; font-weight: 800; letter-spacing: 0.06em; }}
    .wf-subplan-sub {{ fill: var(--muted); font-family: var(--f-body); font-size: 9.4px; }}

    /* Campus Map */
    .wf-quad-lawn {{ fill: var(--meadow); stroke: none; }}
    .wf-bluff-contour {{ fill: none; stroke: var(--birch); stroke-opacity: 0.55; stroke-width: 1.2px; stroke-dasharray: 5 3; }}
    .wf-abbey-drive {{ fill: none; stroke: var(--muted); stroke-width: 3.2px; stroke-linecap: round; opacity: 0.45; }}
    .wf-ctx-bldg {{ fill: var(--brick-ctx); stroke: var(--ink-soft); stroke-width: 1.1px; }}
    .wf-ctx-bldg-bold {{ fill: var(--brick-ctx); stroke: var(--ink); stroke-width: 1.6px; }}
    .wf-bell-tower {{ fill: var(--gold); stroke: var(--ink); stroke-width: 1.5px; }}
    .wf-library-hero {{ fill: var(--poche); fill-opacity: 0.88; stroke: var(--poche-stroke); stroke-width: 1.6px; }}
    .wf-map-hero-lbl {{ fill: var(--ink); paint-order: stroke; stroke: var(--paper); stroke-width: 3px; stroke-linejoin: round; font-family: var(--f-tech); font-size: 10.6px; font-weight: 800; letter-spacing: 0.06em; }}
    .wf-map-lbl {{ fill: var(--ink-soft); font-family: var(--f-tech); font-size: 9.0px; font-weight: 700; letter-spacing: 0.05em; }}
    .wf-map-accent-lbl {{ fill: var(--ink); font-family: var(--f-tech); font-size: 9.2px; font-weight: 800; letter-spacing: 0.05em; }}

    /* Emblem */
    .wf-emblem-fill {{ fill: var(--zone-quiet); }}
    .wf-emblem-ray {{ stroke: var(--birch); stroke-width: 0.8px; stroke-opacity: 0.65; }}
    .wf-emblem-arc {{ fill: none; stroke: var(--sky); stroke-width: 1.1px; }}
    .wf-emblem-scoop {{ fill: none; stroke: var(--accent); stroke-width: 1.8px; }}
    .wf-emblem-outline {{ fill: none; stroke: var(--ink); stroke-width: 1.5px; }}

    /* Layer Visibility Toggles */
    .print-stage.hide-pins .layer-pins {{ display: none; }}
    .print-stage.hide-zones .layer-zones {{ display: none; }}
    .print-stage.hide-reg .layer-reg {{ display: none; }}
    .print-stage.hide-solar .layer-solar {{ display: none; }}

    /* Media Modes */
    .print-stage[data-media-mode="pure-vector"] .media-strip {{
      display: none !important;
    }}
    .print-stage[data-media-mode="duotone"] .media-strip img {{
      filter: grayscale(100%) sepia(38%) contrast(1.08);
    }}

    /* =========================================================================
       6. SECTION HEADINGS & ARTBOARD CONTAINERS
       ========================================================================= */
    .section-banner {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 16px;
      margin: 18px 0 18px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--ws-border);
      flex-wrap: wrap;
    }}
    .section-banner h2 {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #f9fafb;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .spec-pill {{
      font-family: var(--ui-mono);
      font-size: 0.70rem;
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.40);
      color: #fde68a;
    }}
    .section-banner span.sub {{
      font-size: 0.82rem;
      color: var(--ws-muted);
    }}

    /* Artboard Shared Paper Styling + Optional Crop Marks */
    .artboard {{
      position: relative;
      scroll-margin-top: 195px;
      background: var(--paper);
      color: var(--ink);
      font-family: var(--f-body);
      box-shadow:
        0 26px 60px rgba(0, 0, 0, 0.52),
        0 0 0 1px rgba(255, 255, 255, 0.08);
    }}

    .print-stage.show-crops .artboard::before,
    .print-stage.show-crops .artboard::after {{
      content: "";
      position: absolute;
      inset: -10px;
      pointer-events: none;
      border: 1px dashed rgba(245, 158, 11, 0.55);
    }}
    .crop-tag {{
      display: none;
      position: absolute;
      top: -22px;
      right: 0;
      font-family: var(--ui-mono);
      font-size: 0.65rem;
      color: #fbbf24;
      letter-spacing: 0.08em;
    }}
    .print-stage.show-crops .crop-tag {{
      display: block;
    }}

    /* =========================================================================
       7. PIECE 1 — 4" x 9" DOUBLE-SIDED VISITOR RACK CARD SPREAD
       ========================================================================= */
    .rack-spread {{
      display: flex;
      justify-content: center;
      align-items: stretch;
      gap: 36px;
      flex-wrap: wrap;
      margin-bottom: 54px;
    }}

    .rack-card {{
      width: calc(448px * var(--board-zoom));
      min-height: calc(1008px * var(--board-zoom));
      padding: 22px 22px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 12px;
      border-top: 5px solid var(--accent);
    }}

    .rc-masthead {{
      display: grid;
      grid-template-columns: 68px 1fr;
      gap: 12px;
      align-items: center;
      padding-bottom: 10px;
      border-bottom: 1.5px solid var(--rule-strong);
    }}
    .rc-kicker {{
      font-family: var(--f-tech);
      font-size: 0.64rem;
      text-transform: uppercase;
      letter-spacing: 0.11em;
      color: var(--accent);
      font-weight: 700;
    }}
    .rc-masthead h3 {{
      font-family: var(--f-display);
      font-size: 1.32rem;
      line-height: 1.08;
      font-weight: 700;
      color: var(--ink);
      margin-top: 2px;
    }}
    .rc-sub {{
      font-size: 0.72rem;
      color: var(--muted);
      margin-top: 2px;
    }}

    .rc-section-box {{
      background: var(--paper-card);
      border: 1px solid var(--rule);
      padding: 10px 10px 8px;
    }}
    .rc-box-hdr {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 6px;
      gap: 8px;
    }}
    .rc-box-hdr strong {{
      font-family: var(--f-tech);
      font-size: 0.65rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--ink);
    }}
    .rc-box-hdr span {{
      font-family: var(--f-tech);
      font-size: 0.62rem;
      color: var(--muted);
      white-space: nowrap;
    }}
    .rc-caption {{
      margin-top: 6px;
      font-size: 0.71rem;
      line-height: 1.38;
      color: var(--ink-soft);
    }}

    .rc-vignettes {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}
    .vignette-card {{
      position: relative;
      border: 1px solid var(--rule);
      overflow: hidden;
      background: var(--paper-alt);
    }}
    .vignette-card img {{
      width: 100%;
      height: 98px;
      object-fit: cover;
      display: block;
    }}
    .vignette-card figcaption {{
      padding: 4px 7px;
      font-family: var(--f-tech);
      font-size: 0.60rem;
      color: var(--ink-soft);
      background: var(--paper-card);
      border-top: 1px solid var(--rule);
    }}

    .rc-highlights {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 9px;
    }}
    .rc-hl-card {{
      padding: 8px 9px;
      background: var(--paper-card);
      border: 1px solid var(--rule);
      border-left: 3px solid var(--birch);
    }}
    .rc-hl-num {{
      font-family: var(--f-tech);
      font-size: 0.62rem;
      font-weight: 800;
      color: var(--accent);
      letter-spacing: 0.06em;
    }}
    .rc-hl-card h4 {{
      font-family: var(--f-display);
      font-size: 0.83rem;
      line-height: 1.18;
      margin: 2px 0 3px;
      color: var(--ink);
    }}
    .rc-hl-card p {{
      font-size: 0.68rem;
      line-height: 1.34;
      color: var(--ink-soft);
    }}

    .rc-footer {{
      padding-top: 9px;
      border-top: 1.5px solid var(--rule-strong);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      font-size: 0.66rem;
      color: var(--muted);
    }}
    .rc-footer strong {{
      color: var(--ink);
      font-family: var(--f-tech);
      font-size: 0.64rem;
      letter-spacing: 0.05em;
    }}

    /* Rack Card Back — Floor Plans & Directory */
    .rc-back-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 8px;
      border-bottom: 1.5px solid var(--rule-strong);
      gap: 8px;
    }}
    .rc-back-top h3 {{
      font-family: var(--f-display);
      font-size: 1.14rem;
      color: var(--ink);
    }}
    .yah-pill {{
      font-family: var(--f-tech);
      font-size: 0.62rem;
      font-weight: 800;
      padding: 3px 8px;
      background: var(--accent);
      color: var(--pin-fg);
      letter-spacing: 0.05em;
      white-space: nowrap;
    }}

    .zone-legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 5px 8px;
      background: var(--paper-alt);
      border: 1px solid var(--rule);
      font-family: var(--f-tech);
      font-size: 0.60rem;
      color: var(--ink-soft);
    }}
    .z-chip {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .z-box {{
      width: 9px;
      height: 9px;
      border: 1px solid var(--ink-soft);
      display: inline-block;
    }}

    .rc-directory {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4px 10px;
      padding-top: 4px;
    }}
    .rc-dir-item {{
      display: flex;
      align-items: flex-start;
      gap: 6px;
      padding: 3px 5px;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.14s ease;
    }}
    .rc-dir-item:hover,
    .rc-dir-item.is-active {{
      background: var(--accent-soft);
    }}
    .rc-pin-badge {{
      min-width: 17px;
      height: 17px;
      border-radius: 50%;
      background: var(--ink);
      color: var(--paper);
      font-family: var(--f-tech);
      font-size: 0.60rem;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-top: 1px;
      flex-shrink: 0;
    }}
    .rc-dir-item.is-active .rc-pin-badge,
    .rc-dir-item:hover .rc-pin-badge {{
      background: var(--accent);
      color: var(--pin-fg);
    }}
    .rc-dir-copy {{
      display: flex;
      flex-direction: column;
      line-height: 1.18;
    }}
    .rc-dir-copy strong {{
      font-size: 0.66rem;
      color: var(--ink);
    }}
    .rc-dir-copy span {{
      font-family: var(--f-tech);
      font-size: 0.57rem;
      color: var(--muted);
    }}

    /* =========================================================================
       8. PIECE 2 — 24" x 36" LOBBY ORIENTATION POSTERS (2:3 PROPORTION)
       ========================================================================= */
    .poster-grid {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 48px;
    }}

    .poster-board {{
      width: min(100%, calc(920px * var(--board-zoom)));
      min-height: calc(1360px * var(--board-zoom));
      padding: 30px 34px 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 14px;
      border-top: 8px solid var(--accent);
    }}
    .poster-board .wf-plan-l3 {{
      max-width: 555px;
      margin: 0 auto;
    }}

    .ps-masthead {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      gap: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--rule-strong);
      flex-wrap: wrap;
    }}
    .ps-series-tag {{
      font-family: var(--f-tech);
      font-size: 0.72rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 4px;
    }}
    .ps-masthead h3 {{
      font-family: var(--f-display);
      font-size: clamp(1.65rem, 2.5vw, 2.25rem);
      line-height: 1.06;
      color: var(--ink);
      font-weight: 700;
    }}
    .ps-masthead p {{
      margin-top: 5px;
      font-size: 0.83rem;
      color: var(--ink-soft);
      max-width: 590px;
    }}
    .ps-meta-block {{
      text-align: right;
      font-family: var(--f-tech);
      font-size: 0.68rem;
      color: var(--muted);
      line-height: 1.45;
    }}

    .ps-orientation-cue {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      padding: 8px 12px;
      background: var(--accent-soft);
      border: 1px solid var(--rule);
      border-left: 4px solid var(--accent);
      font-size: 0.74rem;
      color: var(--ink);
    }}
    .ps-orientation-cue div strong {{
      font-family: var(--f-tech);
      font-size: 0.66rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--accent);
      display: block;
    }}

    .ps-frame {{
      background: var(--paper-card);
      border: 1px solid var(--rule);
      padding: 11px 14px 10px;
    }}
    .ps-frame-hdr {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 6px;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .ps-frame-hdr h4 {{
      font-family: var(--f-tech);
      font-size: 0.74rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--ink);
    }}
    .ps-frame-hdr span {{
      font-family: var(--f-tech);
      font-size: 0.67rem;
      color: var(--muted);
    }}

    .ps-mid-split {{
      display: grid;
      grid-template-columns: 1.35fr 1fr;
      gap: 12px;
    }}

    .ps-dir-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
    }}
    .ps-dir-card {{
      background: var(--paper-card);
      border: 1px solid var(--rule);
      padding: 6px 8px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .ps-dir-card:hover,
    .ps-dir-card.is-active {{
      border-color: var(--accent);
      background: var(--accent-soft);
    }}
    .ps-dir-top {{
      display: flex;
      align-items: flex-start;
      gap: 6px;
      margin-bottom: 3px;
    }}
    .ps-pin-badge {{
      min-width: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--ink);
      color: var(--paper);
      font-family: var(--f-tech);
      font-size: 0.62rem;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .ps-dir-card.is-active .ps-pin-badge,
    .ps-dir-card:hover .ps-pin-badge {{
      background: var(--accent);
      color: var(--pin-fg);
    }}
    .ps-dir-head {{
      flex: 1;
      line-height: 1.15;
    }}
    .ps-dir-head strong {{
      font-size: 0.69rem;
      color: var(--ink);
      display: block;
    }}
    .ps-dir-meta {{
      font-family: var(--f-tech);
      font-size: 0.56rem;
      color: var(--muted);
    }}
    .ps-3d-chip {{
      font-family: var(--f-tech);
      font-size: 0.55rem;
      font-weight: 700;
      text-decoration: none;
      color: var(--accent);
      border: 1px solid var(--rule);
      padding: 1px 4px;
      border-radius: 4px;
      background: var(--paper);
      white-space: nowrap;
    }}
    .ps-3d-chip:hover {{
      background: var(--accent);
      color: var(--pin-fg);
    }}
    .ps-dir-card p {{
      font-size: 0.63rem;
      line-height: 1.28;
      color: var(--ink-soft);
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    /* Poster II: Detail Medallions & Render Trio */
    .medallion-trio {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
    }}
    .medallion-card {{
      background: var(--paper-card);
      border: 1px solid var(--rule);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .medallion-card h5 {{
      font-family: var(--f-display);
      font-size: 0.96rem;
      color: var(--ink);
    }}
    .medallion-card p {{
      font-size: 0.73rem;
      line-height: 1.4;
      color: var(--ink-soft);
    }}

    .ps-render-trio {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }}
    .ps-render-trio .vignette-card img {{
      height: 138px;
    }}

    /* Poster III: 4 Signature Craft Cards */
    .craft-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}
    .craft-card {{
      background: var(--paper-card);
      border: 1px solid var(--rule);
      display: grid;
      grid-template-columns: 170px 1fr;
      overflow: hidden;
    }}
    .craft-card img {{
      width: 100%;
      height: 100%;
      min-height: 148px;
      object-fit: cover;
      display: block;
      border-right: 1px solid var(--rule);
    }}
    .print-stage[data-media-mode="pure-vector"] .craft-card {{
      grid-template-columns: 1fr;
    }}
    .print-stage[data-media-mode="pure-vector"] .craft-card img {{
      display: none;
    }}
    .craft-copy {{
      padding: 11px 13px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 4px;
    }}
    .craft-copy .rc-hl-num {{
      font-size: 0.64rem;
    }}
    .craft-copy h5 {{
      font-family: var(--f-display);
      font-size: 0.98rem;
      color: var(--ink);
      line-height: 1.18;
    }}
    .craft-copy p {{
      font-size: 0.72rem;
      line-height: 1.38;
      color: var(--ink-soft);
    }}

    .ps-colophon {{
      padding-top: 10px;
      border-top: 1.5px solid var(--rule-strong);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: var(--f-tech);
      font-size: 0.66rem;
      color: var(--muted);
      flex-wrap: wrap;
      gap: 8px;
    }}

    /* =========================================================================
       9. LAYOUT VIEW MODES (ALL / RACK / POSTERS / LOBBY WALL MOCKUP)
       ========================================================================= */
    .print-stage[data-view-mode="rack"] .posters-section {{
      display: none;
    }}
    .print-stage[data-view-mode="posters"] .rack-section {{
      display: none;
    }}

    /* Architectural Lobby Wall Mockup Mode! */
    .wall-mockup-banner {{
      display: none;
    }}
    .print-stage[data-view-mode="mockup"] .rack-section,
    .print-stage[data-view-mode="mockup"] .posters-section .section-banner {{
      display: none;
    }}
    .print-stage[data-view-mode="mockup"] .wall-mockup-banner {{
      display: flex;
    }}
    .print-stage[data-view-mode="mockup"] .posters-section {{
      position: relative;
      padding: 58px 36px 96px;
      border-radius: 16px;
      /* Crisp plaster upper wall + subtle Mount Angel buff-brick wainscot band below */
      background:
        linear-gradient(180deg, #e9e4da 0%, #dfd8cb 76%, #b69474 76.2%, #ab8868 93%, #3b332b 93.2%, #2b2520 100%);
      box-shadow: inset 0 12px 48px rgba(0, 0, 0, 0.22), 0 24px 60px rgba(0, 0, 0, 0.55);
      overflow: hidden;
    }}
    .print-stage[data-view-mode="mockup"] .poster-grid {{
      flex-direction: row;
      justify-content: center;
      align-items: stretch;
      gap: 24px;
      flex-wrap: nowrap;
    }}
    .print-stage[data-view-mode="mockup"] .poster-board {{
      width: 920px;
      min-height: 1360px;
      flex: 0 0 auto;
      zoom: 0.39;
      border: 14px solid #221f1d;
      box-shadow:
        0 26px 44px rgba(0, 0, 0, 0.42),
        inset 0 0 0 2px rgba(255, 255, 255, 0.16);
    }}
    .mockup-bench {{
      display: none;
    }}
    .print-stage[data-view-mode="mockup"] .mockup-bench {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      max-width: 680px;
      margin: 42px auto 0;
      padding: 0 24px;
      position: relative;
      z-index: 5;
    }}
    .aalto-bench-slats {{
      width: 340px;
      height: 16px;
      background: repeating-linear-gradient(90deg, #c99352 0 18px, #8c5e2a 18px 21px);
      border-top: 2px solid #e0af70;
      box-shadow: 0 14px 20px rgba(0, 0, 0, 0.35);
      position: relative;
    }}
    .aalto-bench-slats::before,
    .aalto-bench-slats::after {{
      content: "";
      position: absolute;
      top: 16px;
      width: 12px;
      height: 36px;
      background: #be8847;
    }}
    .aalto-bench-slats::before {{ left: 22px; }}
    .aalto-bench-slats::after {{ right: 22px; }}
    .mockup-scale-note {{
      font-family: var(--ui-mono);
      font-size: 0.72rem;
      color: #231f1b;
      background: rgba(246, 241, 231, 0.88);
      padding: 5px 10px;
      border-radius: 6px;
      border: 1px solid rgba(35, 31, 27, 0.22);
    }}

    /* =========================================================================
       10. RESPONSIVE & PRINT (@media print)
       ========================================================================= */
    @media (max-width: 980px) {{
      .ps-mid-split,
      .ps-dir-grid,
      .medallion-trio,
      .ps-render-trio,
      .craft-grid {{
        grid-template-columns: 1fr;
      }}
      .print-stage[data-view-mode="mockup"] .poster-grid {{
        flex-wrap: wrap;
      }}
    }}

    @media print {{
      body {{
        background: #fff !important;
      }}
      .top-nav,
      .studio-header,
      .workbench-wrap,
      .section-banner,
      .mockup-bench {{
        display: none !important;
      }}
      .print-stage {{
        padding: 0 !important;
        max-width: none !important;
      }}
      .rack-spread {{
        gap: 18px !important;
        margin: 0 !important;
        page-break-after: always;
      }}
      .artboard {{
        box-shadow: none !important;
        border: 1px solid #ccc !important;
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      .poster-board {{
        width: 100% !important;
        min-height: 0 !important;
        margin-bottom: 24px;
        page-break-after: always;
      }}
    }}
  </style>
</head>
<body>
  <!-- Shared Always-Mounted SVG Gradients, Hatches & Markers -->
  {svgs["shared_defs"]}

  <!-- Unified Suite Header -->
  <header class="suite-header">
    <a href="index.html" class="suite-brand" title="Mount Angel Abbey Library — Project Overview">
      <span class="suite-crest">
        <img src="angel-logo.svg" alt="" width="24" height="19">
      </span>
      <span class="suite-brand-text">
        <span class="suite-brand-title">Mount Angel Abbey Library</span>
        <span class="suite-brand-sub">Alvar Aalto &middot; 1970</span>
      </span>
    </a>

    <nav class="suite-nav" aria-label="Project Suite">
      <a href="index.html" class="suite-link">Overview</a>
      <a href="making-of.html" class="suite-link">Making the Model</a>
      <a href="photo-compare.html" class="suite-link">Photo vs. Model</a>
      <a href="drawings.html" class="suite-link">Blueprints <span class="suite-count">47</span></a>
      <a href="visitor-guide.html" class="suite-link is-active">Visitor Guide</a>
      <a href="library-3d.html" class="suite-link suite-link-3d">&#9670; 3D Model</a>
    </nav>
  </header>

  <!-- Studio Title & Direct Print Triggers -->
  <header class="studio-header">
    <div>
      <div class="studio-eyebrow">&#10070; Parametric Architectural Wayfinding &middot; Derived Live from AaltoGeometry</div>
      <h1>Visitor Rack Card &amp; Lobby Orientation Posters</h1>
      <p>
        A flexible graphic-design workbench for Mount Angel Abbey Library&rsquo;s visitor handouts and 24&Prime;&times;36&Prime; Lobby orientation posters. Hover or click any numbered location <strong>1&ndash;12</strong> to cross-highlight rooms across every floor plan, and test palettes, typography, section <em>poch&eacute;</em>, and wall mockups in real time.
      </p>
    </div>
    <div class="studio-quick-actions">
      <button type="button" class="print-btn" id="btnPrintRack">&#128424; Print 4&Prime;&times;9&Prime; Rack Card</button>
      <button type="button" class="print-btn" id="btnPrintPosters">&#128424; Print 24&Prime;&times;36&Prime; Posters</button>
    </div>
  </header>

  <!-- Sticky Style-Honing Workbench -->
  <div class="workbench-wrap">
    <div class="workbench" id="workbench">
      <div class="wb-row">
        <div class="wb-group">
          <span class="wb-lbl">Format</span>
          <div class="pill-bar" id="viewSwitcher">
            <button type="button" class="wb-pill active" data-view="all">All Pieces (5)</button>
            <button type="button" class="wb-pill" data-view="rack">Rack Card (4&Prime;&times;9&Prime;)</button>
            <button type="button" class="wb-pill" data-view="posters">Lobby Posters (24&Prime;&times;36&Prime;)</button>
            <button type="button" class="wb-pill" data-view="mockup">Lobby Wall Mockup</button>
          </div>
        </div>

        <div class="wb-group">
          <span class="wb-lbl">Palette</span>
          <div class="pill-bar" id="themeSwitcher">
            <button type="button" class="wb-pill active" data-theme="vellum">
              <span class="swatch-dot" style="background:#f5efe4;border:2px solid #a42d21"></span>Abbey &amp; Model
            </button>
            <button type="button" class="wb-pill" data-theme="brick">
              <span class="swatch-dot" style="background:#ece0cb;border:2px solid #98261b"></span>Warm Buff-Brick
            </button>
            <button type="button" class="wb-pill" data-theme="swiss">
              <span class="swatch-dot" style="background:#faf9f5;border:2px solid #b02e21"></span>White Plaster
            </button>
            <button type="button" class="wb-pill" data-theme="basalt">
              <span class="swatch-dot" style="background:#151921;border:2px solid #c43c2d"></span>Dark Studio
            </button>
          </div>
        </div>

        <button type="button" class="wb-collapse-btn" id="wbCollapseBtn" title="Collapse or expand fine style controls">&#9650; Fine Controls</button>
      </div>

      <div class="wb-row wb-row-secondary">
        <div class="wb-group">
          <span class="wb-lbl">Type</span>
          <select class="wb-select" id="fontSelect" aria-label="Typography Voice">
            <option value="editorial" selected>Editorial Serif + Grotesk</option>
            <option value="modernist">Nordic Geometric Sans</option>
            <option value="technical">Architectural Drafting Mono</option>
          </select>

          <span class="wb-lbl">Poch&eacute;</span>
          <select class="wb-select" id="pocheSelect" aria-label="Section Poche Fill">
            <option value="solid" selected>Solid Red Poch&eacute;</option>
            <option value="hatch">45&deg; Red Hatch</option>
            <option value="outline">Red Cut Outline</option>
          </select>

          <span class="wb-lbl">Media</span>
          <select class="wb-select" id="mediaSelect" aria-label="Render Vignette Mode">
            <option value="vignettes" selected>Vector + 3D Vignettes</option>
            <option value="duotone">Editorial Duotone</option>
            <option value="pure-vector">Pure Architectural Vector</option>
          </select>
        </div>

        <div class="wb-group">
          <label class="wb-slider-group" title="Scale vector line weights across all plans &amp; sections">
            <span class="wb-lbl">Line Wt</span>
            <input type="range" id="strokeSlider" min="0.75" max="1.40" step="0.05" value="1.00">
            <span id="strokeVal">1.0&times;</span>
          </label>

          <label class="wb-slider-group" title="Zoom artboards on the desk">
            <span class="wb-lbl">Scale</span>
            <input type="range" id="zoomSlider" min="0.80" max="1.25" step="0.05" value="1.00">
            <span id="zoomVal">100%</span>
          </label>
        </div>

        <div class="wb-group">
          <label class="wb-check"><input type="checkbox" id="chkPins" checked> Pins (1&ndash;12)</label>
          <label class="wb-check"><input type="checkbox" id="chkZones" checked> Zone Tints</label>
          <label class="wb-check"><input type="checkbox" id="chkReg" checked> Compass Rays</label>
          <label class="wb-check"><input type="checkbox" id="chkSolar" checked> Daylight Rays</label>
          <label class="wb-check"><input type="checkbox" id="chkCrops"> Crop Marks</label>
        </div>
      </div>
    </div>
  </div>

  <!-- =========================================================================
       PRINT STAGE (ALL ARTBOARDS LIVE-THEMED BY DATA ATTRIBUTES)
       ========================================================================= -->
  <main class="print-stage" id="printStage"
        data-view-mode="all"
        data-print-theme="vellum"
        data-font-voice="editorial"
        data-poche-mode="solid"
        data-media-mode="vignettes">

    <!-- =======================================================================
         SECTION 1: 4" x 9" DOUBLE-SIDED VISITOR RACK CARD
         ======================================================================= -->
    <section class="rack-section">
      <div class="section-banner">
        <h2>Piece I &mdash; Visitor Rack Card <span class="spec-pill">4&Prime; &times; 9&Prime; DL Two-Sided Handout</span></h2>
        <span class="sub">Front: Skylight Cross-Section &amp; Architectural Guide &middot; Back: Heads-Up Floor Plans &amp; 1&ndash;12 Room Key</span>
      </div>

      <div class="rack-spread">
        <!-- RACK CARD FRONT -->
        <article class="artboard rack-card" id="rackFront">
          <span class="crop-tag">TRIM 4.00&Prime; &times; 9.00&Prime; &middot; FRONT</span>

          <div class="rc-masthead">
            {svgs["emblem"]}
            <div>
              <div class="rc-kicker">Visitor Architectural Guide</div>
              <h3>Architecture of Northern Light</h3>
              <div class="rc-sub">Mount Angel Abbey Library &middot; Alvar Aalto, 1970</div>
            </div>
          </div>

          <div class="rc-section-box">
            <div class="rc-box-hdr">
              <strong>Section A&ndash;A &middot; Skylights &amp; Bluff</strong>
              <span>EL. +21&prime;-6&Prime; to -26&prime;-6&Prime;</span>
            </div>
            {svgs["sec_rack"]}
            <p class="rc-caption">
              Entered modestly from the South Abbey Quad (<strong>+2&prime;-0&Prime;</strong>), the library cascades three terraced stories down the northern hillside beneath a curved <strong>+21&prime;-6&Prime; Daylight Scoop</strong> and twelve perforated conical skylights.
            </p>
          </div>

          <div class="rc-vignettes media-strip">
            <figure class="vignette-card">
              <img src="renders/studio_12_sun_summer_noon_section.png" alt="Summer Solstice Noon Section Through Skylights" loading="lazy">
              <figcaption>Summer Noon &middot; Conical Diffusers &amp; Scoop</figcaption>
            </figure>
            <figure class="vignette-card">
              <img src="renders/studio_05_sunken_well_scoop.png" alt="Mezzanine Workstations and Sunken Reading Well" loading="lazy">
              <figcaption>Sunken Reading Well &amp; -4&prime;-6&Prime; Mezzanine</figcaption>
            </figure>
          </div>

          <div class="rc-highlights">
            <div class="rc-hl-card">
              <span class="rc-hl-num">01 &middot; DAYLIGHT</span>
              <h4>Shadowless North Scoop</h4>
              <p>Steep north glass bounces cool sky light off a concave white plaster vault directly into the two-story Reading Well.</p>
            </div>
            <div class="rc-hl-card">
              <span class="rc-hl-num">02 &middot; GEOMETRY</span>
              <h4>Polycentric Birch Fan</h4>
              <p>Four subtly shifted compass origins radiate 15 variable-length birch bookcases toward the Willamette &amp; Pudding River valley.</p>
            </div>
            <div class="rc-hl-card">
              <span class="rc-hl-num">03 &middot; MILLWORK</span>
              <h4>Screens &amp; Squiggle Walls</h4>
              <p>Spot the 32-batten Lobby wood screen, 28&deg; canted wood-fin wall, serpentine catalogue wall, and radial slatted ceiling.</p>
            </div>
            <div class="rc-hl-card">
              <span class="rc-hl-num">04 &middot; HORIZON</span>
              <h4>65.7&deg; Mt. Hood Vista</h4>
              <p>Walk to northeast H-Column D: an eye-level square window frames Oregon&rsquo;s volcanic peak between tapered concrete legs.</p>
            </div>
          </div>

          <footer class="rc-footer">
            <div>
              <strong>BENEDICTINE HOSPITALITY</strong><br>
              Please preserve monastic quiet in the Reading Room &amp; Mezzanine.
            </div>
            <div style="text-align:right">
              <strong>ST. BENEDICT, OR</strong><br>
              Turn card for Floor Plans &rarr;
            </div>
          </footer>
        </article>

        <!-- RACK CARD BACK -->
        <article class="artboard rack-card" id="rackBack">
          <span class="crop-tag">TRIM 4.00&Prime; &times; 9.00&Prime; &middot; BACK</span>

          <div class="rc-back-top">
            <div>
              <div class="rc-kicker">Where Things Are</div>
              <h3>Visitor Floor Plans</h3>
            </div>
            <span class="yah-pill">&#9733; LOBBY (+2&prime;-0&Prime;)</span>
          </div>

          <div class="rc-section-box" style="padding:8px 8px 6px">
            <div class="rc-box-hdr">
              <strong>Main Entrance &amp; Fan Reading Level (+2&prime;-0&Prime; / 0&prime;-0&Prime;)</strong>
              <span>North Up &uarr;</span>
            </div>
            {svgs["l3_rack"]}
          </div>

          <div class="rc-section-box" style="padding:7px 8px 5px">
            {svgs["lower"]}
          </div>

          <div class="zone-legend">
            <span class="z-chip"><i class="z-box" style="background:var(--zone-public)"></i>Public Entry</span>
            <span class="z-chip"><i class="z-box" style="background:var(--zone-quiet)"></i>Quiet Reading</span>
            <span class="z-chip"><i class="z-box" style="background:var(--zone-lounge)"></i>Lounge / Mezz</span>
            <span class="z-chip"><i class="z-box" style="background:var(--zone-aud)"></i>Auditorium</span>
            <span class="z-chip"><i class="z-box" style="background:var(--zone-staff)"></i>Staff / Monastic</span>
          </div>

          <div class="rc-directory">
{rack_dir_html}
          </div>

          <footer class="rc-footer">
            <div><strong>FLASH-FREE PHOTOGRAPHY WELCOME</strong> &middot; Restrooms behind Wood Screen <strong>(1)</strong></div>
            <div><strong>AALTO &middot; 1970</strong></div>
          </footer>
        </article>
      </div>
    </section>

    <!-- =======================================================================
         SECTION 2: 24" x 36" LOBBY ORIENTATION POSTER SUITE (3 BOARDS)
         ======================================================================= -->
    <div class="section-banner wall-mockup-banner">
      <h2>Lobby Wall Installation Preview <span class="spec-pill">Three 24&Prime; &times; 36&Prime; Framed Boards at Scale</span></h2>
      <span class="sub">Simulated Mount Angel plaster &amp; buff-brick Lobby wall above an Alvar Aalto slatted birch bench</span>
    </div>

    <section class="posters-section">
      <div class="section-banner">
        <h2>Piece II &mdash; Lobby Orientation Poster Suite <span class="spec-pill">24&Prime; &times; 36&Prime; (2:3 Architectural Exhibition Boards)</span></h2>
        <span class="sub">Coordinated 3-poster orientation sequence for the South Entrance Lobby (+2&prime;-0&Prime;)</span>
      </div>

      <div class="poster-grid">
        <!-- ===================================================================
             POSTER 01: WELCOME, FLOOR DIRECTORY & ABBEY HILLTOP LOCATOR
             =================================================================== -->
        <article class="artboard poster-board" id="poster01">
          <span class="crop-tag">TRIM 24.0&Prime; &times; 36.0&Prime; &middot; POSTER 01 / 03</span>

          <header class="ps-masthead">
            <div>
              <div class="ps-series-tag">Lobby Orientation &middot; Board I of III</div>
              <h3>Welcome &amp; Building Directory</h3>
              <p>
                Oriented <strong>Heads-Up North</strong> to match your view from the South Entrance Lobby: step straight ahead down four wide treads into the Control Area and two-story Reading Well.
              </p>
            </div>
            <div class="ps-meta-block">
              <strong>MOUNT ANGEL ABBEY LIBRARY</strong><br>
              ALVAR AALTO, ARCHITECT (1964&ndash;1970)<br>
              45.07&deg; N &middot; 122.79&deg; W &middot; EL. +2&prime;-0&Prime; LOBBY
            </div>
          </header>

          <div class="ps-orientation-cue">
            <div>
              <strong>&larr; To Your Left (West)</strong>
              32-Batten Wood Screen &amp; Restrooms <b>(1)</b>, Public Catalogue &amp; Squiggle Walls <b>(3)</b>
            </div>
            <div>
              <strong>&uarr; Straight Ahead (North)</strong>
              Control Desk &amp; Slatted Ceiling <b>(4)</b>, Sunken Reading Well <b>(6)</b> &amp; Birch Stacks <b>(7)</b>
            </div>
            <div>
              <strong>&rarr; To Your Right (East)</strong>
              Rare Book Auditorium <b>(2)</b>, Glazed Offices &amp; Media Lounge <b>(5)</b>, Mt. Hood Vista <b>(8)</b>
            </div>
          </div>

          <div class="ps-frame">
            <div class="ps-frame-hdr">
              <h4>Main Entrance &amp; Fan Reading Deck (Level 3 &middot; +2&prime;-0&Prime; Lobby / 0&prime;-0&Prime; Reading Room)</h4>
              <span>&#9733; You Are Here in South Lobby &middot; Hover or Click Any Pin 1&ndash;12</span>
            </div>
            {svgs["l3_poster"]}
          </div>

          <div class="ps-mid-split">
            <div class="ps-frame">
              <div class="ps-frame-hdr">
                <h4>Terraced Hillside Decks Below</h4>
                <span>Mezzanine (-4&prime;-6&Prime;) &middot; Level 2 (-12&prime;-6&Prime;) &middot; Level 1 (-26&prime;-6&Prime;)</span>
              </div>
              {svgs["lower"]}
            </div>

            <div class="ps-frame">
              <div class="ps-frame-hdr">
                <h4>Mount Angel Abbey Hilltop Campus</h4>
                <span>Quad Axis &amp; South-Side Bell Tower</span>
              </div>
              {svgs["campus"]}
            </div>
          </div>

          <div class="ps-dir-grid">
{poster_dir_html}
          </div>

          <footer class="ps-colophon">
            <span>MOUNT ANGEL ABBEY &middot; ST. BENEDICT, OREGON</span>
            <span>PLEASE OBSERVE QUIET STUDY BELOW THE LOBBY STEPS</span>
            <span>SHEET I &middot; WAYFINDING &amp; CAMPUS PLAN</span>
          </footer>
        </article>

        <!-- ===================================================================
             POSTER 02: SECTION THROUGH NORTHERN LIGHT & CONSTRUCTIVE DETAILS
             =================================================================== -->
        <article class="artboard poster-board" id="poster02">
          <span class="crop-tag">TRIM 24.0&Prime; &times; 36.0&Prime; &middot; POSTER 02 / 03</span>

          <header class="ps-masthead">
            <div>
              <div class="ps-series-tag">Daylight &amp; Section &middot; Board II of III</div>
              <h3>Section Through Northern Light</h3>
              <p>
                Aalto treats the entire roof as a precision optical instrument&mdash;capturing cool, shadowless northern sky light for deep reading while baffling direct Oregon summer sun before it reaches a single page.
              </p>
            </div>
            <div class="ps-meta-block">
              <strong>LONGITUDINAL SECTION A&ndash;A</strong><br>
              SOUTH PORTICO TO NORTH BLUFF<br>
              TOTAL DROP: 48&prime;-0&Prime; (+21&prime;-6&Prime; TO -26&prime;-6&Prime;)
            </div>
          </header>

          <div class="ps-frame">
            <div class="ps-frame-hdr">
              <h4>Constructive Cross-Section Through Conical Skylights, Curved North Scoop &amp; 3&prime;-11&Prime; Steel Truss Roof Plenum</h4>
              <span>Cool Sky Wash (Blue) &middot; Baffled Conical Sun Cones (Amber)</span>
            </div>
            {svgs["sec_poster"]}
          </div>

          <div class="medallion-trio">
            <div class="medallion-card">
              <span class="rc-hl-num">DETAIL A &middot; SHEET 18-A18</span>
              <h5>Perforated Conical Skylights</h5>
              {svgs["cone"]}
              <p>
                Twelve rooftop copper-capped cones funnel sunlight through an inner perforated diffuser cone and white plaster throat, emerging cleanly through 1&Prime;&times;1&Prime; radial hemlock ceiling slats without UV hotspots.
              </p>
            </div>

            <div class="medallion-card">
              <span class="rc-hl-num">DETAIL B &middot; SHEET 30-F2</span>
              <h5>Parapet Lamps &amp; Linoleum Counter</h5>
              {svgs["lamp"]}
              <p>
                Along both the Level 3 well rim and -4&prime;-6&Prime; Mezzanine parapet, angled white stems clear the raised birch curb to suspend oblate mushroom reflectors over cantilevered matte-black linoleum counters.
              </p>
            </div>

            <div class="medallion-card">
              <span class="rc-hl-num">DETAIL C &middot; SHEETS 06-A6 &amp; 11-A11</span>
              <h5>Irregular H-Column D &amp; Vista</h5>
              {svgs["hpier"]}
              <p>
                Four monumental perimeter H-piers rotate along Aalto&rsquo;s compass rays to shelter quiet carrel alcoves; only H-Column D opens at eye level to frame Mt. Hood at <strong>65.7&deg; ENE</strong>.
              </p>
            </div>
          </div>

          <div class="ps-render-trio media-strip">
            <figure class="vignette-card">
              <img src="renders/studio_08_section_aa_ortho.png" alt="Orthographic Section A-A Stencil Cut" loading="lazy">
              <figcaption>Orthographic Section A&ndash;A &middot; 3&prime;-11&Prime; Roof Plenum</figcaption>
            </figure>
            <figure class="vignette-card">
              <img src="renders/studio_12_sun_summer_noon_section.png" alt="Summer Solstice Noon Solar Section" loading="lazy">
              <figcaption>June 21 Solar Noon (68.4&deg; Altitude)</figcaption>
            </figure>
            <figure class="vignette-card">
              <img src="renders/studio_15_sun_winter_heliodon.png" alt="Winter Solstice Heliodon Study" loading="lazy">
              <figcaption>45.07&deg; N Seasonal Solar Heliodon Arcs</figcaption>
            </figure>
          </div>

          <footer class="ps-colophon">
            <span>MOUNT ANGEL ABBEY &middot; ST. BENEDICT, OREGON</span>
            <span>NATURAL DAYLIGHTING REDUCES ELECTRIC GLARE ACROSS ALL THREE STACK DECKS</span>
            <span>SHEET II &middot; SECTION &amp; OPTICS</span>
          </footer>
        </article>

        <!-- ===================================================================
             POSTER 03: POLYCENTRIC GEOMETRY, MILLWORK & ACOUSTIC SIGNATURES
             =================================================================== -->
        <article class="artboard poster-board" id="poster03">
          <span class="crop-tag">TRIM 24.0&Prime; &times; 36.0&Prime; &middot; POSTER 03 / 03</span>

          <header class="ps-masthead">
            <div>
              <div class="ps-series-tag">Geometry &amp; Craft &middot; Board III of III</div>
              <h3>Reading Aalto&rsquo;s Signatures</h3>
              <p>
                One of only two buildings in the United States designed by Finnish master Alvar Aalto, Mount Angel unites severe rectilinear monastic masonry on the quad with a free, organic fan facing nature.
              </p>
            </div>
            <div class="ps-meta-block">
              <strong>POLYCENTRIC REGULATING SYSTEM</strong><br>
              4 WORKING ORIGINS &middot; 3 ROOF TIERS<br>
              CUSTOM FINNISH BIRCH &amp; HEMLOCK MILLWORK
            </div>
          </header>

          <div class="ps-frame">
            <div class="ps-frame-hdr">
              <h4>Four Shifted Compass Origins &amp; Three-Tier Roof Hierarchy</h4>
              <span>WP #4 (0,0) &middot; WP #3 (0,+1&prime;) &middot; WP #3A (+1.5&prime;,+2.6&prime;) &middot; WP_DESK (-1.2&prime;,+2.2&prime;)</span>
            </div>
            {svgs["polycentric"]}
          </div>

          <div class="craft-grid">
            <div class="craft-card">
              <img src="renders/studio_03_roof_cutaway_axon.png" alt="Roof Cutaway Showing Wood Screen and Squiggle Walls" loading="lazy">
              <div class="craft-copy">
                <span class="rc-hl-num">SIGNATURE I &middot; THRESHOLD &amp; ACOUSTICS</span>
                <h5>Wood Screen &amp; Twin Squiggle Walls</h5>
                <p>
                  In the Lobby, 32 vertical wood battens veil the restroom doors in warm shadow. Steps away, a 28&deg;-canted wood-fin screen and an S-curved plaster wall diffuse footsteps before they enter the Reading Well.
                </p>
              </div>
            </div>

            <div class="craft-card">
              <img src="renders/studio_19_control_glass_wall.png" alt="Control Desk Slatted Ceiling and 14-Bay Glazed Wall" loading="lazy">
              <div class="craft-copy">
                <span class="rc-hl-num">SIGNATURE II &middot; TRANSPARENCY</span>
                <h5>14-Bay Birch Glass Wall &amp; Ceiling Drum</h5>
                <p>
                  Fourteen 40&Prime; birch-mullioned clear glass bays sit atop a black-capped white wainscot, sharing borrowed north light with the Director&rsquo;s Office and Periodical Lounge beside the radial slatted ceiling.
                </p>
              </div>
            </div>

            <div class="craft-card">
              <img src="renders/studio_04_mezzanine_counter_pov.png" alt="Variable-Length Aalto Birch Bookcases and Workbench" loading="lazy">
              <div class="craft-copy">
                <span class="rc-hl-num">SIGNATURE III &middot; PARAMETERIZED MILLWORK</span>
                <h5>Variable-Length Birch Bookcases</h5>
                <p>
                  Almost every stack row has its own bespoke length (16.3&prime;&ndash;20.0&prime;) to preserve organic sightlines, crafted on ~3&prime;-1&Prime; bays with recessed black-linoleum kicks and 5-batten directory stanchions.
                </p>
              </div>
            </div>

            <div class="craft-card">
              <img src="renders/studio_20_auditorium_cutaway.png" alt="Rare Book Auditorium Cutaway View" loading="lazy">
              <div class="craft-copy">
                <span class="rc-hl-num">SIGNATURE IV &middot; SCULPTURAL SOUND</span>
                <h5>Rare Book Auditorium (Rm 327)</h5>
                <p>
                  Beneath its own taller <strong>+18&prime;-8&Prime;</strong> dark-membrane roof, a three-wave undulating plaster shell projects unamplified voice from the quarter-circle SE birch stage across fanned seating rows.
                </p>
              </div>
            </div>
          </div>

          <footer class="ps-colophon">
            <span>MOUNT ANGEL ABBEY &middot; ST. BENEDICT, OREGON</span>
            <span>EXPLORE THE FULL 134,459-FACE 3D DIGITAL MAQUETTE AT LIBRARY-3D.HTML</span>
            <span>SHEET III &middot; GEOMETRY &amp; CRAFT</span>
          </footer>
        </article>
      </div>

      <!-- Scale Aalto Birch Bench shown in Lobby Wall Mockup Mode -->
      <div class="mockup-bench">
        <div class="aalto-bench-slats" title="Alvar Aalto Slatted Birch Lobby Bench (Scale Reference)"></div>
        <div class="mockup-scale-note">24&Prime; &times; 36&Prime; Posters Hung at +62&Prime; Eye-Center Above Lobby Bench</div>
      </div>
    </section>
  </main>

  <script>
    (function () {{
      const stage = document.getElementById('printStage');
      const workbench = document.getElementById('workbench');
      const collapseBtn = document.getElementById('wbCollapseBtn');

      // 1. Format / View Mode Switcher
      document.querySelectorAll('#viewSwitcher .wb-pill').forEach((btn) => {{
        btn.addEventListener('click', () => {{
          document.querySelectorAll('#viewSwitcher .wb-pill').forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
          stage.dataset.viewMode = btn.dataset.view;
        }});
      }});

      // 2. Live Print Palette Switcher
      document.querySelectorAll('#themeSwitcher .wb-pill').forEach((btn) => {{
        btn.addEventListener('click', () => {{
          document.querySelectorAll('#themeSwitcher .wb-pill').forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
          stage.dataset.printTheme = btn.dataset.theme;
        }});
      }});

      // 3. Selectors: Font Voice, Poche Mode, Media Mode
      document.getElementById('fontSelect').addEventListener('change', (e) => {{
        stage.dataset.fontVoice = e.target.value;
      }});
      document.getElementById('pocheSelect').addEventListener('change', (e) => {{
        stage.dataset.pocheMode = e.target.value;
      }});
      document.getElementById('mediaSelect').addEventListener('change', (e) => {{
        stage.dataset.mediaMode = e.target.value;
      }});

      // 4. Line Weight & Artboard Zoom Sliders
      const strokeSlider = document.getElementById('strokeSlider');
      const strokeVal = document.getElementById('strokeVal');
      strokeSlider.addEventListener('input', () => {{
        const v = parseFloat(strokeSlider.value);
        stage.style.setProperty('--stroke-scale', v.toFixed(2));
        strokeVal.textContent = v.toFixed(2) + '×';
      }});

      const zoomSlider = document.getElementById('zoomSlider');
      const zoomVal = document.getElementById('zoomVal');
      zoomSlider.addEventListener('input', () => {{
        const z = parseFloat(zoomSlider.value);
        stage.style.setProperty('--board-zoom', z.toFixed(2));
        zoomVal.textContent = Math.round(z * 100) + '%';
      }});

      // 5. Layer Toggles
      const bindToggle = (id, cls, invert = false) => {{
        const el = document.getElementById(id);
        el.addEventListener('change', () => {{
          const on = invert ? el.checked : !el.checked;
          stage.classList.toggle(cls, on);
        }});
      }};
      bindToggle('chkPins', 'hide-pins');
      bindToggle('chkZones', 'hide-zones');
      bindToggle('chkReg', 'hide-reg');
      bindToggle('chkSolar', 'hide-solar');
      bindToggle('chkCrops', 'show-crops', true);

      // 6. Collapse / Expand Fine Controls
      collapseBtn.addEventListener('click', () => {{
        const collapsed = workbench.classList.toggle('collapsed');
        collapseBtn.innerHTML = collapsed ? '&#9660; Fine Controls' : '&#9650; Fine Controls';
      }});

      // 7. Bidirectional Interactive Pin 1..12 Highlighting
      let lockedPin = null;
      const syncPinHighlight = (pinId) => {{
        document.querySelectorAll('[data-pin]').forEach((el) => {{
          el.classList.toggle('is-active', el.dataset.pin === pinId);
        }});
        document.querySelectorAll('[data-pin-link]').forEach((el) => {{
          el.classList.toggle('is-active', el.dataset.pinLink === pinId);
        }});
      }};

      document.querySelectorAll('[data-pin], [data-pin-link]').forEach((el) => {{
        const pid = el.dataset.pin || el.dataset.pinLink;
        el.addEventListener('mouseenter', () => {{
          syncPinHighlight(pid);
        }});
        el.addEventListener('mouseleave', () => {{
          syncPinHighlight(lockedPin);
        }});
        el.addEventListener('click', (ev) => {{
          if (ev.target.closest('a')) return;
          lockedPin = lockedPin === pid ? null : pid;
          syncPinHighlight(lockedPin);
        }});
      }});

      // 8. CleanTargeted Print Triggers
      const printMode = (mode) => {{
        const prev = stage.dataset.viewMode;
        stage.dataset.viewMode = mode;
        window.print();
        setTimeout(() => {{
          stage.dataset.viewMode = prev;
        }}, 250);
      }};
      document.getElementById('btnPrintRack').addEventListener('click', () => printMode('rack'));
      document.getElementById('btnPrintPosters').addEventListener('click', () => printMode('posters'));

      // Optional URL query params (?theme=brick&view=mockup)
      const params = new URLSearchParams(window.location.search);
      const qTheme = params.get('theme');
      if (qTheme) {{
        const tb = document.querySelector(`#themeSwitcher [data-theme="${{qTheme}}"]`);
        if (tb) tb.click();
      }}
      const qView = params.get('view');
      if (qView) {{
        const vb = document.querySelector(`#viewSwitcher [data-view="${{qView}}"]`);
        if (vb) vb.click();
      }}
      const qPoche = params.get('poche');
      if (qPoche) {{
        const ps = document.getElementById('pocheSelect');
        ps.value = qPoche;
        stage.dataset.pocheMode = qPoche;
      }}
    }})();
  </script>
</body>
</html>
"""


def write_visitor_guide(repo_root: Path | None = None) -> Path:
    """Generate and write `docs/visitor-guide.html` inside the repository."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    out_path = repo_root / "docs" / "visitor-guide.html"
    out_path.write_text(render_visitor_guide_html(), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    written = write_visitor_guide()
    print(f"Wrote {written} ({written.stat().st_size:,} bytes)")
