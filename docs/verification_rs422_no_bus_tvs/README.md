# 현재 RS-422 PCB 검증

회로도는37레퍼런스·117핀·48넷이며 ERC 오류·경고0입니다. 이전39 회로에서 D2/D4의6핀만 제거했고 나머지 부품 값·전기 연결·회로도 UUID는 유지했습니다. 이번 작업은 PCB의 배선층과 시트 위치 변경입니다.

현재 PCB는 DRC 오류0·미연결0·회로도 불일치0이며 독립 검사도 통과했습니다. `drc_final.json`, `netcheck_final.json`, `independent_final_audit.json`이 현재 결과입니다. `check_only.log`는 거버·BOM 출력을 하지 않는 기본 검증 실행 기록입니다.

1층 배선41개 구간·42.103 mm를2층으로 옮겼고 SDA 연결선1개를 추가했습니다. 1층 길이는60.902→18.799 mm, GND 푸어는86.571→102.636 mm²입니다. 2층은 신호와 GND 푸어88.032 mm²를 함께 사용합니다. 기존59개 비아·부품 상대 위치·값·패드 넷·트랙 폭과3층0.40 mm 3V3는 유지했습니다. `in1_routing_changes.json`과 `in1_ground_connectivity.json`을 참조합니다.

PCB 중심은 40×40 mm 시트의(20,17) mm이며 보조·그리드 원점도 같은 위치입니다. `sheet_placement.json`에 이동을 기록했습니다. `placement/`와 독립 검사 좌표는 저장 보드에서 PCB 중심을 빼서 환산한 상대 좌표입니다. [도면 시트 화면](../pcb_sheet.png).

탑면 U1만 실장, 바텀36개 배치를 유지합니다. 부품 본체/조립 여유 겹침0, 패드·트랙·비아 외곽 최소0.302168 mm, 드릴–SMD 구리 최소0.026574 mm입니다. 1층 GND 외곽 이격0.20 mm와 신호 간격0.15 mm는 `kicad/ppg_pcb_v08.kicad_dru`를 포함해 검증했습니다. 비아는 모두 양면 텐팅입니다.

남은 경고5건은 실크 외곽4건과 U2 라이브러리 도형 불일치1건입니다. VREF 배선과 기존 U3/C6 디커플링 검토 사항은 유지합니다.

현재 PCB SHA256: `a127537955e5888ac5311f0a84a54265dfcddba2ac4c5e0a987e3f0d69d3c238`. `output_approval_status.json`의 기존 거버·BOM23개 파일은 승인 전까지 동결합니다. 현재 검증 근거의 해시는 `final_source_manifest.json`에 있습니다.

이전 층 변경 기록인 `in2_3V3_routing.json`, `signal_layer_changes.json`, `top_ground_changes.json`, `top_edge_changes.json`은 이력입니다. 이번 변경 직전 파일은 `../legacy_before_in1_routing/`에 보관했습니다. [전체 층 구성과 변경](../PCB_layers_20261001.md).
