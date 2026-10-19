# 현재 작업 자료 (2026-10-19)

- PPG 원본: [회로도](kicad/ppg_pcb_v08.kicad_sch), [PCB](kicad/ppg_pcb_v08.kicad_pcb).
- UART 연결 보드 원본: [회로도](kicad/ppg_uart_adapter/ppg_uart_adapter_v01.kicad_sch), [PCB](kicad/ppg_uart_adapter/ppg_uart_adapter_v01.kicad_pcb), [설계 설명](kicad/ppg_uart_adapter/README.md).
- 업체 전달용 UART 추가 소요 BOM: [PPG 양식 적용본](kicad/MVP-UART_BOM_20261013.xlsx). UART 1개당 14종·25개, 제작 수량 10개에서 250개다. 제작 수량에 따라 필요 수량이 자동 계산되며, 미지정 품번 7종은 검토사항 시트에 표시했다.
- 최신 제조 자료: 아래의 2026-10-09 PPG 10개 + UART 10개 패널 거버 및 부품 좌표 Excel.

위 UART BOM의 비교·양식 기준인 [PPG BOM 2026-10-06](kicad/MVP-PPG_BOM_20261006.xlsx)은 C17 추가 전 이력이다. UART 추가 소요 수량에서 기존 PPG 수량을 차감하지 않는다. 아래 날짜별 검증과 제조 출력은 각 작업 시점의 기록이며, 백업과 임시 파일은 로컬에 보관한다.

# PPG 10 + UART 10 — 10 mm 가이드바 패널 (2026-10-09)

사용자 지정 사진의 형식으로 **10세트(보드 20개), 2열×5행, 157×177mm** 패널을 만들었다. 상·하 10mm 가이드바, Ø3mm 가이드 홀 4개, 양면 피듀셜 각 3개, 실제 연결 탭 90개와 Ø2mm 라우팅 슬롯을 생산 거버에 반영했다. 단품 회로·배치·배선은 유지했다.

[10세트 최종 거버 ZIP](manufacturing/20261009_PPG_UART_10sets_GuideRails10mm/PPG_UART_10sets_GuideRails10mm_Gerber_20261009.zip) · [10세트 부품 좌표 Excel](manufacturing/20261009_PPG_UART_10sets_GuideRails10mm/PPG_UART_10세트_부품좌표_20261009.xlsx) · [패널 도면](manufacturing/20261009_PPG_UART_10sets_GuideRails10mm/PANEL_LAYOUT.png) · [제조·분리 방법](manufacturing/20261009_PPG_UART_10sets_GuideRails10mm/README_FABRICATION.md).

PPG 외곽 GND 보존을 위해 타공 없는 탭을 적용했고, **조립 후 지그 고정+CNC 절단**으로 분리한다. 실제 연결성·탭 최소 폭 3mm·라우팅 및 절단 경로와 부품/패드/홀 간섭을 검사했다. 좌표는 740개 단품 항목과 가이드/피듀셜 10개다. 기존 1+1 출력은 아래의 이력으로 보존하며 최신 제조 패키지와 혼용하지 않는다.

# PPG 1 + UART 1 — 연배열용 거버와 좌표 Excel (2026-10-09)

사용자 지시에 따라 최신 PPG 1개와 UART 연결 보드 1개의 거버·드릴 및 부품 좌표 Excel을 생성했다. 6층·공칭 0.8mm, 보드 사이 3mm, 완성 보드 전체 경계 68.5×25mm다. 기존 외곽 GND와 배치를 보존하는 제조사 CAM용 닫힌 외곽 2개이며, 지지 탭·가이드바·툴링·분리 방식은 제조사가 확정해야 한다.

[연배열 거버·드릴 ZIP](manufacturing/20261009_PPG_UART_1plus1/PPG_UART_1plus1_Gerber_Drill_20261009.zip) · [부품 좌표 Excel](manufacturing/20261009_PPG_UART_1plus1/PPG_UART_부품좌표_20261009.xlsx) · [배열 도면](manufacturing/20261009_PPG_UART_1plus1/ARRAY_LAYOUT.png) · [제조 메모](manufacturing/20261009_PPG_UART_1plus1/README_FABRICATION.md).

거버 13개 층의 형상·극성 및 원본 대비 드릴 168개 좌표를 검증했다. PTH Ø0.25mm 164개, NPTH Ø3mm 4개다. Excel은 74개 항목(실장 56, 납땜 패드 14, 고정홀 4)의 개별·배열 좌표와 면·회전각을 포함한다. 원본 PCB는 변경하지 않았으며, 제조 발주·GitHub 업로드는 수행하지 않았다. 아래는 직전 작업 기록이다.

# PPG / UART — 기본 비아 드릴 Ø0.25mm 및 예외 승인 규칙 (2026-10-09)

현재 작업 원본은 `kicad/ppg_pcb_v08.kicad_pcb`와 `kicad/ppg_uart_adapter/ppg_uart_adapter_v01.kicad_pcb`이다. PPG 64개, UART 100개 비아 모두 외경 Ø0.50mm / 드릴 Ø0.25mm로 적용했다. 프로젝트 최소값·비아 프리셋·DRC·생성기 기본값을 일치시켰다. 현재 승인된 Ø0.20mm 예외는 없다.

**Ø0.20mm 비아는 적용 전에 반드시 사용자 승인을 받는다.** 대상 보드·비아 위치·네트·필요 사유·제작비 영향을 설명하고 명시적 승인을 받은 뒤, 승인된 비아에만 검사 예외를 등록한다. 기본 생성값은 Ø0.25mm로 유지한다. 작업 규칙은 [AGENTS.md](AGENTS.md)에 기록했다.

PPG는 드릴 50개를 변경하고, 홀 간격 확보를 위해 배선이 붙지 않은 GND 스티칭 비아 2개만 각각 0.110mm, 0.015mm 이동했다. 부품 배치와 신호 배선은 유지했다. UART는 드릴 93개만 변경했으며 나머지 PCB 내용은 백업과 바이트 단위로 동일하다. UART 고정홀 Ø3mm 4개와 주변 Ø11mm 조립 영역은 유지했다. 두 보드 모두 전층 GND 채움을 재계산했다.

KiCad 검사: 두 보드 모두 **DRC 오류 0 / 미연결 0 / 신규 경고 0**. UART 경고·회로도 불일치 0. PPG는 변경 전부터 있던 일반 경고 5건(실크 외곽 4건, U2 라이브러리 차이 1건)과 별도 회로도 속성 경고 9건(Voltage 8건, Tolerance 1건)을 유지한다. PPG 기존 ESD 자동 검사에는 D8 패드 내부에서 만나는 배선을 패드 제거 뒤에도 남겨 두는 한계로 동일한 경고 1건이 발생하며, 이번 비아 변경 전후 결과는 같다. 세부 검사와 변경 좌표는 [검증 기록](docs/verification_via_025_20261009/), UART 최신 검사는 [연결 보드 검사](kicad/ppg_uart_adapter/pcb_verification.json)에 보관했다.

독립 검사에서 PPG의 42개 부품·패드·기존 배선과 UUID 보존, 최소 홀 사이 간격 0.256187mm, GND 11/11 영역 연결과 1~5층 외곽 연속성을 확인했다. TVS의 실제 패드 영역 안 동박을 제거하는 별도 검사에서는 SWDIO·SWCLK·NRST 3개 경로 모두 차단되어 기존 ESD 접점 통과를 확인했다([독립 검사](docs/verification_via_025_20261009/ppg_independent.json)).

수정 전 백업: `backups/before_via_drill_025_20261009_200410/`. 이번 작업에서는 거버 생성이나 GitHub 업로드를 하지 않았다. 아래 내용은 이전 작업 당시 기록이다.

# SleepBud PPG PCB v0.8 — C17 변경 배치 재배선 (2026-10-08)

사용자가 저장한 C17 바닥면 (20.5000,19.9000)mm/90° 배치를 유지하고, 이동한 GND 패드와 기존 5V 비아·배선의 간섭을 해소했습니다. 5V_LED 및 GND의 연결 경로를 다시 정리했습니다. C17은 100nF, 미터 0603이며 핀 1=5V_LED, 핀 2=GND입니다.

간섭이 있던 5V 비아를 제거하여 전체 비아는 66→65개입니다. C17 전원은 1.138mm, GND는 0.830mm 직선으로 연결했습니다. C1의 1.933mm 연결 중 1.145mm는 선폭 0.30mm, 간격이 좁은 0.788mm 구간은 0.15mm입니다. 기존 부품과 다른 네트 배선을 유지하는 경로를 택해 5V_LED 동박 총길이는 10.382→11.589mm로 1.207mm 늘었습니다.

기존 42개 부품의 위치·각도·패드 형상과 연결을 보존하고, 변경 범위를 5V_LED/GND 동박으로 제한했습니다. 사용자가 조정한 SCL/SDA 등 다른 신호 배선과 회로도·프로젝트·규칙은 유지했습니다. 전층 GND를 다시 채웠고 15/15 GND 영역 연결, 1~5층 외곽 GND 연속성을 확인했습니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 42개 부품·125개 번호 핀의 회로도/PCB 일치, 다중 핀 네트 연결, 기존 ESD 경로 및 부품 간섭 검사를 통과했습니다.

[C17 배선 전후](docs/review_C17_reroute_20261008/placement_reroute_comparison.png) · [검증 기록](docs/verification_C17_reroute_20261008/). PCB SHA256: `eae91e981d70ecab493e7879cb164b4153b4c0e78430ac3255dfbea034b25f30`. 백업: `backups/20261008_before_C17_reroute/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — C17 PCB 추가 (2026-10-08)

최신 회로도에 추가된 C17을 PCB에 반영했습니다. 값은 100nF, 풋프린트는 Capacitor_SMD:C_0201_0603Metric(미터 0603, 0.6×0.3mm), 핀 1은 5V_LED, 핀 2는 GND입니다. C17은 바닥면 (20.7500,19.6550)mm/-90°에 배치하고 전원과 GND를 연결했습니다. 회로도의 C17 Description 필드는 복사된 문구인 "U2 VDD bypass"로 남아 있으나, PCB에는 실제 회로도 네트인 5V_LED–GND를 반영했습니다.

기존 41개 부품의 배치·패드와 모든 기존 배선 형상을 보존했습니다. 회로도·프로젝트·규칙 파일도 변경하지 않았으며, C17 항목을 부품 데이터에 추가했습니다. 전층 GND를 다시 채웠고, 14/14 GND 영역 연결과 1~5층 외곽 GND 연속성을 확인했습니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 총 42개 부품·125개 번호 핀의 회로도/PCB 일치, 네트 연결과 기존 ESD 경로를 검사했습니다. C17 조립 영역과 주변 부품 간섭 검사를 통과했습니다.

[C17 배치 보기](docs/review_C17_20261008/placement_reroute_comparison.png) · [검증 기록](docs/verification_C17_20261008/). PCB SHA256: `b397c72e3ba9275c58eccc9b854cc602f6b2ea16302c17b6da636f57b90675ac`. 백업: `backups/20261008_before_C17_addition/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — RXN/RXP 패드 교환 및 재배선 (2026-10-08)

사용자가 변경한 R3 (14.1029,17.0)mm/90°, R7 (15.6,17.6)mm/180°, R8 (15.6,16.3)mm/180° 배치를 유지했습니다. 요청에 따라 바닥면 외부 패드 J6/RXN은 위쪽 (15.0655,13.9497)mm, J5/RXP는 아래쪽 (14.8181,19.6172)mm으로 서로 위치를 바꿨습니다. 각 패드의 참조번호·네트·각도는 보존했으며 나머지 39개 부품과 탑면 센서는 움직이지 않았습니다.

RXN/RXP 및 수신 IC까지의 RXN_RCV/RXP_RCV 경로를 재배선했습니다. RXP는 J5→R7→U6.6(A), RXN은 J6→R8→U6.4(B)로 연결하고, R3.1은 RXP, R3.2는 RXN의 연결을 유지했습니다. 사용자가 수정한 SCL 배선을 포함한 다른 네트의 배선 형상과 회로도는 보존했습니다.

수신 네트 4개 동박 길이 합계 19.139→14.801mm. 전체 비아 65→63개. 길이는 비아 수직 길이를 제외한 값입니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 전층 GND 채움 완료, 13/13 GND 동박 영역 연결. 부품 간 조립 영역·몸체·패드 간섭 및 극성 검증 통과. 123핀 회로도 연결, 다중 핀 23네트와 기존 ESD 3경로도 검사했습니다. 6층 구성, 2층 무배선, 외곽 GND와 선폭·비아 규칙을 유지했습니다.

[배선 전후](docs/review_placement_reroute_20261008e/placement_reroute_comparison.png) · [검증 기록](docs/verification_placement_reroute_20261008e/). PCB SHA256: `2ef282c3a06786d3a7ee80a30bc4c60e2382d900a44287dbae603c8d80d230de`. 백업: `backups/20261008_before_placement_reroute_e/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — C11/C15 수정 배치 재배선 (2026-10-08)

사용자가 옮긴 C11은 NRST 배선 통로 확보를 위해 바닥면에서 아래로 0.20mm 미세 조정하여 (18.0,19.6)mm/180°에 배치했습니다. U4는 조립 간격과 원형 보드 외곽 여유를 확보하도록 오른쪽 0.40mm, 아래로 0.20mm 옮겨 (18.7257,21.7439)mm/180°에 배치했습니다. 앞서 허용한 바닥면 간섭 미세 조정 범위이며 C15 (19.4,19.4)mm/0°와 U1·D8을 포함한 나머지 39개 부품은 유지했습니다. 전체 151개 패드의 형상·네트를 보존하고, 영향을 받은 전원·GND·NRST 경로를 정리했습니다.

C11/C15의 전원 연결과 MCU 급전을 다시 정리하고, 이전 위치로 향하는 불필요한 배선을 제거했습니다. 5V_LED의 잘게 나뉜 꺾임은 직선·원호로 정리했습니다. NRST는 외부 패드→D8 신호 접점→MCU 순서가 유지되는지 접점 제거 검사를 통과했습니다.

저장된 PCB의 실제 형상 기준으로 같은 면 부품 간 조립 영역·몸체·패드 겹침은 0건입니다. U4 몸체와 원형 보드 외곽 사이 여유는 0.1048mm, 동박 패드 여유는 0.5585mm입니다. U4 조립 영역 표시(Courtyard)는 외곽 밖으로 0.2108mm 돌출하며(이전 0.1834mm), 실제 부품 몸체는 보드 안에 있습니다.

평면 배선 합계: 3.3V 40.650→36.175mm, 5V_LED 10.536→9.351mm, 12V 14.724→14.163mm, NRST 5.564→5.200mm. 전체 비아 65→65개. 길이는 비아 수직 길이를 제외한 동박 합계이며, 모든 네트가 짧아졌다는 의미는 아닙니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 전층 GND 채움, 13/13 GND 동박 영역 연결, ESD 3경로·회로도 123핀·다중 핀 23네트 검사 통과. 2층 무배선, 1~5층 외곽 GND, 선폭·비아 규칙을 유지했습니다. 회로도·프로젝트·규칙과 관련 없는 배선은 보존했습니다.

[배선 전후](docs/review_placement_reroute_20261008d/placement_reroute_comparison.png) · [검증 기록](docs/verification_placement_reroute_20261008d/). PCB SHA256: `bbd74454cdfd2f07445fb08227b9e11855be98583af45f1e497f3e75ff5221ce`. 변경 전 백업: `backups/20261008_before_placement_reroute_d/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — 3.3V 전체 경로 정리 (2026-10-08)

사용자가 수정한 C14 배치와 SWCLK 경로를 포함해 41개 부품의 위치·각도·면 및 신호 배선을 그대로 유지했습니다. 3.3V 연결망 전체를 다시 구성해 중복 급전 루프, 중앙 VREF 주변 우회와 서쪽의 긴 돌아가는 경로를 정리했습니다. U3–C16은 직결하고 필요한 방향 전환에는 원호를 적용했습니다. C14 전원 비아와 이전 꼬리 배선을 정리해 GND 패드와의 접촉을 해소했습니다.

3.3V 평면 배선 합계 **50.095 → 40.764 mm**, **18.6% 감소**. 4층 3.3V는 **35.293 → 26.266 mm**, 동박 요소 45→27개입니다. 전원 비아는 8→8개이며, 전체 비아는 65개입니다. 길이는 비아 수직 길이를 제외한 평면 동박 합계입니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 전층 GND 채움, 15/15 GND 동박 영역 연결, ESD 3경로·회로도 123핀·다중 핀 23네트 검사 통과. 2층 무배선, 1~5층 외곽 GND, 선폭·비아 규칙을 유지했습니다. 회로도·프로젝트·규칙은 변경하지 않았습니다.

[3.3V 배선 전후](docs/review_3V3_cleanup_20261008c/3V3_cleanup_comparison.png) · [검증 기록](docs/verification_3V3_cleanup_20261008c/). PCB SHA256: `2f48cc14bab60c231189b33674a6b2a69fc755beff8a993c0c3906d5b9a2893a`. 변경 전 백업: `backups/20261008_before_3V3_cleanup/kicad_before_reroute.zip`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — U3/R4/R5/C6/C16 수정 배치 재배선 (2026-10-08)

사용자가 조정한 U3, R4, R5, C6, C16을 포함해 41개 부품의 위치·각도·면과 151개 패드 형상·네트를 그대로 유지했습니다. 변경 전 파일은 `backups/20261008_before_placement_reroute_b/kicad_before_reroute.zip`에 백업했습니다.

이동 전 패드로 향하는 배선을 제거하고 UART_TX, TXP/TXN, 3.3V와 GND 귀환을 새 배치에 맞춰 연결했습니다. 이동한 패드와 겹쳐 신호 네트로 재지정된 기존 GND 비아/배선도 제거하고 필요한 GND 연결을 다시 확보했습니다. TXP는 바닥면으로 연결하고 TXN은 3층을 이용합니다. 새 배치의 평면 배선 합계는 TXP 5.765 mm, TXN 7.755 mm, UART_TX 9.604 mm입니다. 기존 위치와 경로 조건이 다르므로 모든 신호의 길이가 줄었다는 의미는 아닙니다. 전체 비아는 65개입니다.

C16의 GND 비아는 (24.15,15.85)mm, 3.3V 비아는 (24.65,15.35)mm로 나눠 배치했습니다. 전원 연결의 0.650mm 병목 구간만 0.15mm 선폭을 적용하고 양끝은 0.30mm, 4층 공급선은 0.40mm를 유지했습니다. 기존 동쪽 C6 전원 분기를 제거했고, R4 전원은 0.760mm 직선입니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 전층 GND 채움, 15/15 GND 동박 영역 연결, ESD 3경로·회로도 123핀·다중 핀 23네트 검사 통과. 2층 무배선, 1~5층 외곽 GND, 선폭·비아 규칙을 확인했습니다. 회로도·프로젝트·규칙과 관련 없는 배선은 보존했습니다.

[배선 전후](docs/review_placement_reroute_20261008b/placement_reroute_comparison.png) · [검증 기록](docs/verification_placement_reroute_20261008b/). PCB SHA256: `91a72755b21ff8630c9eac5422dce37eba7e7a8c27bb0fce6ad39a48cbc9a3b1`. 거버 생성과 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — 수정 배치 C5/R2/R1 재배선 (2026-10-08)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)에 사용자가 저장한 C5 (21.2,16.2)mm/180°, R2 (21.2,16.9)mm/0°, R1 (21.2,17.6)mm/0° 배치를 그대로 유지해 배선했습니다. 전체 41개 부품의 위치·각도·면 및 151개 패드의 형상·네트를 보존했습니다.

기존 저항 위치로 향하던 B면 배선 10개를 직선 2개로 바꿨습니다. SDA는 기존 비아를 분기점으로 활용해 MCU에서 비아까지의 배선을 공유하고, SCL은 MCU에서 새 R2로 직결했습니다. SDA **6.850→5.904 mm**, SCL **7.860→7.320 mm**, VREF **2.037→1.589 mm**로 단축했습니다. 3.3V와 VREF 비아는 기존 두 자리의 역할을 교환했고, 전체 비아는 **65개 유지**입니다.

C5 GND는 기존 C4 GND 귀환을 공유하며, C5에서 비아까지 실제 경로는 1.781→1.612mm입니다. 새 3.3V 비아 급전을 위해 4층 0.40mm 배선을 국소 수정해 3.3V 전체 길이는45.095→47.042mm로 늘었습니다. 전체 평면 배선 합계는 183.782→183.126mm입니다. 센서 쪽 기존 I2C 경로는 다른 신호와의 간섭 및 추가 변경 비용을 검토한 뒤 유지했습니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. 전층 GND 채움 완료, 16/16 GND 동박 영역 연결, ESD 3경로·회로도 123핀·다중 핀 23네트 검사 통과. 2층 무배선, 1~5층 외곽 GND, 선폭·비아 규칙을 유지했습니다.

[변경 전후](docs/review_placement_route_20261008/placement_route_comparison.png) · [검증 기록](docs/verification_placement_route_20261008/). PCB SHA256: `4a753412db677bffd4155f628a6ae2fa6ba472ef047550a04ff7c33ec5107719`. 변경 전 백업은 `backups/20261008_before_R1_R2_C5_reroute/kicad_before_R1_R2_C5.zip`입니다. 회로도·프로젝트·규칙은 변경하지 않았으며 거버와 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — TXP/TXN 저항 위치 교환 (2026-10-08)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)에서 R5(TXP)와 R6(TXN)의 위치를 맞바꾸고 관련 4개 네트를 재배선했습니다. 부품번호·저항값(22Ω/1005)·회로 연결은 유지했습니다. R5는 (24.7408,16.8914)mm/315°, R6는 (23.7,18.2)mm/270°입니다.

TXP 배선은 **12.233 → 4.939 mm**, TXN은 **7.752 → 7.464 mm**로 줄었습니다. 합계 **19.984 → 12.402 mm, 37.94% 단축**이며 TX 비아는 **6 → 2개**입니다. 저항에서 J3/J4까지 모두 B면 직결이고, TXP 전체도 B면 연결입니다. TXN 드라이버는 3층 직선과 양쪽 짧은 B면 연결로 구성했습니다. 기존 5층 TX 배선은 제거했습니다. 길이는 비아 수직 길이를 제외한 평면 동박 길이입니다.

사용자가 옮긴 R4/C5의 방향과 배치 의도를 유지하면서 R4는 (+0.20,+0.20)mm, C5는 (0,+0.05)mm 미세 조정했습니다. 두 조립 여유 영역 겹침, VREF 비아 간격 문제, 미연결 4곳을 해결했습니다. 모든 탑면 부품은 고정했고 나머지 부품·관련 없는 동박을 보존했습니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건 유지. ESD 3경로·회로도 123핀·다중 핀 23네트 연결을 확인했습니다. 전층 GND 채움 완료, 16/16 GND 영역 연결, 층·외곽 GND·선폭·비아 정책 통과. 전체 비아는 65개입니다.

[변경 전후](docs/review_tx_swap_20261008/tx_swap_comparison.png) · [검증 기록](docs/verification_tx_swap_20261008/). PCB SHA256: `245b0b48098faec4ebdd3d13e3f7ad531b1e78041a6bfc9b882eddd679ae5507`. 변경 전 파일은 `backups/20261008_before_TX_resistor_swap/kicad_before_TX_swap.zip`에 백업했습니다. 거버와 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — U2 서측 이동 및 C4 배선 정리 (2026-10-08)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)에 U2의 9시 방향 1.8 mm 이동을 반영했습니다. C4는 바닥면 북쪽으로 옮기고 R1/R2/R4/C1/C15/D8의 위치 또는 방향과 관련 배선을 조정했습니다. U1을 포함한 모든 탑면 부품은 고정했습니다. C4의 U1.4(VLDO) 배선은 **3.153 → 2.345 mm**로 짧아졌습니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0 · 기존 경고 5건 유지.** 신규 부품 몸체/조립 여유 영역 간섭이 없고, 기존 C11/U5 및 C14/U5 조립 여유 영역 겹침은 늘어나지 않았습니다. ESD 접점 경로 3곳, 회로도 핀 123개, 다중 핀 네트 23개 연결을 확인했습니다. 전층 GND를 재채움했고 15/15 동박 연결 영역이 GND 단자에 연결됩니다. 2층 무배선, 1~5층 외곽 GND, 최소 선폭/비아 규칙을 유지했습니다. 비아는 71 → 69개입니다.

[배치·C4 경로 전후](docs/review_u2_c4_20261008/u2_c4_comparison.png) · [검증 기록](docs/verification_u2_c4_20261008/). 네트별 길이 증감은 검증 기록의 independent_verification.json에 보관했습니다. 회로도·프로젝트·설계 규칙은 변경하지 않았습니다.

PCB SHA256: `0db206e568dc9441220bb5e9327dbec5d7b70599d49fd8e6ac2166f2f1b90cc9`. 변경 전 백업은 `backups/20261008_before_U2_C4_apply/kicad_before_U2_C4.zip`입니다. 배치와 배선 검토용 로컬 원본에 저장했으며 거버와 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — 배선 연결 정리 (2026-10-07)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)에 사용자 최신 배치를 유지하면서 NRST의 D8 우회와 C13의 12V 접속을 정리했습니다. **J9 → 기존 진입 비아 → D8 신호패드 접점 → 추가 보호측 비아 → 3층 → U2.4** 순서입니다. D8은 바닥면 (16.6,19.0)mm / 90°를 유지하고, 보호측 비아 0.50/0.20mm를 (17.15,19.20)mm에 추가했습니다. TVS는 신호–GND 병렬 보호소자입니다.

C13.1–12V 비아를 폭 0.15mm / 길이 0.5521mm로 직접 연결했습니다. 사용자 복구한 비아–U4.8 입력 배선도 유지했습니다. D8 GND는 기존 비아까지 폭 0.30mm / 길이 0.8591mm로 연결했습니다. 전체 41개 부품·패드·기존 비아 위치를 보존했으며 R4 10kΩ UART_TX 풀업도 그대로입니다. 비아는 70→71개입니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0 · 기존 경고 5건**입니다. D6·D7·D8 ESD 접점 경로 검사 통과, D8 패드 영역의 동박을 제거하는 별도 검사에서도 우회 경로가 없음을 확인했습니다. 전층 GND를 재채움했고 15/15 GND 연결 영역이 J2.1에 도달합니다. 외곽 GND·층·선폭·비아 규칙과 회로도 핀 일치 검사도 통과했습니다.

[배선 수정 전후](docs/review_routing_connections_20261007/connections_before_after.png) · [검증 기록](docs/verification_routing_connections_20261007/).

PCB SHA256: `6f5485a1f81b4cb11914d462fbb74e58576903f7c1595e6b5ecb7f60054ed806`. 로컬 원본에 저장했습니다. 거버·드릴·BOM 및 GitHub 업로드는 이번 작업 범위에 포함하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — SCL 1층 직결 (2026-10-06)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)의 R2 쪽 SCL 비아에서 U1.2까지 1층에서 바로 연결했습니다. 1층 우회는 1.999→0.798mm, 3층 우회는 5.753→4.182mm로 줄였습니다. SCL 총 길이는 9.352→6.580mm(2.773mm 단축)이며 불필요한 SCL 비아 1개를 제거했습니다. 전체 비아는 69개입니다.

41개 부품·패드·나머지 비아와 다른 넷의 배선은 그대로입니다. U1 고정, D8 바닥면 유지, TVS를 먼저 거치는 연결을 보존했습니다. **DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건은 동일합니다. ESD 경로 3곳, 전층 GND 연결(13/13 영역), 외곽 GND 및 선폭·비아·층 규칙도 통과했습니다.

[SCL 수정 전후](docs/review_scl_top_20261006/scl_before_after.png) · [검증 기록](docs/verification_scl_top_20261006/).

PCB SHA256: `5c4c9d1eabbfb2f3db410d5fa80927defbf1545fe8b773ff937ddca9fa6ac063`. 로컬 원본 저장 완료. 거버·드릴·BOM 생성 및 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — TVS 배선 순서 수정 (2026-10-06)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)의 ESD 우회 배선을 수정했습니다. J7→D6 접점→내부 비아→U2.16, J8→D7 접점→내부 비아→U2.17 순서로 배선했습니다. 바닥면 D8은 J9→진입 비아→D8 접점→내부 배선→U2.4 순서입니다. TVS의 신호 패드가 외부선과 내부선의 접점이며, 보호소자는 신호와 GND 사이의 병렬 연결을 유지합니다.

**41개 부품의 위치·각도·면 및 패드는 전부 유지했습니다. U1은 탑면 고정, D8은 기존 바닥면 위치 그대로입니다. 탑면 부품 배치 변경은 위치안을 먼저 제시하고 사용자 확인 후 적용합니다.**

D6·D7·D8 GND 귀환은 폭 0.30mm로 기존 GND 비아에 연결했습니다. NRST 진입 비아를 X -0.010mm/Y -0.050mm 이동했고, D8 보호측 통로를 막던 GND 비아 1개를 제거했습니다. 전체 비아는 70개입니다. 전층 GND를 재채움했고 13/13 연결 영역이 GND 단자 J2.1에 연결됩니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건은 동일합니다. 별도 구리 연결 검사에서 D6·D7·D8 접점을 우회하는 IC 경로가 없음을 확인했습니다. 이 검사를 `kicad/netcheck_v08.py`에도 추가했습니다. 1~5층 외곽 GND, 2층 무배선, 최소 선폭 및 비아 규격도 통과했습니다. 이는 PCB 연결·배선 검사이며 실물 ESD 내성 시험을 대신하지 않습니다.

TVS 접점을 먼저 거친 뒤 내부 비아로 배선하는 기준은 [TI ESD 배선 가이드](https://www.ti.com/document-viewer/lit/html/SLVAEX9B/GUID-5B25B8F3-9415-48A5-8854-CD5714AA5D6E)를 참고했습니다. D8에는 사용자가 지정한 바닥면 배치에 필요한 진입 비아가 있습니다.

[ESD 배선 확대](docs/review_esd_flow_20261006/esd_detail.png) · [전층 검토](docs/review_esd_flow_20261006/layers/six_layers.png) · [검증 기록](docs/verification_esd_flow_20261006/).

PCB SHA256: `9caf20e4383d00f97e604291ab7e9c29394bed81c2da8c6ed2c2addbab580384`. 로컬 원본 저장 완료. 거버·드릴·BOM 및 GitHub 업로드는 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — SWCLK·VREF 배선 정리 (2026-10-06)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)에 최신 사용자 배선을 기준으로 SWCLK·VREF의 짧은 분할과 불필요한 꺾임을 정리했습니다. 4층 SWCLK의 직선 24개는 직선 4개와 R0.478mm 원호 3개로 바꿨고, 바닥면 VREF의 직선 3개는 직선 하나로 합쳤습니다. SWCLK는 9.2739→9.0607mm, VREF는 2.5595→2.4418mm로 전체 0.3310mm 단축됐습니다.

탑면 PPG 센서 U1을 포함한 41개 부품·모든 패드와 비아 71개의 위치·규격을 유지했습니다. 다른 넷의 배선도 동일합니다. **DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건은 동일합니다. 전층 GND 재채움 후 전체 GND 연결(13/13 영역), 1~5층 외곽 GND 연속성, 2층 무배선, 최소 선폭 0.15mm와 비아 규격을 확인했습니다.

[전층 검토 이미지](docs/review_routing_refine_20261006/layers/six_layers.png) · [검증 기록](docs/verification_routing_refine_20261006/).

PCB SHA256: `67b9e0a161565ff865ad6a17902c53fbecc39c5072f45e77c577ac987b9ab87d`. 로컬 원본에 저장했습니다. 이번 작업에서는 거버·드릴·BOM 및 GitHub 업로드를 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — 부품 간섭 정리 (2026-10-06)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)의 탑면 PPG 센서 U1 위치·각도·패드를 유지했습니다. 사용자의 최신 배치를 기준으로 C5를 오른쪽 0.225mm/아래 0.56mm, R5를 위쪽 0.10mm 미세 조정해 간섭과 연결을 정리했습니다. 다른 부품은 그대로입니다.

VREF·TXP_DRV·TXP·SWCLK의 영향 구간을 조정하고 C5 근처에 GND 비아(랜드 0.50mm/드릴 0.20mm) 1개를 추가했습니다. VREF 배선은 5.051mm, 전체 배선은 1.959mm 짧아졌으며 비아는 71개입니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**. 기존 경고 5건(U4·U5 실크 외곽 4건, U2 라이브러리 차이 1건)은 동일합니다. 41개 부품·123개 번호 핀의 연결, 최소 선폭 0.15mm와 비아 규격을 확인했습니다. 전층 GND 재채움, 전체 GND 연결(14/14 영역), 1~5층 외곽 GND 연속성 및 2층 무배선을 검증했습니다.

[전층 검토 이미지](docs/review_placement_cleanup_20261006/layers/six_layers.png) · [검증 기록](docs/verification_placement_cleanup_20261006/).

PCB SHA256: `e0328b245de0281effbb0ba79942b417090891ca4a4f0d901ac16a0b8efa0a21`. 로컬 원본 저장 완료. 거버·드릴·BOM 및 GitHub 업로드는 이번 작업에서 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

# SleepBud PPG PCB v0.8 — 변경 배치 반영 (2026-10-06)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)에 C1·C4·R1·R2·D8의 이동을 반영해 전원·I²C·리셋 배선을 다시 연결했습니다. 최소 선폭과 조립 여유 확보를 위해 사용자 배치에서 C1만 아래로 0.15mm, C4만 오른쪽으로 0.08mm 미세 조정했습니다. 나머지 부품 위치·각도·패드 연결은 유지했습니다.

NRST는 5층의 3.616mm 연결을 사용하고, 4층 3.3V의 중간 꺾임을 합쳐 폭 0.40mm/R0.40 원호로 정리했습니다. 12V는 이동한 SDA 비아를 피하도록 조정했습니다. 전체 배선 길이는 입력 파일보다 3.118mm 줄었으며 비아는 70개입니다.

**DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건(U4·U5 실크 외곽 4건, U2 라이브러리 차이 1건)은 동일합니다. 41개 부품·123개 핀이 회로도와 일치합니다. 전층 GND를 재채움했고 16개 구리 연결 영역 모두 J2.1에 연결됩니다. 1~5층 외곽 GND 연속성, 2층 무배선, 최소 선폭 0.15mm, 비아 규격을 확인했습니다.

[전층 검토 이미지](docs/review_placement_20261006/layers/six_layers.png) · [검증 기록](docs/verification_placement_20261006/).

PCB SHA256: `42224bb6b24e6fadfa758637256e70588f81b92c895da37d11371f9d5dfd237f`. 로컬 원본 저장 완료. 거버·드릴·BOM 및 GitHub 업로드는 이번 작업에서 진행하지 않았습니다.

<details>
<summary>Previous work records / 이전 작업 기록</summary>

> 최신 수정 — 2026-10-06: 중앙 3.3V의 불필요한 V자 꺾임을 제거하고 폭 0.40mm 직접 연결과 원호로 대체했습니다. 해당 경로 0.6765mm 단축, DRC 오류 0·미연결 0·회로도 불일치 0·기존 경고 5건. 기존 원호 56개를 보존하고 1개를 추가했습니다. PCB SHA256: `d31a87e7ca3bec457658657d579a00a1d0a14226ededab17be3ef085d721ba52`. 아래 기록은 이 수정 이전 단계입니다. 거버 미생성.

# SleepBud PPG PCB v0.8 — 꺾임 정리 및 곡선 배선 (2026-10-06)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)의 같은 직선 위 중간 분할 8곳을 합치고, 공간이 확보된 56개 코너를 실제 KiCad 원호(PCB_ARC)로 바꿨습니다. 곡선은 기존 직선에 접선 방향으로 이어지며, 짧은 패드 탈출 구간과 분기점 부근은 직선으로 유지했습니다.

| 층 | 적용 원호 수 |
|---|---:|
| 1층 | 14 |
| 2층 | 0 — 무배선 GND 층 유지 |
| 3층 | 10 |
| 4층 | 20 |
| 5층 | 3 |
| 6층 | 9 |

전체 배선은 직선 313개와 원호 56개이며 길이는 199.685 → 199.451mm입니다. 부품 41개·패드 151개·비아 70개의 위치·각도·넷과 123개 번호 핀 연결을 유지했습니다. 최소 선폭 0.15mm, 4층 3.3V 선폭 0.30/0.40mm, 비아 규격도 그대로입니다.

원본 파일 검사: **DRC 오류 0 · 미연결 0 · 회로도 불일치 0**, 기존 경고 5건은 동일합니다. 모든 곡선 끝의 접점과 접선을 확인했고 최대 접선 각도 오차는 0.019575°입니다. 전층 GND 재채움 후 전체 GND 연결 및 1~5층 외곽 연속성을 확인했습니다. 설계 규칙이나 검사 심각도는 바꾸지 않았습니다.

[4층 곡선화 전후](docs/review_curves_20261006/curve_before_after.png) · [전층 검토](docs/review_curves_20261006/layers/six_layers.png) · [검증 기록](docs/verification_curves_20261006/)

현재 PCB SHA256: `9a20272bce551736dd36ffd91ece1cbf10b4da316c59067ebb4d4ec9ea205e0e`.
**거버·드릴·BOM은 생성하거나 갱신하지 않았습니다. 이번 배선은 로컬 원본에 저장했으며 GitHub에는 추가 업로드하지 않았습니다.**

<details>
<summary>이전 4층 3.3V 최적화 기록 — 곡선화 전</summary>

# SleepBud PPG PCB v0.8 — 4층 3.3V 배선 최적화 (2026-10-06)

사용자가 수정한 [현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)의 바닥면 U2.2→C15 전원 연결, 전원 비아 삭제 및 중앙 45° 코너를 유지하고, 4층(In3.Cu)의 3.3V 경로만 정리했습니다. 비아가 제거된 자리의 V자 중복 연결과 불필요한 꺾임을 줄였습니다.

| 항목 | 사용자 수정본 | 최적화 후 |
|---|---:|---:|
| 4층 3.3V 배선 길이 | 30.014mm | 28.224mm |
| 4층 3.3V 배선 구간 | 37 | 27 |
| 4층 GND 면적 | 70.285mm² | 70.649mm² |

GND 면적은 양쪽 모두 동일 조건으로 재채움한 후 비교했습니다. 4층 전원 선폭 0.30/0.40mm, 전체 최소 선폭 0.15mm를 유지합니다. 41개 부품과 패드의 위치·각도·연결, 비아 70개, 다른 층 및 다른 넷의 배선은 사용자 수정본과 동일합니다.

원본 파일 검사: **DRC 오류 0 · 미연결 0 · 회로도 불일치 0**. 기존 경고 5건(U4·U5 실크 외곽 4건, U2 라이브러리 차이 1건)은 동일합니다. 전층 GND를 재채움했고 17개 연결 영역 모두 J2.1에 연결됩니다. 1~5층 외곽 GND 연속성, 2층 무배선, 비아 규격도 통과했습니다.

[4층 전후 비교](docs/review_l4_power_20261006/l4_power_before_after.png) · [전층 검토](docs/review_l4_power_20261006/layers/six_layers.png) · [검증 기록](docs/verification_l4_power_20261006/)

현재 PCB SHA256: `3978af66433edf39972056465ec87a712339e6beff50f82e82f3de54fd9c657c`.
**거버·드릴·BOM은 생성하거나 갱신하지 않았습니다. 사용자 검토 후 거버 생성 지시를 기다립니다. 이번 배선은 로컬 원본에 저장했으며 GitHub에는 추가 업로드하지 않았습니다.**


</details>

<details>
<summary>이전 C15·C16 배선 완료 기록 — 2026-10-06</summary>

# SleepBud PPG PCB v0.8 — 배선 완료·검토 대기 (2026-10-06)

[현재 PCB](kicad/ppg_pcb_v08.kicad_pcb)에 D6·D7 탑면 이동과 C15·C16 100nF/16V/X7R 미터 0603 추가 배선을 반영했습니다. 135°·225°·315° SMT 배치 허용에 따라 기존 사선 배치를 유지했습니다. 중지했던 수정본에서 부품 위치·각도와 기존 배선을 그대로 두고 C15·C16의 3.3V 연결 두 곳을 완료했습니다.

C15는 기존 전원 비아를 재사용합니다. C16은 전원 비아 1개(랜드 0.50mm / 드릴 0.25mm)를 추가해 바닥면 배선을 짧게 연결했습니다. 새 전원 패턴은 총 1.688mm(바닥면 1.524mm, 4층 0.164mm)이며, 전체 최소 선폭 0.15mm와 4층 3.3V 주배선 폭 0.30mm 이상을 유지합니다.

원본 파일 기준 **DRC 오류 0, 미연결 0, 회로도 불일치 0**입니다. 기존 경고 5건(U4·U5 실크 외곽 4건, U2 풋프린트 라이브러리 차이 1건)은 동일합니다. 41개 레퍼런스·123개 핀 연결이 회로도와 일치합니다. 전층 GND를 재채움했고, 17개 GND 연결 영역 전체가 J2.1에 연결되며 1~5층 외곽 GND도 연속입니다. 2층은 무배선, 5층 기존 짧은 배선은 유지합니다.

[6층 배선·GND 미리보기](docs/review_routing_20261006/layers/six_layers.png) · [D6/D7·C15/C16 확대](docs/review_routing_20261006/layers/top_esd_and_caps.png) · [검증 기록](docs/verification_routing_20261006/) · [회로도](kicad/ppg_pcb_v08.kicad_sch)

**이번 작업은 배선과 검토 자료까지만 완료했습니다. 거버는 사용자 검토 후 별도 지시에 따라 생성합니다. 기존 제조 출력·BOM은 갱신하지 않았으며 현재 PCB용 제조 자료로 사용하지 않습니다.**


</details>

<details>
<summary>이전 로컬 PCB 완료 단계 기록 — 2026-10-05</summary>

# SleepBud PPG PCB v0.8 — 6층 전층 GND, 탑면 SWD 패드

2026-10-05 현재 [원본 PCB](kicad/ppg_pcb_v08.kicad_pcb)는 **6층·Ø13.5mm·공칭 0.8mm**, 최소 배선 폭 **0.15mm**입니다. 39레퍼런스(구매 부품 28개 + 구리 패드 11개), 번호 있는 패드 119개, 회로도 넷 48개를 유지했습니다. ERC 0, DRC 오류 0·미연결 0·회로도 불일치 0이며 기존 경고 5개(실크 외곽 4, U2 라이브러리 도형 불일치 1)는 남아 있습니다. [현재 검증 원자료](docs/verification_all_ground_20261005/), [현재 6층 검토 이미지](docs/review_all_ground_20261005/layers/six_layers.png).

사용자 지시의 우선순위는 **L1~L5 외곽 GND 연속 확보**, 탑 GND 확대, 바텀 배선 최소화입니다. L2는 GND 전용, L5는 GND 중심으로 필요한 짧은 우회를 허용합니다. 2026-10-05 추가 요청에 따라 **L1~L6 전층의 가용 영역을 GND로 채웠습니다.** L3/L4의 중앙 제외 영역을 제거하고 L6 바텀 GND를 추가했습니다. L1~L5 외곽 띠는 유지하며, L6는 연속 외곽 띠를 강제하지 않습니다. 이번 GND 단계에서 부품·배선·비아는 이동하지 않았습니다.

| 층 | 현재 구성 | 배선 길이 | GND 푸어 면적 |
|---|---|---:|---:|
| L1 F.Cu | U1 + SWD 패드 5개, GND 푸어와 짧은 연결 | 30.262mm | 93.914mm² |
| L2 In1.Cu | GND 전용, 배선 없음 | 0.000mm | 103.592mm² |
| L3 In2.Cu | 신호·일부 전원 연결, 전면적 GND 푸어 | 40.567mm | 88.189mm² |
| L4 In3.Cu | 3V3 분배·보조 신호, 전면적 GND 푸어 | 53.395mm | 70.941mm² |
| L5 In4.Cu | GND 중심, 필요한 짧은 우회 | 5.930mm | 101.160mm² |
| L6 B.Cu | 나머지 33레퍼런스, 부품 주변 연결과 GND | 69.080mm | 49.929mm² |

현재 배선은 322구간이며 최소 0.15mm입니다(0.15mm 235개 / 0.2mm 40개 / 0.3mm 12개 / 0.4mm 35개). 비아 외경은 모두 Ø0.50mm입니다. 신호 28개와 GND 28개는 드릴 Ø0.20mm, 전원·기준전압 15개는 드릴 Ø0.25mm로 총 71개입니다. 전원·기준전압은 3V3/5V_LED/12V/12V_IN/VLDO/VREF이며 LDO_EN은 신호입니다.

TXP J3의 사용자 이동 위치 **(25.5,15.9)mm / 270° / B.Cu**를 유지하고 생성 소스 좌표도 동기화했습니다. [TXP 검사 이력](docs/verification_txp_move_20261005/), [이번 GND 변경 비교](docs/review_all_ground_20261005/pcb_change.json), [현재 독립 감사](docs/verification_all_ground_20261005/independent_audit.json).

사용자가 이동한 R4를 기준으로 배선을 복구한 후, 추가 요청에 따라 조립 여유 영역 겹침도 해소했습니다. 최종 R4는 (20.050, 14.550)mm / 90°, C7은 (20.025, 12.330)mm / 90°입니다. C7은 사용자 위치에서 오른쪽으로 0.025mm만 옮겨 U6 전원 바이패스 배치를 유지했습니다. D1의 사용자 위치와 나머지 큰 IC·FB1 배치를 유지했습니다. 관련 비아와 팬아웃을 조정하고 옛 R4 전용의 불필요한 연결을 정리했습니다. [배치·배선 변경 상세](docs/review_r4_move_20261005/pcb_change.json), [독립 비교 감사](docs/verification_r4_move_20261005/independent_audit.json), [R4·C7 확대도](docs/review_r4_move_20261005/layers/r4_assembly_detail.png).

부품 수 39개, 풋프린트와 물리 패드의 UUID, 119개 핀의 넷 및 회로도 논리는 유지했습니다. 조립 여유 영역을 포함한 DRC 오류·미연결·회로도 불일치는 0건이며 검사 심각도나 허용 간격을 완화하지 않았습니다. 사용자 저장본의 변경 내용은 [비교 기록](docs/verification_r4_move_20261005/user_change_audit.json)에 구분했습니다.

이전 선폭·비아 단계에서는 0.10mm 배선을 모두 0.15mm 이상으로 넓히고 외곽 GND 비아 10개를 추가했습니다. 당시 이미지·검증은 [선폭·비아 변경 이력](docs/verification_via_split_20261005/)이며, [0.10mm 위치도](docs/review_via_split_20261005/trace_widths/all_layers_0p10mm.png)는 그 변경 이전 PCB를 설명합니다.

L1~L5의 저장된 GND 푸어를 원형 띠와 면적 비교했습니다. **L1 폭 0.325mm, L2~L5 폭 0.225mm의 검사 띠에서 결손 0**이며 케이블 GND J2.1까지의 연결도 확인했습니다. 이번에는 중앙 푸어와 B.Cu를 포함한 모든 GND 영역의 연결도 검사하여 **16/16 연결 그래프 영역이 J2에 도달하며 고립 영역 0개**임을 확인했습니다. 처음 잡은 내층 약 0.25mm는 구현 목표로, 사용자 지정 제조 최소폭이 아닙니다. 검사 띠의 폭과 제조 보증폭은 구분해야 합니다. 실제 6층 재료·동박·절연층 적층은 제조업체와 확정하기 전입니다.

앞선 6층 전환에서는 외곽 GND 공간을 위해 U5의 중심을 유지하고 방향을 45°에서 225°로 변경했습니다. R4는 (25.8267,16.0024)에서 (25.750001,15.9000)mm로 약 0.128mm 옮기고 45°에서 180°로 변경했습니다. 이는 R4 재배치와 선폭·비아 변경보다 앞선 이력입니다. [6층 전환 비교 감사](docs/verification_6layer_20261005/independent_audit.json).

탑면 하단은 왼쪽부터 **NRST(J9)–SWDIO(J7)–GND(J10)–SWCLK(J8)–3V3 VTref(J11)**입니다. 사용자 요청 필수 접점은 앞의 NRST/SWDIO/SWCLK/GND 4개이고, VTref는 제시한 안에 추가한 프로그래머 타깃 전압 기준 접점입니다. Ø0.8mm·피치 1.27mm·F.Cu/F.Mask·no F.Paste는 현재 구현값입니다. 중심은 x=17.46/18.73/20.00/21.27/22.54mm, y=21.85mm입니다. 위쪽 배치도 비교했으나 기존 비아 간섭 때문에 하단을 유지했습니다. 바텀 케이블 GND J2도 유지합니다. R/D/G/C/V는 F.Fab 검토 표기로 실제 실크가 아닙니다. [패드 배치 비교](docs/verification_swd_top_20261005/placement_comparison.json).

프로젝트 룰은 일반·최소 선폭 0.15mm, 이종 넷 구리 간격 0.15mm, 구멍–구리 0.20mm, 구멍–구멍 0.25mm입니다. 최소 관통 드릴은 0.20mm이며 비아 외경과 넷별 드릴 크기는 사용자 룰로 고정했습니다. L4 3V3 분배선의 선폭 검사 하한은 0.30mm입니다. F/B GND 푸어–신호 간격은 0.15mm, 내층 푸어 간격은 0.20mm입니다. 외곽 이격은 일반 구리 0.30mm, F GND 푸어만 0.20mm입니다. [사용자 규칙 파일](kicad/ppg_pcb_v08.kicad_dru)을 PCB·프로젝트와 함께 보관해야 비아 크기, L2 배선 금지와 탑 외곽 이격 예외가 유지됩니다. PCB 중심은 40×40mm 시트의 (20,17)mm이며 보조·그리드 원점도 같습니다.

제조 검토: Ø0.50/0.20mm 비아의 공칭 환형 링은 0.15mm입니다. 유지한 전원 비아 Ø0.50/0.25mm는 0.125mm로, 한샘디지텍 안내의 1oz 이상 일반 동박 최소 환형 링 0.15mm와는 차이가 있습니다. 적용 동박에 따라 전원 비아 외경 Ø0.55mm 이상이 필요할 수 있으나 이번에는 변경하지 않았습니다. 구멍–구리 0.20mm 및 탑 GND 외곽 0.20mm도 업체 안내의 0.30mm 항목과 별도 협의 대상입니다. 따라서 DRC 0건은 현재 프로젝트 룰 통과이며 제조사 전체 조건 승인으로 보지 않습니다. [한샘디지텍 제작 사양](https://www.hsdgt.com/order/information.html), [드릴 안내](https://www.hsdgt.com/pop/pop-drill.html).

**TVS 전원선 변경은 이번 배치·배선 작업에서 아직 실행하지 않았습니다.** D6/D7/D8은 ESD351DPYR이며 각각 SWDIO/SWCLK/NRST 보호를 유지합니다. 사용자 요청 후속안은 D6→3V3, D7→5V_LED이며, 5V 선에는 적정 동작전압의 대체 부품을 적용해야 합니다. 전원 비드 FB1은 미터 1005, ESD만 1.0×0.6mm 예외를 허용한 조건을 유지합니다.

**U1 3번 LDO_EN ↔ U2 12번 PA7**을 유지합니다. 펌웨어 요구사항은 내부 풀다운, push-pull 출력, 초기 LOW입니다. GPIOA 클록 활성화 후 출력 래치에 LOW를 먼저 쓰고 GPIO를 초기화합니다. STM32 HAL 기준 GPIO_MODE_OUTPUT_PP, GPIO_PULLDOWN, GPIO_SPEED_FREQ_LOW입니다. 사용 시 HIGH로 센서를 켜고 센서를 초기화하며, 종료 시 LOW로 전환합니다. 이 저장소에는 펌웨어 소스가 없어 요구사항만 기록했습니다. 사용자 결정에 따라 외부 풀다운 저항은 추가하지 않습니다. 내부 풀다운은 펌웨어 설정 이후 적용되므로 리셋·초기화 전 OFF 상태를 하드웨어로 고정한 설계는 아닙니다. [MAXM86161 데이터시트](https://www.analog.com/media/en/technical-documentation/data-sheets/MAXM86161.pdf), [STM32C0 참조 매뉴얼](https://www.st.com/resource/en/reference_manual/dm00781702.pdf).

RS-422의 U3 XR33194/U6 XR33183, R3 120/1% 종단, R4 10k 풀업, R5–R8 22Ω 직렬저항은 유지합니다. D2/D4 SM712는 삭제된 기존 상태를 유지하며 통신선 외부 TVS는 없습니다. D1·FB1 입력 보호는 유지합니다. AMP 프로브 공급은 공칭 9V이며 기존 12V_IN/12V 넷 이름은 유지했습니다.

- 현재 원본: [PCB](kicad/ppg_pcb_v08.kicad_pcb), [회로도](kicad/ppg_pcb_v08.kicad_sch), [현재 6층 이미지](docs/review_all_ground_20261005/layers/six_layers.png), [현재 검증](docs/verification_all_ground_20261005/)
- 이전 검증 이력: [선폭·비아 변경 완료본](docs/verification_via_split_20261005/), [6층 전환 완료본](docs/verification_6layer_20261005/), [4층 SWD 완료본](docs/verification_swd_top_20261005/), [PA7 LDO_EN 변경](docs/verification_ldo_en_20261004/), [RS-422 변경](docs/RS422_update_20261001.md)
- 기존 docs/layers_png, PDF, 좌표 CSV, STEP 및 배치 이미지는 6층 변경 이전 자료입니다. docs/review_6layer_20261005는 선폭·비아 변경 전 이력이며, docs/review_via_split_20261005는 R4 이동 전 자료입니다. review_r4_move와 verification_txp_move는 각각 R4 작업 및 TXP 검사 단계의 이력입니다. 현재 전층 GND 완료본은 review_all_ground_20261005입니다.

**2026-10-05 사용자 승인에 따라 전층 GND 완료본의 거버·드릴을 생성했습니다.** [현재 거버·드릴 ZIP](manufacturing/20261005_all_ground/PPG_v0.8_6L_GND_20261005_Gerber_Drill.zip), [제조 메모](manufacturing/20261005_all_ground/README_FABRICATION.md), [출력 검증](docs/verification_all_ground_20261005/gerber_validation.json), [실제 거버 동박 미리보기](manufacturing/20261005_all_ground/review/gerber_render/copper_six_layers.png). 6개 동박·양면 마스크·양면 실크·외곽의 11개 거버와 도금71홀/비도금0홀 Excellon을 포함하며 원점·층 순서·외형·드릴 좌표를 검증했습니다. 적층·동박·기존 제조 예외 조건은 제조 메모에 기록했습니다. BOM은 갱신하지 않았으며 발주·업로드는 하지 않았습니다. [출력 승인 기록](docs/OUTPUT_APPROVAL.md). 기존 gerber/와 루트 Gerber ZIP은 LVDS 이력으로 혼용하면 안 됩니다. kicad/run_v08.sh의 기본 실행은 계속 검증 전용입니다.

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
