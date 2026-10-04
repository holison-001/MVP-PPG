# RS-422 PCB 레이어 검토 PNG

현재 PCB에서 직접 출력한 검토 이미지입니다. 탑면과 내층은 위에서 본 방향, 바텀면은 부품 쪽에서 본 방향으로 좌우 반전했습니다. 배선 확인을 위해 구리와 보드 외곽만 표시하며, 부품 레퍼런스는 [별도 배치도](../placement_preview_rs422/rs422_top_bottom.png)에서 확인합니다.

- [01_F_Cu_TOP.png](01_F_Cu_TOP.png): TOP: GND pour and local traces, viewed from top
- [02_In1_Cu_GND.png](02_In1_Cu_GND.png): Layer 2: selected routing and GND pour, viewed from top
- [03_In2_Cu_3V3.png](03_In2_Cu_3V3.png): Layer 3: broad 3V3 traces and routing, viewed from top
- [04_B_Cu_BOTTOM.png](04_B_Cu_BOTTOM.png): BOTTOM copper, viewed from bottom, mirrored

[도면 시트 내 PCB 위치](../pcb_sheet.png)도 별도로 출력했습니다.

거버·BOM을 생성하지 않는 검토 출력입니다. 원본 PCB와 이미지 해시는 `source_manifest.json`에 기록했습니다.
