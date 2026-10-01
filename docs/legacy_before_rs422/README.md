# SleepBud PPG PCB v0.8 — ESD PCB 반영

2026-10-01 기준, 현재 회로도의 **D1–D8 TVS와 FB1을 PCB 배치·배선에 반영했습니다. 탑면에는 PPG 센서 U1만 유지합니다.**

Ø13.5 mm, 4층, 두께 0.8 mm이며 바텀면에 나머지 34개 레퍼런스를 배치했습니다. 전체 35개 레퍼런스에는 구리 케이블·디버그 패드 9개가 포함됩니다(실장 부품 26개).

## 반영 내용

- D1: `SPHV15-01ETG`, SOD-882 1.0 × 0.6 mm. D2–D8: `ESD351DPYR`, DFN1006 1.0 × 0.6 mm. 로컬 풋프린트와 `CablePad_D0.8`을 작성했습니다.
- FB1: `BLM15PX601SN1D`, 0402 / 미터 1005. `J1 / 12V_IN → FB1 → 12V / C13 / U4`로 입력 전원을 분리했습니다. D1은 비드 앞의 12V_IN–GND에 연결합니다.
- 각 TVS의 GND 패드에 별도 비아를 약 0.52–0.57 mm의 0.20 mm 배선으로 연결했습니다.
- U1의 위치·방향·탑면 배치를 유지하고, U2/U3/U6 및 일부 수동소자·케이블 패드를 이동해 바텀면 공간을 확보했습니다.
- 회로도 UUID 경로, 부품 필드, 풋프린트 식별자, NC를 포함한 패드 넷을 동기화했습니다.
- BOM은 DNP 제외·동일 부품 레퍼런스 통합·패키지명·데이터시트 파일명·합의한 값 표기를 적용했습니다.

## 검증 결과

| 항목 | 결과 |
|---|---:|
| 회로도/PCB 레퍼런스 | 35 / 35 |
| 탑면 / 바텀면 | U1 1개 / 34개 |
| PCB DRC 오류 / 미연결 / 회로도 불일치 | 0 / 0 / 0 |
| 회로도 ERC 오류·경고 | 0 |
| DRC 경고 | 6 |
| BOM | 16그룹 / 35레퍼런스 / DNP 0 |
| 최소 배선 폭 / 비아 직경·드릴 | 0.10 / 0.50·0.25 mm |

DRC 경고는 기존 U4/U5 실크가 마스크에 잘리는 5건과 기존 U2의 실크 제거에 따른 라이브러리 차이 1건입니다. 검사 규칙과 경고 수준을 낮추지 않았습니다. Gerber 출력 시 실크에서 솔더마스크 개구를 차감했습니다. 상세 결과와 변경 좌표는 [작업 기록](docs/PCB_update_20261001.md), [검증 원자료](docs/verification_v08/)에 있습니다.

## 현재 파일

- [KiCad PCB](kicad/ppg_pcb_v08.kicad_pcb), [회로도](kicad/ppg_pcb_v08.kicad_sch), [회로도 PDF](docs/ppg_pcb_v08_schematic.pdf)
- [탑면 배치](docs/placement_front.png), [바텀면 배치](docs/placement_back.png), [PCB 레이어 PDF](docs/ppg_pcb_v08_layers.pdf)
- [탑면 SVG](docs/layout_front.svg), [바텀면 SVG](docs/layout_back.svg), [부품 좌표 CSV](docs/ppg_pcb_v08_positions.csv)
- [통합 BOM 엑셀](bom/MVP-PPG_BOM_부품별통합_DNP제외_값표준화_v2.xlsx), [BOM 설명·표기 규칙](bom/README.md)
- [Gerber·드릴 ZIP](ppg_pcb_v08_gerber.zip), [개별 제조 파일](gerber/)
- [기판 외형·드릴 STEP](docs/ppg_pcb_v08_board_only.step): 부품 3D 모델을 포함하지 않습니다. 공칭 기판은 0.8 mm이며, STEP의 KiCad 기본 동박·마스크 표현을 포함한 Z 범위는 약 0.81 mm입니다.

ESD 추가 전 STEP·3D 렌더·라우터 세션은 [과거 자료 폴더](docs/legacy_before_esd/)에 보관했습니다. 부품을 포함한 최신 3D 조립 모델은 이번 출력에 포함하지 않습니다. `PPG_PCB_v0.8_사양.md`와 `docs/verification_20260930/`는 이전 설계 기록입니다.

## 다시 검증·출력하기

KiCad 10 CLI, `pcbnew`를 사용할 수 있는 Python, BOM용 Python의 `openpyxl`이 필요합니다.

```bash
# 이 클라우드 환경의 도구 경로
source /workspace/.amp-env/activate.sh
./kicad/run_v08.sh --check-only
./kicad/run_v08.sh
```

기본 실행은 현재 배선 PCB의 복사본을 검사한 뒤 BOM·좌표·Gerber·드릴·PDF·SVG를 갱신하며 원본 PCB와 회로도를 재생성하지 않습니다. 오류·미연결·회로도 불일치가 있으면 출력을 중단합니다. `KICAD_CLI`, `KICAD_PYTHON`, `BOM_PYTHON`으로 실행 파일 경로를 지정할 수 있습니다.

`design_v08.py`는 최종 배치 좌표를 포함합니다. `--rebuild`는 배치부터 자동 배선한 별도 후보를 만드는 명시적 옵션이며 `FREEROUTING`이 필요합니다. 검토된 배선의 원본은 현재 `.kicad_pcb`이며, 자동 재배선 결과에는 추가 조정·DRC가 필요할 수 있습니다.

## 부품 선정 근거와 실제 시험

- [TI ESD351 데이터시트](https://www.ti.com/lit/ds/symlink/esd351.pdf): 핀 1은 IO/cathode, 핀 2는 GND/anode입니다. 권장 랜드는 0.30 × 0.50 mm, 중심 간격 0.70 mm입니다.
- [Littelfuse SPHV 데이터시트](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_array_sphv_datasheet.pdf?assetguid=4bdc7e09-5dd4-4010-a86a-0008bb6e228c): SPHV15-01ETG의 핀 1은 cathode, 핀 2는 anode입니다. 권장 랜드는 0.325 × 0.650 mm, 중심 간격 0.650 mm입니다.
- [Murata BLM15PX601SN1 사양](https://www.murata.com/en-us/products/productdetail?partno=BLM15PX601SN1%23): 600 Ω @ 100 MHz, 85°C에서 0.9 A, 최대 DCR 0.23 Ω입니다.

D1의 클램핑 전압은 1 A에서 22 V로, [MCP1703A의 입력 절대최대값 18 V](https://ww1.microchip.com/downloads/en/DeviceDoc/20005122B.pdf)보다 높습니다. 비드와 C13 이후 U4 입력에 남는 과도전압은 실제 ESD 시험으로 확인해야 합니다. 부품 자체의 ESD 정격을 보드의 보증 내성으로 해석하지 않습니다.
