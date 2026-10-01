# SleepBud PPG PCB v0.8 — ESD·입력 비드 개정판

2026-09-30 개정. **D1–D8 ESD 소자와 FB1을 회로도·PCB에 반영하고 배선했습니다.** Ø13.5 mm, 4층을 유지했으며, 기존 PCB 파일의 두께 1.6 mm를 사양값인 **0.8 mm**로 수정했습니다. 이 개정판은 시제품 제작·평가용이며, 보드의 ESD 내성을 실측 검증한 양산 승인본은 아닙니다.

**제작 전 수정 필요 (2026-10-01):** 개별 IC STEP를 대조하면서 U4/U5의 기존 풋프린트가 Microchip MC 패키지와 다름을 확인했습니다. 현재 Gerber와 보드 전체 STEP에는 기존 풋프린트가 남아 있습니다. [패키지 불일치와 교정 항목](docs/step/README.md#u4u5에서-발견한-pcb-불일치)을 해결하고 재검증한 뒤 제작해야 합니다.

## 반영 내용

- 앞면에 `SPHV15-01ETG` 1개, `ESD351DPYR` 7개, `BLM15PX601SN1D` 1개를 추가했습니다. 센서 위치와 중앙 광학 모듈의 코트야드를 유지했습니다.
- 전원은 `J1 / 12V_IN → FB1 → 12V / C13 / U4`입니다. D1은 비드 앞의 `12V_IN–GND` 사이에 연결했습니다.
- D2–D8은 차례로 TXP, TXN, RXP, RXN, SWDIO, SWCLK, NRST에 연결했습니다. D1–D8 모두 **1번 핀은 cathode/보호 신호, 2번 핀은 anode/GND**입니다.
- TVS 2종의 제조사 권장 랜드와 `CablePad_D0.8`을 로컬 라이브러리에 추가했습니다. 실제 실장 부품은 **26개**, 케이블·시험용 동박 패드는 **9개**로 총 **35개 참조번호**입니다.
- J7–J9에는 드릴 Ø0.25 mm의 도금 비아가 있습니다. J7 비아는 패드 중심에서 0.05 mm 벗어나며, J8은 기존 위치에서 위쪽으로 0.25 mm 이동했습니다. 시험 지그는 현재 좌표와 패드의 구멍을 반영해야 합니다.

## 검증 결과

| 항목 | 결과 |
|---|---|
| 회로도·설계 데이터·PCB 참조번호 | 35개 일치 |
| 번호가 있는 전기 핀 | 111개 일치 |
| PCB DRC 오류 / 미연결 / 회로도 불일치 | 0 / 0 / 0 |
| 회로도 ERC 오류 / 경고 | 0 / 0 |
| DRC 경고 | 17개: 동박 패드의 코트야드 없음 9개, U2 라이브러리 차이 1개, 실크 간섭 5개, 비아 중심 밖에서 만나는 트랙 2개 |

검증 단계에서는 기존에 무시하던 검사도 복원하고 제외 항목을 해제합니다. DRC 경고는 보고서에 그대로 남깁니다. 구성·연결·외형·두께·센서 코트야드 이격 검사는 [연결 및 형상 검증](docs/ppg_pcb_v08_verification.json), ERC/DRC 원문과 출력 파일의 해시는 [출력 기록](docs/ppg_pcb_v08_export_manifest.json)에서 확인할 수 있습니다.

## 제작 자료

| 자료 | 파일 |
|---|---|
| 회로도 / PCB | [회로도 PDF](docs/ppg_pcb_v08_schematic.pdf), [PCB 레이어 PDF](docs/ppg_pcb_v08_layers.pdf) |
| 조립도 | [앞면](docs/ppg_pcb_v08_assembly_front.pdf), [뒷면 — 실제 뒷면 시점으로 좌우 반전](docs/ppg_pcb_v08_assembly_back.pdf) |
| 구매·실장 | [BOM](docs/ppg_pcb_v08_BOM.csv), [실장 부품 좌표](docs/ppg_pcb_v08_assembly_positions.csv) |
| 케이블·시험 패드 | [동박 패드 좌표](docs/ppg_pcb_v08_copper_pads.csv) |
| 원본 전체 좌표 | [KiCad 좌표](docs/ppg_pcb_v08_positions.csv) — 동박 패드 포함 |
| 제조 출력 | [Gerber·드릴 ZIP](ppg_pcb_v08_gerber.zip), [개별 파일](gerber/) |
| 기구 검토 | [STEP](docs/ppg_pcb_v08.step), [앞면 렌더](docs/render_front.png), [뒷면 렌더](docs/render_back.png) |
| 검사 원문 | [DRC](docs/ppg_pcb_v08_DRC.json), [ERC](docs/ppg_pcb_v08_ERC.json) |
| 부품 자료 | [데이터시트 목록 및 원본 PDF](docs/datasheets/README.md) — 참조번호·품번·문서 버전·출처 포함 |
| 개별 IC 기구 자료 | [U1–U6 STEP 목록](docs/step/README.md) — 공식 패키지 모델·도면 기반 참고 모델·최대 치수 외형 구분 |

실장 부품 26개에 모두 3D 모델을 연결했습니다. U1은 **2.9 × 4.3 × 1.4 mm 명목 외형 모델**, U2는 단순화한 패키지 외형이며, TVS는 일반 모델을 패키지 외형에 맞춘 시각화용 모델입니다. 센서의 내부 광학 구조·창·커버나 하우징을 나타내지 않습니다.

실장 좌표와 동박 패드 좌표는 보드 중심 원점·**+Y 아래쪽**, KiCad 원본 전체 좌표는 **+Y 위쪽**입니다. 실장 업체와 좌표 방향·회전·앞뒷면 해석을 확인해 해당 형식의 파일을 사용합니다.

뒷면 조립도는 보드를 뒤집어 보는 시점입니다. 전체 레이어 PDF의 B.Fab은 좌우 반전하지 않은 앞면 좌표 시점이므로 구분해서 읽습니다. 조립도는 중복 부품번호를 정리하고 D1–D8과 J1–J9를 표시했습니다. J1–J9의 신호는 [사양의 패드 표](PPG_PCB_v0.8_사양.md)에서 확인합니다.

## 배선과 남은 실물 평가

외부 패드는 뒷면, TVS는 앞면에 있어 신호 비아를 통한 **짧은 분기형(shunt) 연결**을 사용했습니다. 신호가 TVS 패드를 반드시 통과하는 flow-through 배선은 아닙니다. D2–D8의 앞면 신호 분기는 약 0.22–0.69 mm이며, GND는 전용 비아로 내부 GND 면에 연결합니다. D6의 GND 경로는 약 1.84 mm로 다른 TVS보다 길어 SWDIO 시험에서 특히 확인해야 합니다. 상세 길이는 [배선 기록](docs/verification_esd/routing.json)에 있습니다. 앞면 길이에는 뒷면 분기와 비아 배럴 길이가 포함되지 않습니다.

**12 V 보호의 잔류 전압이 주요 미검증 항목입니다.** [Littelfuse SPHV 데이터시트](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_array_sphv_datasheet.pdf?assetguid=4bdc7e09-5dd4-4010-a86a-0008bb6e228c)의 D1 클램핑 전압은 1 A에서 22 V, 5 A에서 28 V로, [MCP1703A 입력 절대최대값 18 V](https://ww1.microchip.com/downloads/cn/DeviceDoc/cn557682.pdf)보다 높습니다. FB1·C13 이후 U4 입력과 각 보호 핀의 과도전압을 실제 ESD 시험으로 확인해야 합니다. 기존 선정 부품은 유지했습니다.

실물에서 남은 확인은 입력 전압 허용범위·과도응답, LED 구동 조건별 발열, 케이블을 연결한 통신·ESD 시험, 하우징/커버의 광학 간섭입니다. 제작 업체의 실제 0.8 mm 적층·재료·공차도 확정해야 합니다. 부품의 ESD 정격이나 DRC 통과를 보드의 보증 내성으로 해석하지 않습니다.

## 다시 검증·출력하기

현재 배선된 `kicad/ppg_pcb_v08.kicad_pcb`와 회로도가 출력의 기준입니다. 저장소 루트에서 KiCad 10의 Python으로 실행합니다.

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' kicad/export_v08.py --save-refill
```

이 도구는 임시 복사본의 존을 채우고 회로도·PCB 연결, ERC, DRC를 검사한 뒤 BOM·좌표·Gerber·드릴·PDF·STEP·렌더를 생성합니다. 검사나 출력이 실패하면 기존 출력물을 유지하며 임시 작업 경로를 보고합니다. `--check-only`는 검사만 실행합니다. `--save-refill`은 성공한 검증본의 존 채움 결과를 원본 PCB에 저장합니다.

`build_pcb_v08.py`는 초기 배치용 생성기이므로 현재 배선본의 재출력에 사용하지 않습니다. `design_v08.py`는 부품·핀·명목 배치 데이터이며 상세 배선은 PCB 파일을 기준으로 합니다. 기존 DSN/SES와 ESD 회로도 초안은 [이전 단계 자료](docs/baseline_20260930/), 당시 검증 결과는 [기존 검증 폴더](docs/verification_20260930/)에 보존합니다.

회로 구성과 인터페이스의 자세한 내용은 [v0.8 사양](PPG_PCB_v0.8_사양.md)을 참조하세요. SWD 기준 전압 3V3는 케이블 패드에 없으며 **C11 또는 C12의 1번 패드**에서 확인합니다.
