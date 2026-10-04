# Finite NRST/C5 check

Best frozen PCB remains `../uart-complete/kicad/ppg_pcb_v08.kicad_pcb`: DRC errors 0; one NRST connection unfinished. This investigation did not change that PCB, the actual repository, BOM, or Gerber files.

C5 search: 728 poses, 52 mechanically legal, 7 provisionally legal against the current copper and via holes. Exact poses are in `left-feasible-poses.json`. These exclude the new NRST via (-0.5, 2.4), so they are not final routing solutions. The requested pose (-1.4, 2.4258), 180° fails at 0.0246549 mm foreign copper clearance due to nearby 5V_LED copper.

J9 search: radius 0.55–0.90 mm around (-3.2955, 1.4062), 0.025 mm grid, 2540 candidates. With C5 temporarily removed and 5V_LED F.Cu tracks removed, 2488 candidates fail foreign copper clearance and the remaining 52 fail the 0.025 mm nominal drill-to-pad gap with a 0.001 mm search margin. No legal candidate remained for a route attempt. Eleven compatible items from the earlier NRST solution were retained in memory; three conflicting terminal items were excluded. See `j9-ring-results.json`.

No search expansion or final manufacturing output was performed. The finite local check did not solve NRST.
