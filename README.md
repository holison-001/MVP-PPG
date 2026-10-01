# SleepBud PPG PCB v0.8 — RS-422

**2026-10-02: U4/U5 MCP1703A /MC 풋프린트 불일치를 교정하고 재배선을 완료했습니다.** [최신 교정·검증 기록](docs/footprint_correction_20261001/README.md)을 기준으로 검토하세요.

- [PCB](kicad/ppg_pcb_v08.kicad_pcb), [회로도](kicad/ppg_pcb_v08.kicad_sch): ERC 0, DRC 오류 0·미연결 0·회로도 불일치 0. 무시 항목을 복원한 DRC 경고 25건은 기록에 공개했습니다.
- Ø13.5 mm, 4층, 0.8 mm. 37레퍼런스(실장 부품28개 + 구리 패드9개), 117핀, 48넷. 앞면은 PPG U1만 배치합니다.
- U3 XR33194/U6 XR33183 RS-422, 120Ω 수신 종단, 10kΩ 풀업, 22Ω 직렬저항 유지. D2/D4 통신선 TVS는 없으며 D1·FB1과 D6–D8은 유지합니다.
- F.Cu/In1.Cu GND 푸어, In2.Cu 최소0.40 mm 3V3 배선과 일부 신호, B.Cu 나머지 부품·팬아웃. PCB와 함께 [사용자 규칙 파일](kicad/ppg_pcb_v08.kicad_dru)을 보관하세요.
- [새 탑면](docs/footprint_correction_20261001/top.png), [새 바텀면](docs/footprint_correction_20261001/bottom.png), [2층](docs/footprint_correction_20261001/in1.png), [3층](docs/footprint_correction_20261001/in2.png).
- [MC 데이터시트·랜드·STEP 출처](docs/footprint_correction_20261001/footprint_sources.md), [현재 케이블 좌표](docs/footprint_correction_20261001/README.md#배치와-층). SWDIO=J7, SWCLK=J8, NRST=J9.

**기존 거버·좌표·BOM·보드 STEP·회로도 PDF·이전 렌더는 이번 교정을 반영하지 않은 이력입니다.** 이번 작업에서 새 거버나 BOM은 생성하지 않았습니다. 새 제조 출력은 [출력 승인 규칙](docs/OUTPUT_APPROVAL.md)에 따라 별도 진행합니다. 실물 전원 과도응답·통신·ESD·광학·발열 및 조립 검증이 남아 있습니다.

검증: KiCad 도구 경로를 설정하고 `./kicad/run_v08.sh --check-only`를 실행합니다. 기본 실행도 검증 전용입니다. 자동 재생성 후보는 별도 검토가 필요하며 현재 PCB를 덮어쓰지 않습니다.

AMP 프로브 공급은 공칭9V이며 기존 `12V_IN`/`12V` 넷 이름은 유지합니다. [RS-422 회로 변경 기록](docs/RS422_update_20261001.md), [ZIP 원본 가져오기 검토](docs/import_review_20261001/README.md), [교정 전 검증](docs/verification_rs422_no_bus_tvs/), [D2/D4 삭제 전 이력](docs/legacy_rs422_with_sm712/), [LVDS 이력](docs/legacy_before_rs422/).
