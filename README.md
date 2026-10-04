# SleepBud PPG PCB v0.8 — RS-422, D2/D4 삭제

D2·D4 SM712를 삭제한 **37레퍼런스(구매 부품28개 + 구리 패드9개)** 회로입니다. U3 XR33194/U6 XR33183, R3 `120/1%` 종단, R4 `10k` 풀업, R5–R8 `22` 직렬저항은 유지합니다. 탑면에는 PPG U1만 배치합니다.

주 [PCB 파일](kicad/ppg_pcb_v08.kicad_pcb)에 RS-422 배선을 반영했습니다. **ERC0, DRC 오류0·미연결0·회로도 불일치0**이며 NRST까지 연결했습니다. 독립 검사에서도 부품 본체/조립 여유 겹침0, 패드·배선·비아–외곽 최소0.302168mm를 확인했습니다. 1층 GND 푸어는 외곽0.20mm 이격으로 확장했습니다. 실크 외곽4건·U2 라이브러리 도형 불일치1건의 경고는 [검증 기록](docs/verification_rs422_no_bus_tvs/)에 남겼습니다.

| 층 | 현재 구성 |
|---|---|
| 1층 F.Cu | PPG U1만 실장, 배선 18.80 mm, GND 푸어 102.64 mm², 외곽 이격0.20 mm |
| 2층 In1.Cu | 일부 신호 배선과 GND 푸어88.03 mm² |
| 3층 In2.Cu | 3V3 전체 푸어 제거, **0.40mm 전원 배선**과 NRST·SWDIO·12V·RS-422 일부 배선 |
| 4층 B.Cu | 나머지36레퍼런스와 부품 팬아웃 배선 |

1층 배선을2층으로 추가 이동해 **60.90→18.80 mm (69.1% 감소)**로 줄였고 GND 푸어는 **86.57→102.64 mm²**로 늘렸습니다. 새 비아 없이 기존 연결을 사용했습니다. 1층의 신호–푸어 간격0.15 mm·외곽 이격0.20 mm, 3층의0.40 mm 3V3 배선은 유지합니다. PCB 중심은 **40×40 mm 시트의(20,17) mm**로 이동했고 부품 상대 위치는 같습니다. [도면 시트 화면](docs/pcb_sheet.png), [층 변경·검토 사항](docs/PCB_layers_20261001.md). PCB와 함께 [사용자 규칙 파일](kicad/ppg_pcb_v08.kicad_dru)을 보관해야 푸어 이격이 유지됩니다.

- [회로도](kicad/ppg_pcb_v08.kicad_sch), [회로도 PDF](docs/ppg_pcb_v08_schematic.pdf)
- [탑·바텀 배치 PNG](docs/placement_preview_rs422/rs422_top_bottom.png), [D2/D4 제거 전후](docs/placement_preview_rs422/d2_d4_removed_comparison.png)
- [1층 PNG](docs/layers_png/01_F_Cu_TOP.png), [2층 PNG](docs/layers_png/02_In1_Cu_GND.png), [3층 PNG](docs/layers_png/03_In2_Cu_3V3.png), [4층 PNG](docs/layers_png/04_B_Cu_BOTTOM.png)
- [변경·핀 연결·케이블 표](docs/RS422_update_20261001.md), [이번 검증 원자료](docs/verification_rs422_no_bus_tvs/)
- [BOM 검토본](bom/MVP-PPG_BOM_부품별통합_DNP제외_값표준화_v2.xlsx): 승인 절차 지정 전에 생성한19그룹·37레퍼런스 자료
- [D2/D4 삭제 전39 회로 이력](docs/legacy_rs422_with_sm712/), [LVDS 배선·제조 이력](docs/legacy_before_rs422/)

**거버·BOM의 추가 생성/갱신은 사용자 승인 후 진행합니다.** [출력 승인 규칙](docs/OUTPUT_APPROVAL.md). 기존 `gerber/`와 루트 Gerber ZIP은 LVDS 이력으로 새 RS-422 제조 자료가 아닙니다.

검증 실행: `source /workspace/.amp-env/activate.sh` 후 `./kicad/run_v08.sh --check-only`. 기본 실행도 검증 전용입니다. 거버·BOM 출력은 명시적 승인 후 `--publish-approved-outputs` 옵션으로 진행합니다.

AMP 프로브 공급은 공칭9V이며 PPG의 기존 `12V_IN`/`12V` 넷 이름은 유지했습니다. D1·FB1 전원 보호와 D6–D8 SWD 보호는 유지하고 통신선 외부 TVS는 생략했습니다. SWDIO=J7, SWCLK=J8, NRST=J9입니다.

`ppg_rs422_review.*`와 `docs/review_rs422_pending/`는 NRST가 남아 있던 이전 검토 스냅샷입니다. 기존 좌표 CSV·STEP·옛 렌더 파일은 제조 자료 갱신 대상이며, 최신 배치/구리는 위에 연결한 PCB·배치 PNG·층별 PNG를 사용합니다.
