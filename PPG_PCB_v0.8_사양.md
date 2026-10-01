# PPG PCB v0.8 — UART over LVDS / ESD·입력 비드 개정

원설계 2026-09-15, ESD PCB 반영 2026-09-30. **Ø13.5 mm, 4층, 명목 두께 0.8 mm**의 시제품 설계입니다. 최신 검사·출력 현황과 남은 실물 평가는 [README](README.md)를 기준으로 합니다.

## 구성

| 블록 | 부품 | 역할 |
|---|---|---|
| PPG | U1 `MAXM86161EFD+` | LED·광검출기·AFE 통합 모듈, I²C 주소 0x62 |
| MCU | U2 `STM32C011F6U6` | 센서 I²C 및 UART 통신 |
| TTL→LVDS | U3 `SN65LVDS1DBVR` | PA9 / UART_TX → TXP·TXN |
| LVDS→TTL | U6 `SN65LVDT2DBVR` | RXP·RXN → PA10 / UART_RX, 110 Ω 종단 내장 |
| 12→5 V | U4 `MCP1703A-5002E/MC` | 5V_LED 생성 |
| 5→3.3 V | U5 `MCP1703A-3302E/MC` | MCU·LVDS·센서 제어 전원 |
| 입력 ESD | D1 `SPHV15-01ETG` | 12V_IN–GND, 단방향 TVS, SOD882 1.0 × 0.6 mm |
| 신호 ESD | D2–D8 `ESD351DPYR` | LVDS 4선과 SWDIO·SWCLK·NRST, DFN1006 1.0 × 0.6 mm |
| 입력 비드 | FB1 `BLM15PX601SN1D` | 12V_IN → 12V, 600 Ω @ 100 MHz, 1005 미터 규격 |

실장 부품 26개와 동박 패드 9개로 구성됩니다. 앞면은 U1·D1–D8·FB1, 나머지 실장 부품과 외부 패드는 뒷면입니다.

## 전원과 센서

전원 경로는 `J1 → 12V_IN → FB1 → 12V → U4 → 5V_LED → U5 → 3V3`입니다. D1은 FB1 앞에, U4 입력 바이패스 C13은 FB1 뒤에 연결합니다. FB1의 두 넷을 동박으로 우회 연결하면 필터 기능이 사라집니다.

U1의 VLED는 5V_LED, LDO_EN은 3V3에 연결합니다. VLDO와 VREF에는 각각 1 µF 바이패스, VLED에는 10 µF 벌크 커패시터가 있습니다. 센서의 PGND·GND_DIG·GND_ANA는 공통 GND 면에 연결합니다. SDA·SCL은 4.7 kΩ으로 3V3에 풀업합니다. INTB와 GPIO는 연결하지 않아 펌웨어에서 I²C 상태·FIFO를 폴링해야 합니다. U1의 6–8번 핀은 전기적으로 연결하지 않고 납땜 랜드를 유지합니다. [MAXM86161 데이터시트](https://www.analog.com/media/en/technical-documentation/data-sheets/MAXM86161.pdf)

## LVDS 링크와 케이블

TX와 RX가 분리된 전이중 링크이며 방향 제어 회로는 없습니다. U3 DBV 핀은 `1 VCC / 2 GND / 3 Z(−) / 4 Y(+) / 5 D`, U6는 `1 VCC / 2 GND / 3 A(+) / 4 B(−) / 5 R`입니다. 모두 3V3 전원을 사용합니다. U6의 종단이 내장되어 외부 종단저항을 추가하지 않습니다. 컨트롤러의 TX는 보드의 RX에, 보드의 TX는 컨트롤러의 RX에 연결합니다. [TI LVDS 데이터시트](https://www.ti.com/lit/ds/symlink/sn65lvds1.pdf)

| 뒷면 Ø1.2 mm 패드 | 기능 |
|---|---|
| J1 | +12 V 입력, 12V_IN |
| J2 | 공통 GND |
| J3 / J4 | TXP / TXN, 보드 → 컨트롤러 |
| J5 / J6 | RXP / RXN, 컨트롤러 → 보드 |

케이블은 **6선 + 별도 압전 동축**입니다. LVDS 각 쌍은 꼬임선으로 구성하고 전원선·압전 동축과 분리합니다. 압전 동축은 이 PCB 회로에 포함되지 않습니다.

U6는 입력 개방 시 출력 High를 제공하지만, 케이블·상대 드라이버·전원 시퀀스를 포함한 유휴 상태는 실제 구성에서 확인합니다. 3.3 V 동작에서 공통모드 허용범위는 조건에 따라 제한되므로 공통 GND 연결을 유지해야 합니다. 1–2 m 케이블과 목표 UART 보레이트는 시제품 통신 시험 대상입니다. UART 배선은 전이중 부트로더 통신에 사용할 수 있으나 부트 모드 진입·옵션 바이트·펌웨어 절차는 별도로 준비해야 합니다.

## SWD와 시험 패드

| 뒷면 Ø0.8 mm 패드 | 신호 | PCB 좌표 (mm) |
|---|---|---|
| J7 | SWDIO / PA13 | (2.6, −2.6) |
| J8 | SWCLK / PA14 | (3.7, −2.85) |
| J9 | NRST | (−4.7, −2.6) |

좌표 원점은 보드 중심이며 +Y는 아래쪽입니다. J8은 원설계보다 위로 0.25 mm 이동했습니다. J7–J9에 Ø0.25 mm 도금 비아가 들어가며 J7 비아만 중심에서 0.05 mm 벗어납니다. 지그는 이 패드 형상을 기준으로 설계합니다. 디버거 GND는 J2, 3V3 기준 전압은 **C11 또는 C12의 1번 패드**에서 취합니다. 케이블 패드에는 3V3가 없습니다.

## ESD 배선

| 소자 | 1번 핀: cathode / 보호 신호 | 2번 핀 |
|---|---|---|
| D1 | 12V_IN | GND |
| D2 / D3 | TXP / TXN | GND |
| D4 / D5 | RXP / RXN | GND |
| D6 / D7 / D8 | SWDIO / SWCLK / NRST | GND |

ESD351의 신호 범위는 0–3.6 V이며 전형적 정전용량은 1.8 pF입니다. 뒷면 외부 패드에서 앞면 TVS까지 비아를 통한 분기형 연결을 사용하며, 각 TVS의 GND는 전용 비아로 내부 GND 면에 연결합니다. 이는 공간 제약을 반영한 배선으로 flow-through 구성은 아닙니다. D2–D8의 앞면 신호 분기는 0.22–0.69 mm, D6의 앞면 GND 경로는 약 1.84 mm입니다. 전체 방전 경로에는 뒷면 배선과 비아 길이도 포함됩니다. [TI ESD351 데이터시트](https://www.ti.com/lit/ds/symlink/esd351.pdf), [배선 측정 기록](docs/verification_esd/routing.json)

SPHV15의 클램핑 전압은 U4 입력 절대최대값을 초과할 수 있습니다. FB1·C13 이후의 잔류 전압, 실제 입력 허용범위 및 보드 ESD 내성은 아직 실측 검증하지 않았습니다. 부품 정격을 시스템 내성으로 간주하지 않습니다. 상세 수치와 평가 항목은 [README](README.md#배선과-남은-실물-평가)에 있습니다.

## 기구·제조 기준

- 외형 Ø13.5 mm, 4층, 명목 PCB 두께 0.8 mm. 기존 파일의 1.6 mm 설정은 수정했습니다. 제작사 적층·재료·공차는 미확정입니다.
- U1 명목 외형은 2.9 × 4.3 × 1.4 mm이며 중앙 위치를 유지합니다. 새 앞면 부품의 코트야드는 U1과 겹치지 않습니다.
- 기존 높이 추산은 PCB 0.8 + 센서 1.4 + 뒷면 부품 최대 1.45 = **약 3.65 mm**입니다. 납땜·조립 공차와 하우징·광학 커버는 이 합산에 포함하지 않습니다.
- 실장 부품 26개에 모두 3D 모델을 연결했습니다. U1·U2는 단순화한 외형, TVS는 일반 외형 모델입니다. 센서 광학 창·내부 구조나 실제 커버 형상을 검증하는 모델은 아닙니다.
- 광학 커버의 투과율·간격·반사 경로, 피부 접촉과 새 앞면 부품의 하우징 간섭은 실제 기구물에서 확인해야 합니다. [ADI 광학·기구 통합 지침](https://www.analog.com/en/resources/technical-articles/guidelines-for-the-optomechanical-integration-of-heartrate-monitors-in-wearable-earbud-devices.html)

실장 좌표 `_assembly_positions.csv`와 동박 패드 좌표 `_copper_pads.csv`는 보드 중심 원점·+Y 아래쪽입니다. KiCad 원본 `_positions.csv`는 +Y 위쪽이며 동박 패드를 포함한 35개 항목입니다. 실장 업체와 좌표 방향·회전·앞뒷면 해석을 확인한 뒤 해당 형식의 파일을 사용합니다.

[앞면 조립도](docs/ppg_pcb_v08_assembly_front.pdf)와 [뒷면 조립도](docs/ppg_pcb_v08_assembly_back.pdf)를 제공합니다. 뒷면 조립도는 실제 뒷면을 보는 시점으로 좌우 반전했으며, 전체 레이어 PDF의 B.Fab은 앞면 좌표 기준으로 반전하지 않았습니다. 조립도의 중복 부품번호를 정리하고 D1–D8·J1–J9를 표시했습니다. 케이블·시험 패드의 신호는 위 J1–J9 표를 참조합니다.

검증과 제조 자료 생성에는 현재 배선본을 검사하는 `kicad/export_v08.py`를 사용합니다. `build_pcb_v08.py`와 이전 DSN/SES는 현재 배선된 PCB를 복원하는 도구가 아닙니다. 파일 목록·실행 방법·경고 내역은 [README](README.md)에 정리되어 있습니다.

부품별 제조사 PDF, 적용 참조번호와 보관 문서 버전은 [데이터시트 목록](docs/datasheets/README.md)을 참조합니다.

**2026-10-01 기구 대조 결과:** [주요 IC STEP 목록](docs/step/README.md)에 개별 모델과 U1/U2 최대 외형을 추가했습니다. U1의 제조사 최대 치수는 3.0 × 4.4 × 1.5 mm, U2는 3.1 × 3.1 × 0.6 mm이므로 위의 기존 공칭 외형·높이 합산과 구분해야 합니다. U4/U5의 현재 PCB 풋프린트는 MC 패키지와 불일치하므로 제작 전에 풋프린트·배선을 교정하고 제조 자료를 재생성해야 합니다.
