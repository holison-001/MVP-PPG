# 사전 점검 결과: ppg_pcb_v08

프로젝트: `C:\WORK\모두의창업\2라운드\귀장착부\2차_260914\PPG_PCB_v0.8\kicad`

| 항목 | 상태 | 내용 |
|---|---|---|
| P01 프로젝트 파일 구성 | OK | C:\WORK\모두의창업\2라운드\귀장착부\2차_260914\PPG_PCB_v0.8\kicad\ppg_pcb_v08.* |
| P02 KiCad 설치(kicad-cli) | OK | C:\Program Files\KiCad\10.0\bin\kicad-cli.exe (KiCad 10.0) |
| P03 참조번호 주석(Annotation) | OK | 부품 41개 |
| P04 모든 기호에 풋프린트 지정 | OK |  |
| P05 풋프린트 라이브러리 경로 | OK | 풋프린트 13종 |
| P06 PCB 가 회로도와 같은 부품을 가짐 | OK |  |
| P07 PCB 넷이 회로도와 같음 | OK | 다핀 넷 핀 98개 일치 |
| P08 기호 핀 번호가 풋프린트 패드에 있음 | OK |  |
| P09 보드 외곽(Edge.Cuts) | OK | 원 외곽 사용 |
| P10 이름 길이와 대소문자 | OK |  |
| P11 참조번호 형식 | OK |  |
| P12 풋프린트 특수 요소 | OK |  |
| P13 PCB 풋프린트가 라이브러리와 같음 | OK |  |
| P14 다중 유닛 심볼 | OK |  |
| P15 ERC / DRC | 건너뜀 | "ERC/DRC 실행"을 켜면 점검 |
| P16 층수·디자인 룰·넷 클래스 | 참고 | 동박 6층. 트랙 258개, 비아 65개, 존 6개는 넘어가지 않음 |
| P17 규칙 영역(키아웃) | OK |  |

# 변환 결과

- layout: `C:\WORK\모두의창업\2라운드\귀장착부\2차_260914\PPG_PCB_v0.8\kicad\PADS_out\ppg_pcb_v08_pads.asc`
- netlist: `C:\WORK\모두의창업\2라운드\귀장착부\2차_260914\PPG_PCB_v0.8\kicad\PADS_out\ppg_pcb_v08_pads_netlist.asc`
- logic: `C:\WORK\모두의창업\2라운드\귀장착부\2차_260914\PPG_PCB_v0.8\kicad\PADS_out\ppg_pcb_v08_pads_logic.txt`
- preview: `C:\WORK\모두의창업\2라운드\귀장착부\2차_260914\PPG_PCB_v0.8\kicad\PADS_out\logic_preview` (PNG 1장)

## 변환 중 메모


## Layout 검증(납품 파일만으로 핀 좌표·넷리스트 대조)

- 데칼 13, 품명 29(ECO 미등록 0), 부품 41, 넷 23, 핀 좌표 대조 150(최대 오차 0.0001 mm)
- 넷리스트: 부품 41, 넷 23 (Layout 과 같음)
- 불일치 없음

## Logic 검증

- 방식: KiCad 회로도 모양, 시트 크기 A2
- 시트 1, 부품 Logic 41(게이트 41) / Layout 41, 선 106, 접점 8, 오프페이지·라벨 90
- 넷 Logic 23 / Layout 23, 핀 Logic 98 / Layout 98
- 불일치 없음
