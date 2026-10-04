# RS-422 mechanical candidate — not feasible

This is the best recorded candidate from the final strict geometry search. It is exploratory evidence only and must not be promoted to the PCB or used for manufacturing. The candidate has 39 components: U1 alone on the top and 38 on the bottom.

| Exact check | Result | Limit |
|---|---:|---:|
| Bottom courtyard sum | 118.924434 mm² | PCB circle 143.138815 mm² |
| Courtyard overlap | 0.513177 mm² across 44 pairs | 0 |
| Maximum copper radius | 6.487091 mm | ≤6.450000 mm |
| Minimum copper-to-edge clearance | 0.262909 mm | ≥0.300000 mm |
| Maximum physical body radius | 6.505333 mm | ≤6.750000 mm |
| Maximum courtyard radius | 6.868650 mm | ≤7.000000 mm |
| Body overlap pairs | 0 | 0 |
| Pad copper gap below 0.15 mm | 0 | 0 |

Copper edge violations: C14, C6, C7, D1, FB1, J2, J3, J4, J5, J6, R3.

The largest courtyard overlap is D4–R8 (0.144088 mm²), followed by J2–U4 (0.053836 mm²) and FB1–U3 (0.042516 mm²). All 44 overlapping pairs and all radius violations are listed in `mechanical_candidate_assessment.json`.

Courtyards retain their original geometry. Cable and test pads, which have no explicit library courtyard, use a 0.15 mm margin around copper. The final search used 45-degree orientations, zero anchor/link preference weights and progressively increased physical-edge penalties. Body constraints and the copper clearance requirement were preserved; courtyard overhang up to 0.25 mm was permitted.

This bounded search did not find a valid layout. It does not prove that a 13.5 mm layout is impossible. No candidate PCB or fabrication output was promoted.

Candidate: `packing_strict_best.json`  
Candidate SHA-256: `95d9c8068b0f0b0511ca408d00d770494a73f921b54c0765b2f53cc1873843b5`  
Geometry: `packing_geometry_physical.json`  
Geometry SHA-256: `decd3631b51500bb6cff86787ae325c2378f71cdacd3383167c65e1842ca838c`
