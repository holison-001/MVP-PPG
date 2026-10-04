# 제조·BOM 출력 승인

사용자 요청(2026-10-01)에 따라 **거버와 BOM 생성·갱신은 명시적 승인 후 진행**합니다. PCB·회로도 편집, ERC/DRC·연결 검증, 배치·레이어 검토 이미지는 계속 진행할 수 있습니다.

현재 bom/의37부품 엑셀은 이 지시 전에 생성한 검토본입니다. 기존 거버는 LVDS 이력입니다. 새 RS-422 제조용 거버는 아직 만들지 않았습니다.

`kicad/run_v08.sh`의 기본 실행과 `--check-only`는 검증만 수행합니다. 제조·BOM 출력에는 `--publish-approved-outputs` 옵션이 필요하며, 이 옵션은 사용자의 명시적 승인 후에만 사용합니다. 옵션 자체가 승인을 대신하지 않습니다. 승인 대기 시점의 파일 해시는 `verification_rs422_no_bus_tvs/output_approval_status.json`에 기록했습니다.

`kicad/export_review_v08.py`는 PCB 검토용 레이어 PNG/SVG/PDF만 출력하며 거버·드릴·BOM을 생성하지 않습니다.
