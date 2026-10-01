# RS-422 배치 화면

- [탑·바텀 배치 PNG](rs422_top_bottom.png): U1만 탑면, RS-422 후보 38레퍼런스 바텀.
- [바텀 변경 전후 PNG](bottom_before_after.png): 기존 LVDS PCB 배치와 RS-422 후보 비교.

각 면을 부품 쪽에서 직접 본 방향입니다. 바텀은 KiCad 보드 좌표를 전체 좌우 반전했고, 탑은 위에서 내려다본 방향입니다. 배선·비아를 숨긴 부품 배치도입니다. 기존 PCB나 후보 좌표를 변경하지 않았습니다.

RS-422 쪽은 저장된 `packing_strict_best.json` 좌표와 `packing_geometry_physical.json` 실제 도형을 사용한 미검증 후보입니다. 빨강은 부품 조립 여유(코트야드)의 겹침, 주황은 0.30 mm 구리–외곽 간격 부족입니다. 실제 부품 본체의 겹침은 없습니다. 기존 LVDS 쪽은 마지막 검증 PCB에서 추출한 패드·코트야드 도형을 사용했습니다.

재생성: `render.py` (Python + matplotlib + shapely, Noto Sans CJK 폰트). 입력과 출력 해시는 `source_manifest.json`에 있습니다. PNG는 제조용 확정 배치가 아닙니다.
