# U4/U5 MC 패키지 및 U2 로컬 풋프린트 출처

검토일: 2026-10-01. 이 문서는 풋프린트의 출처와 기하학적 근거를 기록합니다. 최종 PCB의 배치·배선·제조 출력 검증 결과를 대신하지 않습니다.

## U4/U5 — Microchip MCP1703A /MC

적용 부품: `MCP1703A-5002E/MC`, `MCP1703A-3302E/MC`.

- 로컬 풋프린트: [MCP1703A_MC_DFN8_3x2mm_P0.5mm.kicad_mod](../../kicad/SleepBud.pretty/MCP1703A_MC_DFN8_3x2mm_P0.5mm.kicad_mod)
- 제조사 원본: [MCP1703A.pdf](../../datasheet/pdf/MCP1703A.pdf), **DS20005122C, Revision C, February 2023**, 38페이지, 2,296,306바이트. 원본 바이트를 보존했으며 편집·재출력하지 않았습니다.
- 공식 출처: [Microchip 데이터시트](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP1703-Data-Sheet-DS20005122.pdf), [제품 페이지](https://www.microchip.com/en-us/product/mcp1703a).
- PDF SHA-256: `6fdfc2f20167c7292c92c9c4c8003fd4d8615e0f2f90e224e1e10dce6ed65b5f`
- 근거: p12 Table 3-1 핀 기능, **p29–30 C04-123 Rev E 패키지 도면**, **p31 C04-2123 Rev E 권장 랜드 패턴**, p35 주문 코드. 제조사 도면을 직접 확인했습니다.

풋프린트는 제조사 도면을 시계 방향으로 90° 회전한 방향입니다. 아래 좌표는 KiCad 앞면 로컬 좌표이며 X는 오른쪽, Y는 아래쪽입니다.

| 항목 | 적용값 및 도면 근거 |
|---|---|
| 본체 | X 3.00 × Y 2.00 mm, 도면의 E/D BSC 치수 |
| 접점 패드 | 타원 0.85 × 0.30 mm, p31 Y1/X1 최대 치수 |
| 마주 보는 패드열 중심 간격 | 3.00 mm, p31 C 공칭값 |
| 같은 열의 접점 피치 | 0.50 mm, p31 E BSC |
| 중앙 EP 구리 | X 1.75 × Y 1.55 mm, 회전한 p31 Y2/X2 최대 치수 |
| 핀 1 | (-1.50, -0.75) mm, 왼쪽 위; 왼쪽은 위에서 1–4, 오른쪽은 아래에서 5–8 |
| 전기적 대응 | 1=VOUT, 4=GND, 8=VIN, 9=EP/GND; 나머지 NC |
| 최소 구리 간격 | EP–접점: `1.50 - 0.85/2 - 1.75/2 = 0.20 mm`; 인접 접점: `0.50 - 0.30 = 0.20 mm` |
| 코트야드 | X ±2.20, Y ±1.25 mm; 접점 구리 끝에서 0.275 mm, 본체 Y 끝에서 0.25 mm 여유 |

기존 `DFN-8-1EP_2x3mm_P0.5mm_EP0.61x2.2mm`는 KiCad의 **Linear-DDB** 도면 기반입니다. 그 패드열 간격 1.88 mm와 EP 0.61 × 2.20 mm는 Microchip MC와 다르므로 이 부품에 사용하지 않습니다.

### 마스크와 페이스트의 프로젝트 설계 선택

제조사 p31은 구리 랜드 패턴을 제시합니다. 다음 마스크 확장과 페이스트 분할은 별도의 프로젝트 선택이며 제조사 지정 스텐실로 표현하지 않습니다.

- NSMD 마스크 확장: 각 구리 패드에서 0.025 mm. 인접 접점 및 EP 사이 마스크 개구 간 이론적 최소 간격은 0.15 mm입니다.
- EP 전체에는 페이스트를 지정하지 않고, **0.70 × 0.60 mm 창 4개**를 (±0.45, ±0.40) mm에 배치했습니다.
- 총 페이스트 면적 `4 × 0.70 × 0.60 = 1.68 mm²`; EP 면적 `1.75 × 1.55 = 2.7125 mm²`; 면적 비율 **61.94%**입니다.
- 창 사이 간격은 X/Y 모두 0.20 mm, EP 구리 경계 안쪽 여유는 0.075 mm입니다. 이 분할은 스텐실 두께나 조립 공정의 적합성까지 검증한 결과는 아닙니다.
- p31의 열 비아는 선택 항목입니다. 풋프린트에는 열 비아를 강제하지 않습니다. EP 9번은 GND와 같은 전위로 연결해야 합니다.

### MC STEP 참조 모델

[MCP1703A_MC_datasheet_reference.step](../../kicad/SleepBud.3dshapes/MCP1703A_MC_datasheet_reference.step)는 **프로젝트에서 데이터시트에 따라 만든 독립 참조 모델**이며 Microchip 제공 STEP이 아닙니다. 프로젝트 커밋 `2d90e067ea9b30de5ff0745b3141243147a49600`의 `docs/step/MCP1703A_MC_datasheet_reference.step`를 그대로 복사했습니다.

- 본체 외형은 공칭 **3.00 × 2.00 × 0.90 mm**이며, 제조사 최대 높이는 **1.00 mm**입니다. 0.90 mm 모델을 최대 높이 검증에 사용하지 않습니다.
- 좌표는 X ±1.50, Y ±1.00, Z 0–0.90 mm입니다. Z=0은 단자 착좌면입니다. 3D의 Y는 위쪽이므로 핀 1은 X 음수/Y 양수이고, KiCad 풋프린트의 왼쪽 위 핀 1과 대응합니다.
- 접점은 직사각형으로 단순화했습니다. EP는 명시된 범위의 중간값 1.625 × 1.425 mm이며 제조사 공칭값으로 주장하지 않습니다. 타이 바·모따기·핀 1 표시는 모델링하지 않았습니다.
- FreeCAD에서 유효한 솔리드 10개와 전체 외형을 확인했습니다. SHA-256: `727919d2686ed0e583724ec33345a882a818a7affaae37d8421f00dc2e296f25`

## U2 — KiCad UFQFPN20 로컬 실크 도형 생략 변형

로컬 파일: [ST_UFQFPN-20_3x3mm_P0.5mm_NoSilk.kicad_mod](../../kicad/SleepBud.pretty/ST_UFQFPN-20_3x3mm_P0.5mm_NoSilk.kicad_mod).

원본은 KiCad 10.0 설치 라이브러리의 `Package_DFN_QFN:ST_UFQFPN-20_3x3mm_P0.5mm`입니다. 설치 원본 파일의 SHA-256은 `1f5f3c7dc9b86acee46d91907a13140ce9f2e047811ab518eafe0f1ac967264a`입니다. 원본의 도면 링크는 [ST STM8S003F3 데이터시트](https://www.st.com/resource/en/datasheet/stm8s003f3.pdf)이며, 3 × 3 mm, 0.50 mm 피치 UFQFPN20 패키지입니다.

변형은 라이브러리 이름·설명을 바꾸고 실크 **도형 7개**를 제거했습니다. 20개 구리 패드와 Fab·코트야드·3D 모델 노드는 원본과 동일하며, 독립 검사에서 확인했습니다. 참조 텍스트 등 다른 속성은 유지하므로 `NoSilk`라는 이름을 모든 실크 속성이 삭제되었다는 의미로 해석하지 않습니다. 원본 3D 파일 경로를 유지했다는 사실만으로 해당 STEP 파일의 존재나 모델 정확성이 보장되지는 않습니다.

### KiCad 출처와 라이선스

출처/저작자 표기: **KiCad library community contributors**. 설치된 이 풋프린트에는 별도의 개인 저작자 이름이 들어 있지 않으므로 개인 이름을 추정하지 않았습니다. 원본 라이브러리는 [KiCad 공식 footprints 저장소](https://gitlab.com/kicad/libraries/kicad-footprints)에서 관리합니다.

KiCad 풋프린트 라이브러리는 **CC BY-SA 4.0 및 전자 설계 사용에 대한 KiCad 예외**를 따릅니다. 예외는 라이브러리를 사용한 설계 및 생성 파일에 적용되며, 라이브러리 모음을 재배포하는 경우의 조건과 구분됩니다. 이 프로젝트의 U2 변형은 위 출처와 변경 내용을 함께 기록합니다. [공식 라이선스 설명](https://www.kicad.org/libraries/license/)과 원문 보관본 [KiCad-footprints-LICENSE.md](KiCad-footprints-LICENSE.md)를 참고하십시오. 보관본은 2026-10-01에 [공식 저장소 LICENSE.md](https://gitlab.com/kicad/libraries/kicad-footprints/-/raw/master/LICENSE.md)에서 받았습니다.

Microchip PDF와 독립 MC STEP에 KiCad 라이브러리 라이선스를 확대 적용한 것은 아닙니다. 각 자료의 출처와 저작권은 별도로 유지합니다.
