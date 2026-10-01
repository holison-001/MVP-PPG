# SleepBud PPG PCB v0.8 — RS-422 회로 반영

현재 회로도와 BOM은 **XR33194/XR33183 기반 RS-422 39개 레퍼런스**로 갱신했습니다. **PCB 반영은 대기(PENDING)**입니다. 탑면에는 PPG 센서 U1만 배치하는 조건을 유지합니다.

- [RS-422 회로도](kicad/ppg_pcb_v08.kicad_sch), [회로도 PDF](docs/ppg_pcb_v08_schematic.pdf), [미리보기](docs/rs422_schematic_preview.png)
- [통합 BOM 엑셀](bom/MVP-PPG_BOM_부품별통합_DNP제외_값표준화_v2.xlsx): 20그룹·39레퍼런스, 구매 부품 30개와 구리 패드 9개
- [변경·핀 연결·케이블 교차 연결·검증 범위](docs/RS422_update_20261001.md)
- [RS-422 탑·바텀 배치 검토 PNG](docs/placement_preview_rs422/rs422_top_bottom.png), [기존 LVDS와 바텀 비교](docs/placement_preview_rs422/bottom_before_after.png) — 배선 전·검증 미통과 후보
- [회로 검증 원자료](docs/verification_rs422_schematic/): ERC 0건, 39개 부품의 모델/넷리스트 일치
- [이전 LVDS 설계·제조·검증 이력](docs/legacy_before_rs422/)

## PCB와 제조 파일 상태

현재 `kicad/ppg_pcb_v08.kicad_pcb`는 **이전 LVDS 배선본**입니다. 현재 RS-422 회로도와 일치하지 않습니다. `gerber/`, 루트 Gerber ZIP, PCB 레이어·배치·좌표·STEP는 기존 LVDS 이력이며 RS-422 제조 파일이 아닙니다. 새로운 PCB 배치·배선·DRC·회로도 일치 검사 완료 후 함께 갱신해야 합니다. Ø13.5 mm 배치 탐색에서 조립 여유 영역의 겹침과 0.30 mm 외곽 간격 미달이 남아 PCB를 확정하지 않았습니다. [배치 검토 기록](docs/verification_rs422_schematic/placement_feasibility/)을 보관했습니다.

`run_v08.sh`는 현재 회로도와 PCB의 불일치를 검사하므로 미완성 조합에서 제조 출력을 생성하면 안 됩니다. `--rebuild`는 별도 후보 생성 기능이며 현재 PCB 반영 완료를 뜻하지 않습니다. 이 변경에서 PCB 재생성·Gerber 재출력은 수행하지 않았습니다.

## 전원과 보호

AMP의 프로브 공급은 공칭 +9 V입니다. PPG의 기존 `12V_IN`/`12V` 넷 이름은 그대로 두었으며 공급을 12 V로 바꾸지 않았습니다. AMP TX±는 PPG RX±로, PPG TX±는 AMP RX±로 극성을 유지하여 교차 연결합니다.

D2/D4 SM712 및 R5–R8 22 Ω 0402 HP를 적용하고, R3 120 Ω 종단은 수신기 직렬 저항 앞 케이블 측에 둡니다. 0402의 0.2 W 표기를 더 큰 AMP 저항과 동일한 펄스 내량으로 해석하지 않습니다. 최종 시제품에서 IEC 내성·잔류 전압·발열 검증이 필요합니다.
