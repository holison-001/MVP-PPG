# RS-422 부품 배치 화면

현재 37부품(1개 탑 / 36개 바텀)의 저장된 배치 도형을 표시합니다. D2·D4 제거 상태이며 탑면 U1 위치·방향은 유지합니다.

- `rs422_top_bottom.png`: 현재 탑/바텀 배치. **배치 형상 검증 통과 · 배선 미표시**.
- `d2_d4_removed_comparison.png`: 이전 39부품 SM712 구성과 현재 37부품 비교.
- `bottom_before_after.png`: 과거 LVDS 배치와 현재 RS-422 비교. LVDS 그림은 이력 참고입니다.
- `history_sm71239/`: 이전 39부품 후보의 원본 좌표·도형·검증 결과.

각 면을 부품 쪽에서 직접 본 방향입니다. 바텀은 KiCad 보드 좌표에서 좌우 반전했으며, J7 SWDIO / J8 SWCLK / J9 NRST를 외부 인출선으로 표시했습니다.

현재 형상 판정: 조립 여유 겹침 0쌍 · 최소 외곽 간격 0.305 mm / 요구 0.30 mm. 실제 본체 겹침은 0건입니다. 조립 여유 겹침은 빨강, 구리–외곽 간격 부족은 주황으로 표시합니다.

이 그림은 부품 배치 화면이며 배선·비아를 표시하지 않습니다. 형상 통과 표시는 배치 검사만 뜻하며 PCB 배선, 전기적 연결, 제조 검증의 완료를 뜻하지 않습니다.

Matplotlib·Shapely가 설치된 Python에서 `python3 render.py`로 다시 그릴 수 있습니다. 현재 클라우드 환경에서는 `PYTHONPATH=/workspace/.amp-env/python-extra python3 render.py`를 사용합니다. 임시 후보는 `--placement`, `--geometry`, `--audit`, `--output-dir` 옵션으로 별도 출력할 수 있습니다. 입력·출력 SHA-256은 `source_manifest.json`에 기록됩니다.
