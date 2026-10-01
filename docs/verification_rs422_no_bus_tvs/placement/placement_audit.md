# 37-component placement — mechanical checks pass

D2 and D4 were removed. U1 remains at (0, 0), 0° on the top; all other 36 components are on the bottom. Coordinates are in millimetres with positive Y down and KiCad orientation degrees, applied after the bottom-side flip.

- Courtyard overlaps: 0; physical body overlaps: 0.
- Minimum pad-to-pad copper gap: 0.298285 mm (required 0.15 mm).
- Minimum copper-to-board-edge clearance: 0.305327 mm (required 0.30 mm).
- Maximum body radius: 6.609147 mm (board radius 6.75 mm).
- Maximum courtyard radius: 6.992833 mm (permitted up to 7.00 mm).
- Exact checks were repeated from the saved 8-decimal coordinates.

Candidate: `placement_candidate.json`; orientation geometry: `geometry.json`; exact audit: `placement_audit.json`.

This confirms placement geometry only. The candidate still needs net assignment, routing, and KiCad DRC before PCB/manufacturing promotion. Circuit values were not modified.
