# MVP-PPG 나머지 층 PNG

현재 검증된 PCB에서 직접 출력한 1800 × 1800 PNG입니다. 모두 위에서 내려다본 방향이며 미러링하지 않았습니다.

- `01_F_Cu_TOP.png`: 탑 동박·PPG U1 외형·보드 외곽
- `02_In1_Cu_GND.png`: 내층 1 GND 동박 채움·비아·보드 외곽
- `03_In2_Cu_3V3.png`: 내층 2 3.3V 동박 채움·비아·보드 외곽

KiCad SVG 출력(`--fit-page-to-board --exclude-drawing-sheet --mode-single --drill-shape-opt 2`)을 Inkscape로 PNG 변환했습니다. 구멍은 실제 드릴 크기이며 PCB 자체는 수정하지 않았습니다. 바텀면 부품 배치는 `../placement_back.png`에 있습니다.
