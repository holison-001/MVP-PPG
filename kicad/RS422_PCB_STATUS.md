# SleepBud PPG PCB v0.8 — C17 변경 배치 재배선 (2026-10-08)

사용자가 저장한 C17 바닥면 (20.5000,19.9000)mm/90° 배치를 유지하고, 이동한 GND 패드와 기존 5V 비아·배선의 간섭을 해소했습니다. 5V_LED 및 GND의 연결 경로를 다시 정리했습니다. C17은 100nF, 미터 0603이며 핀 1=5V_LED, 핀 2=GND입니다.

간섭이 있던 5V 비아를 제거하여 전체 비아는 66→65개입니다. C17 전원은 1.138mm, GND는 0.830mm 직선으로 연결했습니다. C1의 1.933mm 연결 중 1.145mm는 선폭 0.30mm, 간격이 좁은 0.788mm 구간은 0.15mm입니다. 기존 부품과 다른 네트 배선을 유지하는 경로를 택해 5V_LED 동박 총길이는 10.382→11.589mm로 1.207mm 늘었습니다.

기존 42개 부품의 위치·각도·패드 형상과 연결을 보존하고, 변경 범위를 5V_LED/GND 동박으로 제한했습니다. 사용자가 조정한 SCL/SDA 등 다른 신호 배선과 회로도·프로젝트·규칙은 유지했습니다. 전층 GND를 다시 채웠고 15/15 GND 영역 연결, 1~5층 외곽 GND 연속성을 확인했습니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 42개 부품·125개 번호 핀의 회로도/PCB 일치, 다중 핀 네트 연결, 기존 ESD 경로 및 부품 간섭 검사를 통과했습니다.

[C17 배선 전후](../docs/review_C17_reroute_20261008/placement_reroute_comparison.png) · [검증 기록](../docs/verification_C17_reroute_20261008/). PCB SHA256: `eae91e981d70ecab493e7879cb164b4153b4c0e78430ac3255dfbea034b25f30`. 백업: `backups/20261008_before_C17_reroute/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — C17 PCB 추가 (2026-10-08)

최신 회로도에 추가된 C17을 PCB에 반영했습니다. 값은 100nF, 풋프린트는 Capacitor_SMD:C_0201_0603Metric(미터 0603, 0.6×0.3mm), 핀 1은 5V_LED, 핀 2는 GND입니다. C17은 바닥면 (20.7500,19.6550)mm/-90°에 배치하고 전원과 GND를 연결했습니다. 회로도의 C17 Description 필드는 복사된 문구인 "U2 VDD bypass"로 남아 있으나, PCB에는 실제 회로도 네트인 5V_LED–GND를 반영했습니다.

기존 41개 부품의 배치·패드와 모든 기존 배선 형상을 보존했습니다. 회로도·프로젝트·규칙 파일도 변경하지 않았으며, C17 항목을 부품 데이터에 추가했습니다. 전층 GND를 다시 채웠고, 14/14 GND 영역 연결과 1~5층 외곽 GND 연속성을 확인했습니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 총 42개 부품·125개 번호 핀의 회로도/PCB 일치, 네트 연결과 기존 ESD 경로를 검사했습니다. C17 조립 영역과 주변 부품 간섭 검사를 통과했습니다.

[C17 배치 보기](../docs/review_C17_20261008/placement_reroute_comparison.png) · [검증 기록](../docs/verification_C17_20261008/). PCB SHA256: `b397c72e3ba9275c58eccc9b854cc602f6b2ea16302c17b6da636f57b90675ac`. 백업: `backups/20261008_before_C17_addition/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — RXN/RXP 패드 교환 및 재배선 (2026-10-08)

사용자가 변경한 R3 (14.1029,17.0)mm/90°, R7 (15.6,17.6)mm/180°, R8 (15.6,16.3)mm/180° 배치를 유지했습니다. 요청에 따라 바닥면 외부 패드 J6/RXN은 위쪽 (15.0655,13.9497)mm, J5/RXP는 아래쪽 (14.8181,19.6172)mm으로 서로 위치를 바꿨습니다. 각 패드의 참조번호·네트·각도는 보존했으며 나머지 39개 부품과 탑면 센서는 움직이지 않았습니다.

RXN/RXP 및 수신 IC까지의 RXN_RCV/RXP_RCV 경로를 재배선했습니다. RXP는 J5→R7→U6.6(A), RXN은 J6→R8→U6.4(B)로 연결하고, R3.1은 RXP, R3.2는 RXN의 연결을 유지했습니다. 사용자가 수정한 SCL 배선을 포함한 다른 네트의 배선 형상과 회로도는 보존했습니다.

수신 네트 4개 동박 길이 합계 19.139→14.801mm. 전체 비아 65→63개. 길이는 비아 수직 길이를 제외한 값입니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 전층 GND 채움 완료, 13/13 GND 동박 영역 연결. 부품 간 조립 영역·몸체·패드 간섭 및 극성 검증 통과. 123핀 회로도 연결, 다중 핀 23네트와 기존 ESD 3경로도 검사했습니다. 6층 구성, 2층 무배선, 외곽 GND와 선폭·비아 규칙을 유지했습니다.

[배선 전후](../docs/review_placement_reroute_20261008e/placement_reroute_comparison.png) · [검증 기록](../docs/verification_placement_reroute_20261008e/). PCB SHA256: `2ef282c3a06786d3a7ee80a30bc4c60e2382d900a44287dbae603c8d80d230de`. 백업: `backups/20261008_before_placement_reroute_e/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — C11/C15 수정 배치 재배선 (2026-10-08)

사용자가 옮긴 C11은 NRST 배선 통로 확보를 위해 바닥면에서 아래로 0.20mm 미세 조정하여 (18.0,19.6)mm/180°에 배치했습니다. U4는 조립 간격과 원형 보드 외곽 여유를 확보하도록 오른쪽 0.40mm, 아래로 0.20mm 옮겨 (18.7257,21.7439)mm/180°에 배치했습니다. 앞서 허용한 바닥면 간섭 미세 조정 범위이며 C15 (19.4,19.4)mm/0°와 U1·D8을 포함한 나머지 39개 부품은 유지했습니다. 전체 151개 패드의 형상·네트를 보존하고, 영향을 받은 전원·GND·NRST 경로를 정리했습니다.

C11/C15의 전원 연결과 MCU 급전을 다시 정리하고, 이전 위치로 향하는 불필요한 배선을 제거했습니다. 5V_LED의 잘게 나뉜 꺾임은 직선·원호로 정리했습니다. NRST는 외부 패드→D8 신호 접점→MCU 순서가 유지되는지 접점 제거 검사를 통과했습니다.

저장된 PCB의 실제 형상 기준으로 같은 면 부품 간 조립 영역·몸체·패드 겹침은 0건입니다. U4 몸체와 원형 보드 외곽 사이 여유는 0.1048mm, 동박 패드 여유는 0.5585mm입니다. U4 조립 영역 표시(Courtyard)는 외곽 밖으로 0.2108mm 돌출하며(이전 0.1834mm), 실제 부품 몸체는 보드 안에 있습니다.

평면 배선 합계: 3.3V 40.650→36.175mm, 5V_LED 10.536→9.351mm, 12V 14.724→14.163mm, NRST 5.564→5.200mm. 전체 비아 65→65개. 길이는 비아 수직 길이를 제외한 동박 합계이며, 모든 네트가 짧아졌다는 의미는 아닙니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 전층 GND 채움, 13/13 GND 동박 영역 연결, ESD 3경로·회로도 123핀·다중 핀 23네트 검사 통과. 2층 무배선, 1~5층 외곽 GND, 선폭·비아 규칙을 유지했습니다. 회로도·프로젝트·규칙과 관련 없는 배선은 보존했습니다.

[배선 전후](../docs/review_placement_reroute_20261008d/placement_reroute_comparison.png) · [검증 기록](../docs/verification_placement_reroute_20261008d/). PCB SHA256: `bbd74454cdfd2f07445fb08227b9e11855be98583af45f1e497f3e75ff5221ce`. 변경 전 백업: `backups/20261008_before_placement_reroute_d/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — 3.3V 전체 경로 정리 (2026-10-08)

사용자가 수정한 C14 배치와 SWCLK 경로를 포함해 41개 부품의 위치·각도·면 및 신호 배선을 그대로 유지했습니다. 3.3V 연결망 전체를 다시 구성해 중복 급전 루프, 중앙 VREF 주변 우회와 서쪽의 긴 돌아가는 경로를 정리했습니다. U3–C16은 직결하고 필요한 방향 전환에는 원호를 적용했습니다. C14 전원 비아와 이전 꼬리 배선을 정리해 GND 패드와의 접촉을 해소했습니다.

3.3V 평면 배선 합계 **50.095 → 40.764 mm**, **18.6% 감소**. 4층 3.3V는 **35.293 → 26.266 mm**, 동박 요소 45→27개입니다. 전원 비아는 8→8개이며, 전체 비아는 65개입니다. 길이는 비아 수직 길이를 제외한 평면 동박 합계입니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 전층 GND 채움, 15/15 GND 동박 영역 연결, ESD 3경로·회로도 123핀·다중 핀 23네트 검사 통과. 2층 무배선, 1~5층 외곽 GND, 선폭·비아 규칙을 유지했습니다. 회로도·프로젝트·규칙은 변경하지 않았습니다.

[3.3V 배선 전후](../docs/review_3V3_cleanup_20261008c/3V3_cleanup_comparison.png) · [검증 기록](../docs/verification_3V3_cleanup_20261008c/). PCB SHA256: `2f48cc14bab60c231189b33674a6b2a69fc755beff8a993c0c3906d5b9a2893a`. 변경 전 백업: `backups/20261008_before_3V3_cleanup/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — U3/R4/R5/C6/C16 수정 배치 재배선 (2026-10-08)

사용자가 조정한 U3, R4, R5, C6, C16을 포함해 41개 부품의 위치·각도·면과 151개 패드 형상·네트를 그대로 유지했습니다. 변경 전 파일은 `backups/20261008_before_placement_reroute_b/kicad_before_reroute.zip`에 백업했습니다.

이동 전 패드로 향하는 배선을 제거하고 UART_TX, TXP/TXN, 3.3V와 GND 귀환을 새 배치에 맞춰 연결했습니다. 이동한 패드와 겹쳐 신호 네트로 재지정된 기존 GND 비아/배선도 제거하고 필요한 GND 연결을 다시 확보했습니다. TXP는 바닥면으로 연결하고 TXN은 3층을 이용합니다. 새 배치의 평면 배선 합계는 TXP 5.765 mm, TXN 7.755 mm, UART_TX 9.604 mm입니다. 기존 위치와 경로 조건이 다르므로 모든 신호의 길이가 줄었다는 의미는 아닙니다. 전체 비아는 65개입니다.

C16의 GND 비아는 (24.15,15.85)mm, 3.3V 비아는 (24.65,15.35)mm로 나눠 배치했습니다. 전원 연결의 0.650mm 병목 구간만 0.15mm 선폭을 적용하고 양끝은 0.30mm, 4층 공급선은 0.40mm를 유지했습니다. 기존 동쪽 C6 전원 분기를 제거했고, R4 전원은 0.760mm 직선입니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 전층 GND 채움, 15/15 GND 동박 영역 연결, ESD 3경로·회로도 123핀·다중 핀 23네트 검사 통과. 2층 무배선, 1~5층 외곽 GND, 선폭·비아 규칙을 확인했습니다. 회로도·프로젝트·규칙과 관련 없는 배선은 보존했습니다.

[배선 전후](../docs/review_placement_reroute_20261008b/placement_reroute_comparison.png) · [검증 기록](../docs/verification_placement_reroute_20261008b/). PCB SHA256: `91a72755b21ff8630c9eac5422dce37eba7e7a8c27bb0fce6ad39a48cbc9a3b1`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# Current RS-422 PCB — route the user's C5/R2/R1 column (2026-10-08)

Canonical PCB SHA256: `4a753412db677bffd4155f628a6ae2fa6ba472ef047550a04ff7c33ec5107719`.

Preserved all 41 component placements and all 151 pad identities from user source `d846727bc1072eb4670b2364c6f00038f31e0101b5c887cce5076438363aad64`. C5 is at (21.2,16.2)mm/180 degrees, R2 at (21.2,16.9)mm/0 degrees, R1 at (21.2,17.6)mm/0 degrees. No placement overrides were applied.

Removed ten stale B.Cu I2C pullup routing objects and added two straight links. SDA shares the existing MCU-to-via trace before branching to R1. SCL connects the MCU directly to R2. SDA planar length falls from 6.849856 to 5.904380mm, SCL 7.859719 to 7.320044mm. Existing sensor-side F.Cu/In4.Cu paths and all three I2C vias remain unchanged after evaluating the broader routing constraints.

The old 3V3 via position (21.7,15.7)mm now serves VREF; the old VREF via position (22.1,17.55)mm serves 3V3. VREF shortens 2.036822 to 1.589224mm. C5 ground shares the existing C4 ground return, for a full C5-to-via path of 1.611975mm. R1/R2 power bus and R4 feed are straight. Local 0.40mm In3.Cu copper clears VREF and feeds the new 3V3 landing. The required power branch increases 3V3 length 45.095459 to 47.041884mm; total board planar trace length changes 183.782441 to 183.126220mm. Via count stays 65.

Native DRC: errors 0, unconnected 0, schematic parity 0; same four silk-edge and one U2 library-footprint warnings. All 123 pins match the schematic, all 23 multi-pin nets are connected, and all three ESD pad-cut checks pass. Six GND layers refilled; all 16 GND groups reach J2.1. Layer/rim/width/via policies pass. Schematic, project, rules, component geometry and unrelated copper are preserved.

[Before/after](../docs/review_placement_route_20261008/placement_route_comparison.png) · [Verification](../docs/verification_placement_route_20261008/). Backup: `backups/20261008_before_R1_R2_C5_reroute/kicad_before_R1_R2_C5.zip`. Saved to canonical local PCB. No Gerber generation or GitHub publication.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# Current RS-422 PCB — TX resistor location swap (2026-10-08)

Canonical PCB SHA256: `245b0b48098faec4ebdd3d13e3f7ad531b1e78041a6bfc9b882eddd679ae5507`.

Swapped B.Cu R5/TXP and R6/TXN while preserving references, 22-ohm 1005 footprints, pad identities and circuit nets. R5 is at (24.7408,16.8914)mm/315 degrees; R6 is at (23.7,18.2)mm/270 degrees. TXP now routes entirely on B.Cu. Both external output legs are direct B.Cu connections. TXN uses two vias and one straight In2.Cu span. Old In4.Cu TX routing is removed.

TXP planar length: 12.232672 to 4.938654mm. TXN: 7.751520 to 7.463730mm. Combined length reduces 37.94%, and TX vias fall from six to two. Total board vias: 65. The latest user R4/C5 placement is retained with only R4 (+0.20,+0.20)mm and C5 (0,+0.05)mm shifts to resolve local assembly/copper clearances; their four unfinished connections are restored.

Native DRC: errors 0, unconnected 0, schematic parity 0; four prior silk-edge warnings plus the prior U2 library-footprint warning remain. No new body/courtyard overlaps. All original 151 physical pad identities and 123 pin nets are preserved; all 23 multi-pin nets are connected. ESD pad-cut tests pass for D6/D7/D8. Six GND zones refilled, all 16 copper groups reach J2.1, layer/rim/width/via policies pass. All top components and unrelated source copper remain unchanged; schematic/project/rules unchanged.

[Before/after](../docs/review_tx_swap_20261008/tx_swap_comparison.png) · [Verification](../docs/verification_tx_swap_20261008/). Backup: `backups/20261008_before_TX_resistor_swap/kicad_before_TX_swap.zip`. Saved to canonical local PCB; no Gerber generation or GitHub publication.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# Current RS-422 PCB — U2 west relocation and C4 routing (2026-10-08)

Canonical PCB SHA256: `0db206e568dc9441220bb5e9327dbec5d7b70599d49fd8e6ac2166f2f1b90cc9`.

U2 moves 1.8 mm west to (18.3419,17.2749) mm, 90 degrees. C4 moves to (20.4,15.1) mm, 0 degrees, on B.Cu. R1/R2/R4/C1/C15/D8 are rearranged; every F.Cu footprint remains fixed. The VLDO planar routed length falls from 3.153 to 2.345 mm. Local signal, power and ground routes are rebuilt together, preserving unrelated original copper. SCL's top detour uses four lines and three tangent arcs. Total vias: 69, previously 71.

Native DRC: errors 0, unconnected 0, schematic parity 0; the same four silk-edge warnings and one U2 library-footprint warning remain. No new or increased assembly courtyard overlap or component body overlap. All 123 schematic pins match, all 23 multi-pin nets are connected, and all three external-pad/TVS/MCU paths pass pad-cut topology checks. All six GND zones are filled, all 15 GND copper components reach J2.1, and layer/rim/width/via policies pass. Schematic, project and rules are unchanged.

[Before/after](../docs/review_u2_c4_20261008/u2_c4_comparison.png) · [Verification](../docs/verification_u2_c4_20261008/). Detailed per-net length changes are recorded; relocation shortens C4, RX, SDA and NRST, while some other signal and power routes grow to accommodate the west placement. This is a reviewed space-use change, not a claim that every route became shorter.

The latest source is backed up at `backups/20261008_before_U2_C4_apply/kicad_before_U2_C4.zip`. Saved to the canonical local PCB. No Gerber generation or GitHub publication in this turn.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# Current RS-422 PCB — connection cleanup (2026-10-07)

Canonical PCB SHA256: `6f5485a1f81b4cb11914d462fbb74e58576903f7c1595e6b5ecb7f60054ed806`.

Preserved the user's latest 41-footprint placement. NRST now follows J9 → existing entry via → D8 signal landing → new protected via (17.15,19.20)mm → In2.Cu → U2.4. D8 remains B.Cu at (16.6,19.0)mm, 90 degrees. The added signal via is 0.50/0.20mm; all original vias retain their positions. Total vias: 71. R4 and fixed top sensor U1 are unchanged.

Added the explicit C13.1-to-12V-via connection, 0.15mm wide and 0.5521mm long. Preserved the user's restored 12V-via-to-U4.8 tracks. Added D8-to-existing-GND-via trace, 0.30mm wide and 0.8591mm long. Existing non-NRST routing remains unchanged.

Native DRC: errors 0, unconnected 0, schematic parity 0, same five prior warnings. Schematic/net and all three ESD flow checks pass; cutting D8's signal-pad copper also disconnects J9 from U2.4. All six GND zones refilled; all 15 GND copper graph nodes reach J2.1. Layer/rim/width/via policies pass. Schematic, project and rule files are unchanged.

[Before/after](../docs/review_routing_connections_20261007/connections_before_after.png) · [Verification](../docs/verification_routing_connections_20261007/).

Saved to canonical local PCB; no Gerber, drill, BOM or Git publication.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# Current RS-422 PCB — SCL direct top connection (2026-10-06)

Canonical PCB SHA256: `5c4c9d1eabbfb2f3db410d5fa80927defbf1545fe8b773ff937ddca9fa6ac063`.

R2's existing SCL via now connects directly to U1.2 on F.Cu: 1.999→0.798mm. The In2.Cu detour is shortened from 5.753 to 4.182mm using two lines and one arc. Total SCL routed length is 9.352→6.580mm, reduced by 2.773mm. The redundant upper SCL via is removed; 69 vias remain.

All 41 footprints and pads, remaining vias and routing outside SCL are unchanged. Fixed U1, bottom D8 and all ESD pad-first paths are preserved. Native DRC: errors 0, unconnected 0, schematic parity 0; same five existing warnings. Netcheck and three ESD flow checks pass. All six GND zones are filled and all 13 GND graph nodes reach J2.1. Ground rim, layer, trace width and via rules pass. No schematic, project or rule changes.

[SCL before/after](../docs/review_scl_top_20261006/scl_before_after.png) · [Verification](../docs/verification_scl_top_20261006/).

Saved to the canonical local PCB. No Gerber, drill, BOM or Git publication was performed.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# Current RS-422 PCB — TVS pad-first routing (2026-10-06)

Canonical PCB SHA256: `9caf20e4383d00f97e604291ab7e9c29394bed81c2da8c6ed2c2addbab580384`.

J7/SWDIO and J8/SWCLK now reach D6.1 and D7.1 before their internal signal vias. The external and protected traces enter opposite edges of each TVS signal landing. D8 stays at its unchanged bottom placement: J9 reaches an entry via, then D8.1, then the protected route to U2.4. The former NRST bypass on L3 is removed. The TVS devices remain shunt devices between signal and GND.

All 41 footprints and every pad retain position, rotation, layer and net. U1 remains fixed. Front-side component placement changes require a proposed position and user confirmation before application, as recorded in AGENTS.md. NRST entry via moves (-0.010,-0.050)mm. One obstructing GND via is removed; 70 vias remain. D6/D7/D8 ground returns use 0.30mm tracks to existing ground vias. Unrelated routing and the recent internal SWCLK/VREF work are preserved.

Native DRC: errors 0, unconnected 0, schematic parity 0; same five existing warnings. Native KiCad TVS-pad omission checks and an independent copper-envelope graph both verify that all three source-to-IC paths require their TVS signal landing. D6/D7 have no entry vias before the TVS. D8's bottom placement permits an entry via. These checks establish routing topology, not transient ESD immunity. The native check is integrated into netcheck_v08.py for subsequent routing changes.

All six ground zones are filled, all 13 ground graph nodes reach J2.1, and L1-L5 ground rims remain continuous. Layer, width, via, schematic and metadata checks pass. Schematic, project, rules and component-placement source are unchanged.

[ESD detail](../docs/review_esd_flow_20261006/esd_detail.png) · [Six layers](../docs/review_esd_flow_20261006/layers/six_layers.png) · [Verification](../docs/verification_esd_flow_20261006/).

Saved to the canonical local PCB. No Gerber, drill, BOM or Git publication was performed.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# Current RS-422 PCB — SWCLK/VREF routing refined (2026-10-06)

Canonical PCB SHA256: `67b9e0a161565ff865ad6a17902c53fbecc39c5072f45e77c577ac987b9ab87d`.

Using the latest user routing as the baseline, L4 SWCLK's 24 short straight segments are replaced by four straight segments and three tangent arcs of R0.478mm. Bottom SWCLK is simplified to two lines and one arc; bottom VREF becomes one direct line. SWCLK length is 9.273942→9.060672mm and VREF is 2.559548→2.441808mm, a total reduction of 0.331010mm. The four changed paths decrease from 34 pieces to 14.

All 41 footprint placements, all pads, all 71 vias and unrelated net routing are preserved, including fixed top PPG U1 and the user's relocated SWCLK/VREF vias. Native DRC: errors 0, unconnected 0, schematic parity 0, same five existing warnings. Netcheck passes. All six GND zones are refilled and all 13 GND graph nodes reach J2.1. L1-L5 GND rims, track-free L2, minimum 0.15mm width and via rules pass. Schematic, project, rule and component-source files remain unchanged.

[Six-layer review](../docs/review_routing_refine_20261006/layers/six_layers.png) · [Verification](../docs/verification_routing_refine_20261006/).

Saved to the canonical local PCB. No Gerber, drill, BOM or Git publication was performed.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# Current RS-422 PCB — placement interference cleared (2026-10-06)

Canonical PCB SHA256: `e0328b245de0281effbb0ba79942b417090891ca4a4f0d901ac16a0b8efa0a21`.

Top PPG U1 position, rotation and pads are unchanged. Relative to the user's latest placement, C5 moves +0.225mm X/+0.56mm Y to (22.725,17.56), 270 degrees; R5 moves -0.10mm Y to (23.7,18.2), 90 degrees. All other footprints and pads are preserved. The authoritative PLACEMENT table matches the final board.

Affected VREF, TXP_DRV, TXP and SWCLK routing is corrected. Two vias move and one GND via (0.50mm land/0.20mm drill) is added near C5, for 71 vias total. VREF is shortened by 5.051mm; total routed length decreases 1.959mm. SWCLK's bottom MCU escape and original via are retained.

Native DRC: errors 0, unconnected 0, schematic parity 0, same five existing warnings. Netcheck passes for 41 footprints and 123 numbered pins, minimum track width 0.15mm and existing via rules. All six GND zones are filled; all 14 GND graph nodes reach J2.1. L1-L5 peripheral GND remains continuous and L2 remains track-free. Schematic, project and design-rule files are unchanged.

[Six-layer review](../docs/review_placement_cleanup_20261006/layers/six_layers.png) · [Verification](../docs/verification_placement_cleanup_20261006/).

Saved to the canonical local PCB. No Gerber, drill, BOM or Git publication was performed.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# Current RS-422 PCB — placement rerouting complete (2026-10-06)

Canonical PCB SHA256: `42224bb6b24e6fadfa758637256e70588f81b92c895da37d11371f9d5dfd237f`.

Reworked C1, C4, R1, R2 and D8 connections after the user's placement changes. Final clearance corrections are C1 +0.15mm in Y and C4 +0.08mm in X; all other footprint positions/angles and pad identities are preserved. PLACEMENT in design_v08.py matches the final board. C4's added GND via connects its otherwise isolated ground fill without drilling through the SMD pad.

NRST uses a 3.6156mm L5 connection. L4 3V3 intermediate bends are merged into a 0.40mm-wide route with R0.40 arc, and L4 12V clears the relocated SDA via. Total routed length decreases 3.1180mm from the user input. There are 70 vias (one added, one removed, five moved).

Native DRC: errors 0, unconnected 0, schematic parity 0, same five existing warnings. Schematic/net and routing-policy checks pass: 41 footprints, 123 numbered pins, minimum width 0.15mm, signal/GND drills 0.20mm and power/reference drills 0.25mm. All six GND zones are filled; all 16 GND graph nodes reach J2.1; L1-L5 ground rims remain continuous and L2 remains track-free. Schematic, project and rule files are unchanged.

[Six-layer review](../docs/review_placement_20261006/layers/six_layers.png) · [Verification](../docs/verification_placement_20261006/).

Saved to the canonical local PCB. No Gerber, drill, BOM or Git publication was performed.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

> 최신 수정 — 2026-10-06: 중앙 3.3V의 불필요한 V자 꺾임을 제거하고 폭 0.40mm 직접 연결과 원호로 대체했습니다. 해당 경로 0.6765mm 단축, DRC 오류 0·미연결 0·회로도 불일치 0·기존 경고 5건. 기존 원호 56개를 보존하고 1개를 추가했습니다. PCB SHA256: `d31a87e7ca3bec457658657d579a00a1d0a14226ededab17be3ef085d721ba52`. 아래 기록은 이 수정 이전 단계입니다. 거버 미생성.

# Current RS-422 PCB — corner cleanup and native arcs (2026-10-06)

Canonical PCB SHA256: `9a20272bce551736dd36ffd91ece1cbf10b4da316c59067ebb4d4ec9ea205e0e`.

Eight redundant collinear splits were merged, and 56 eligible corners were replaced with native KiCad PCB_ARC objects. Arc counts by layer are F.Cu 14, In2.Cu 10, In3.Cu 20, In4.Cu 3, B.Cu 9; In1.Cu remains a track-free GND layer. Short pad escapes and branch junctions retain their existing connections. There are now 313 straight tracks, 56 arcs and 70 unchanged vias. Total true path length is 199.685477 → 199.450821mm.

All 41 footprint identities, 151 physical pads and 123 numbered pin nets are preserved, including positions, rotations and metadata. Track net/layer/width values are unchanged. The geometry audit preserves all fixed branch and pad/via contact nodes. Native arc geometry includes start/mid/end, center, radius and actual arc length, not a straight chord approximation.

Arc centerline radius targets the existing trace width. Saved native three-point radius reconstruction is recorded without rounding away differences; its lower-bound comparison allows 0.0001mm numerical tolerance, with actual minimum R 0.149941904mm. This is an audit measurement tolerance only; board DRC rules were not changed. All 112 arc endpoints pass tangent checks, maximum angular error 0.019575 degrees.

Canonical DRC: errors 0, unconnected 0, schematic parity 0, same five previous warnings. Netcheck passes with minimum trace width 0.15mm and L4 3V3 widths 0.30/0.40mm. All six GND zones are refilled; all 17 saved GND graph nodes reach J2.1 and L1–L5 peripheral GND remains continuous.

[Arc before/after](../docs/review_curves_20261006/curve_before_after.png) · [Six layers](../docs/review_curves_20261006/layers/six_layers.png) · [Verification](../docs/verification_curves_20261006/).

No Gerber, drill, BOM or Git publication was performed. Fabrication output remains pending user review.

<details>
<summary>Previous L4 routing optimization record — before native arcs</summary>

# Current RS-422 PCB — L4 3V3 routing optimized (2026-10-06)

Canonical PCB SHA256: `3978af66433edf39972056465ec87a712339e6beff50f82e82f3de54fd9c657c`.

Based on the user's saved board `8cb336d7…`, this update changes only L4/In3.Cu 3V3 tracks and regenerates ground fill. The user's B.Cu U2.2-to-C15 power connection, removed power via and new central 45-degree corner are preserved. All 41 footprints, 151 physical pads, 123 numbered pin nets, 70 remaining vias and all tracks outside L4 3V3 are unchanged from the user's input.

L4 3V3 length: 30.013704 → 28.224137mm; segments: 37 → 27; widths remain 0.30/0.40mm. With both boards refilled under the same settings, L4 GND area increases from 70.2851 to 70.6489mm². The redundant V-shaped connection at the removed via and unnecessary intermediate bends were shortened. Other layers have identical routed copper and identical refilled GND area.

Canonical DRC: errors 0, unconnected 0, schematic parity 0, same five existing warnings. Netcheck passes. The board now has 321 track segments and 70 vias. Minimum track width is 0.15mm; via dimensions and project/rule files are unchanged. All six GND zones are filled, all 17 saved GND graph nodes reach J2.1, L1–L5 ground rims are continuous and L2 remains free of tracks.

[Before/after L4](../docs/review_l4_power_20261006/l4_power_before_after.png) · [Six layers](../docs/review_l4_power_20261006/layers/six_layers.png) · [Verification](../docs/verification_l4_power_20261006/).

Gerber/drill/BOM generation remains on hold pending user review. No manufacturing files or Git commits were created for this routing update.

<details>
<summary>Previous routing completion record — before the user's L4 edit</summary>

# Current RS-422 PCB — routing complete, review before Gerber (2026-10-06)

Current canonical PCB SHA256: `5058f421e6e8d56442d0f3bb0674544cc2cda25106a297b010cab9f6ea7ee266`.

D6/D7 are on top near the SWD pads; C15/C16 are 100nF 16V X7R metric 0603 on 3V3–GND. The paused 41-reference placement, angles and all existing tracks/vias are preserved. The user permits 135/225/315-degree SMT placement. Routing adds three 3V3 tracks and one power via (0.50mm land / 0.25mm drill), completing both remaining capacitor connections. C15 reuses its nearest existing power via. C16 uses a nearby added via and a 0.164mm L4 connection to keep bottom routing short.

Canonical DRC: errors 0, unconnected 0, schematic parity 0; the same five previous warnings remain. The 41 references and 123 numbered pin nets match the schematic. All six GND zones are refilled; all 17 saved GND graph nodes reach J2.1, with no floating fill. L1–L5 continuous ground rims, minimum track width 0.15mm, via policy, L2 no tracks and the existing L5 short routes all pass. New/relocated D6/D7/C15/C16 bodies and courtyards have no overlaps.

Total 330 track segments and 71 vias. Bottom track length is 69.049mm; front is 33.387mm with 93.270mm² saved GND fill. Existing component placement and schematic bytes are unchanged during this routing step.

[Six-layer review](../docs/review_routing_20261006/layers/six_layers.png) · [Local changes](../docs/review_routing_20261006/layers/top_esd_and_caps.png) · [Verification](../docs/verification_routing_20261006/).

Gerber/drill/BOM exports were not generated or changed. The user will review this routing before authorizing Gerber output. Previous manufacturing files are historical and do not describe this 41-reference board.

<details>
<summary>Previous PCB completion record — 2026-10-05</summary>

# Current RS-422 PCB — GND pours on all six layers and fabrication export

2026-10-05 final PCB SHA256: `acde2a668cf37064ec92e6d2a75cca0f7511d923814010b9736734c7725d5f3e`.
Six copper layers, circular profile centerline diameter13.5mm, nominal thickness0.8mm.

The user's TXP J3 position (25.5,15.9)mm, 270 degrees, B.Cu is preserved and synchronized to design_v08.py. R4 remains (20.05,14.55)mm at90 degrees; C7 remains (20.025,12.33)mm at90 degrees. All39 references, 143 physical pad UUIDs, 119 numbered pin nets, 322 routed segments and71 vias are unchanged by this GND-pour step. Schematic logic, DRC settings and custom rules are unchanged.

The central exclusions on L3/In2.Cu and L4/In3.Cu were removed. A full-board B.Cu GND zone was added. All6 zones remove isolated islands and fill available copper space. F/B local clearance is0.15mm; inner clearance remains0.20mm. All saved GND components, including central and B.Cu areas, reach J2.1:16/16 copper graph nodes, isolated0. L1-L5 retain continuous perimeter bands (checked width0.325mm front,0.225mm inner). B.Cu does not require a continuous perimeter band.

| Layer | Track length mm | Saved GND area mm² |
|---|---:|---:|
| F.Cu | 30.262 | 93.914 |
| In1.Cu | 0.000 | 103.592 |
| In2.Cu | 40.567 | 88.189 |
| In3.Cu | 53.395 | 70.941 |
| In4.Cu | 5.930 | 101.160 |
| B.Cu | 69.080 | 49.929 |

Tracks:0.15mm235,0.20mm40,0.30mm12,0.40mm35. All via lands0.50mm; signal28 plus GND28 use0.20mm drills; power/reference15 use0.25mm drills. L2 has no tracks. L5 has6 segments totaling5.930mm of reviewed short detours. L4 3V3 distribution width remains at least0.30mm.

Final canonical DRC errors0, unconnected0, schematic parity0. Existing warnings5 are unchanged: U4/U5 silk-edge items4 and U2 library-footprint mismatch1. No rules, severities or exclusions were relaxed. Schematic bytes are unchanged from the preceding verified design.

Project foreign-copper clearance0.15mm, hole-to-copper0.20mm, hole-to-hole0.25mm. General edge clearance0.30mm, F GND exception0.20mm. Actual physical stackup and copper weight remain unconfirmed. The retained power-via annular ring0.125mm and current hole/edge exceptions need manufacturer review as described in the fabrication memo.

User-authorized Gerber/drill output: [ZIP](../manufacturing/20261005_all_ground/PPG_v0.8_6L_GND_20261005_Gerber_Drill.zip), [fabrication memo](../manufacturing/20261005_all_ground/README_FABRICATION.md). Includes11 Gerbers and Excellon PTH71/NPTH0. Actual exported files were parsed and rendered; layer order, mm units, center origin, Ø13.5mm outline and all drill coordinates/sizes were verified. The auto-generated default job file was excluded from the fabrication ZIP because its material stackup is not manufacturer-confirmed. BOM/positions/paste were not generated; no order or upload was made.

Front SWD pads remain J9 NRST, J7 SWDIO, J10 GND, J8 SWCLK, J11 3V3 VTref; Ø0.8mm,1.27mm pitch, F.Cu/F.Mask without paste. Board center and auxiliary/grid origins remain(20,17)mm. U1.3 LDO_EN remains connected to U2.12 PA7; firmware initial-LOW/internal-pulldown requirement is unchanged. D6/D7/D8 retain ESD351 on SWDIO/SWCLK/NRST; the deferred TVS power-net reassignment was not included.

Current [CAD layer overview](../docs/review_all_ground_20261005/layers/six_layers.png), [Gerber copper overview](../manufacturing/20261005_all_ground/review/gerber_render/copper_six_layers.png), [verification](../docs/verification_all_ground_20261005/). Prior review_r4_move, verification_txp_move, via_split and six-layer-conversion outputs are historical.

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>

</details>
