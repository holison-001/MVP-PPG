# SleepBud PPG PCB v0.8 — 작업 체크포인트

2026-09-30 작업 기록입니다. **ESD·비드는 회로도에 반영했으며, PCB 배치·배선에는 아직 반영하지 않았습니다.**

현재 PCB, Gerber, STEP, 부품 좌표 및 기존 BOM은 ESD 추가 전 26개 부품 기준입니다. 이 파일들을 ESD 개정판의 제조 자료로 사용하면 안 됩니다.

## 반영한 작업

- A3 가로 회로도를 센서, MCU, LVDS, 전원, 케이블, SWD의 기능별 영역으로 정리했습니다.
- 기존 26개 부품의 회로도 UUID와 핀 UUID를 유지했습니다.
- D1: 12V 입력의 Littelfuse `SPHV15-01ETG` 단방향 TVS, 1.0 × 0.6 mm.
- D2–D8: TXP, TXN, RXP, RXN, SWDIO, SWCLK, NRST의 TI `ESD351DPYR` 단방향 TVS, 1.0 × 0.6 mm.
- FB1: Murata `BLM15PX601SN1D`, 600 Ω @ 100 MHz, 1005 미터 규격(1.0 × 0.5 mm).
- 전원 연결은 `J1 / 12V_IN → FB1 → 12V / C13 / U4`입니다. D1은 비드 앞의 12V_IN과 GND 사이에 연결합니다.
- 회로도 생성기는 새 부품과 정리된 배치를 재생성하도록 갱신했습니다. Datasheet와 MPN 필드도 포함합니다.

## 검증 상태

| 항목 | 현재 결과 |
|---|---|
| ESD 회로도 부품 수 | 35개 |
| 회로도 넷리스트와 설계 데이터 | 불일치 0개 |
| 회로도 ERC | 오류 0개, 풋프린트 링크 경고 11개 |
| 새 ESD 풋프린트 | 8개 부품의 로컬 라이브러리 제작 필요 |
| 기존 풋프린트 경고 | J7–J9의 `CablePad_D0.8` 링크 3개 |
| PCB | 기존 26개 부품의 배선 상태 유지; ESD·FB1 미반영 |
| 기존 PCB DRC | 오류 0개, 미연결 0개, 기존 경고 8개 |
| ESD PCB 제조 자료 | 미생성 |

회로도 미리보기는 [ESD 회로도 초안 PDF](docs/ppg_pcb_v08_schematic_esd_draft.pdf), 검증 원자료는 [검증 폴더](docs/verification_20260930/)에 있습니다.

## 다음 작업

1. D1 및 D2–D8의 제조사 권장 랜드로 풋프린트를 작성하고 라이브러리 연결을 확인합니다.
2. Ø13.5 mm 외형과 센서 광학 영역을 유지하면서 앞면 가장자리에 새 부품을 배치합니다. `design_v08.py`의 새 부품 좌표는 아직 제안값입니다.
3. 케이블/테스트 패드 근처의 ESD 방전 경로와 짧은 GND 경로를 배선하고, J1의 기존 12V 연결을 비드 전후로 분리합니다.
4. PCB–회로도 연결 일치, DRC, 미연결, 기구 간섭 및 도면 시인성을 검증합니다.
5. PCB가 검증된 뒤 BOM·좌표·Gerber·STEP·렌더를 다시 생성합니다.

## 부품 선정 근거와 실제 시험

- [TI ESD351 데이터시트](https://www.ti.com/lit/ds/symlink/esd351.pdf): 핀 1은 IO/cathode, 핀 2는 GND/anode입니다. 권장 랜드는 0.30 × 0.50 mm, 중심 간격 0.70 mm입니다.
- [Littelfuse SPHV 데이터시트](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_array_sphv_datasheet.pdf?assetguid=4bdc7e09-5dd4-4010-a86a-0008bb6e228c): SPHV15-01ETG의 핀 1은 cathode, 핀 2는 anode입니다. 권장 랜드는 0.325 × 0.650 mm, 중심 간격 0.650 mm입니다.
- [Murata BLM15PX601SN1 사양](https://www.murata.com/en-us/products/productdetail?partno=BLM15PX601SN1%23): 600 Ω @ 100 MHz, 85°C에서 0.9 A, 최대 DCR 0.23 Ω입니다.

D1의 클램핑 전압은 1 A에서 22 V로, [MCP1703A의 입력 절대최대값 18 V](https://ww1.microchip.com/downloads/en/DeviceDoc/20005122B.pdf)보다 높습니다. 비드와 C13 이후 U4 입력에 남는 과도전압은 실제 ESD 시험으로 확인해야 합니다. 부품 자체의 ESD 정격을 보드의 보증 내성으로 해석하지 않습니다.

## 파일 안내

- `kicad/ppg_pcb_v08.kicad_sch`: ESD·비드를 포함한 현재 회로도 초안.
- `kicad/ppg_pcb_v08.kicad_pcb`: ESD 추가 전 PCB.
- `kicad/design_v08.py`: 현재 35개 부품의 전기적 설계 데이터와 새 부품의 제안 배치.
- `kicad/build_sch_v08.py`, `kicad/layout_schematic_v08.py`: 회로도 생성 및 배치 도구.
- `PPG_PCB_v0.8_사양.md`: ESD 추가 전 원설계 사양. 최신 진행 상태는 이 README를 우선합니다.
- `docs/ppg_pcb_v08_schematic.pdf`: ESD 추가 전에 정리했던 26개 부품 회로도.
- `gerber/`, `ppg_pcb_v08_gerber.zip`, 나머지 PCB 출력물: ESD 추가 전 원설계 자료.

KiCad 자동 백업, 캐시, 개인 UI 설정 및 임시 검토 폴더는 Git에서 제외합니다. 기존 로컬 백업은 그대로 보존합니다.
