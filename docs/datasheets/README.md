# 부품 데이터시트

2026-10-01 수집·확인. 현재 설계에서 모델명이 정해진 실장 부품 15개에 대응하는 제조사 원문 PDF 7종을 보관합니다. 같은 제품군 문서를 사용하는 부품은 하나의 PDF로 연결했습니다. 다운로드한 PDF는 편집하거나 다시 출력하지 않았습니다.

| 참조번호 | 설계 부품 | 보관 PDF | 문서 버전 / 쪽수 | 실제 입수처 |
|---|---|---|---|---|
| U1 | MAXM86161EFD+ | [MAXM86161](MAXM86161.pdf) | 19-100523 Rev 1, 2023-04 / 65쪽 | [Datasheet4U 보관본](https://datasheet4u.com/pdf/1569506/MAXM86161.pdf) |
| U2 | STM32C011F6U6 | [STM32C011x4/x6](STM32C011x4_x6.pdf) | DS13866 Rev 3, 2022-12 / 94쪽 | [Future Electronics 보관본](https://www1.futureelectronics.com/doc/STMicroelectronics/STM32C011D6Y6TR.pdf) |
| U3, U6 | SN65LVDS1DBVR, SN65LVDT2DBVR | [LVDS 송·수신기](SN65LVDS1_SN65LVDT2.pdf) | SLLS373M, 2024-03 / 44쪽 | [TI](https://www.ti.com/lit/ds/symlink/sn65lvds1.pdf) |
| U4, U5 | MCP1703A-5002E/MC, MCP1703A-3302E/MC | [MCP1703A](MCP1703A.pdf) | DS20005122C, 2023-02 / 38쪽 | [Microchip](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP1703-Data-Sheet-DS20005122.pdf) |
| D1 | SPHV15-01ETG | [SPHV](SPHV.pdf) | GD. 04/15/21 / 6쪽 | [IC-Components 보관본](https://www.ic-components.nl/files/80/SPHV12-01ETG.pdf) |
| D2–D8 | ESD351DPYR | [ESD351](ESD351.pdf) | SLVSEO3, 2018-07 / 20쪽 | [TI](https://www.ti.com/lit/ds/symlink/esd351.pdf) |
| FB1 | BLM15PX601SN1D | [BLM15_SN 제품군 사양서](BLM15PX601SN1D.pdf) | JENF243A-0018AJ-01 / 11쪽 | [Farnell 보관본](https://www.farnell.com/datasheets/2575526.pdf) |

## 보관본의 범위와 최신 제조사 문서

일부 제조사 서버에서 원문 다운로드가 되지 않아 유통사 또는 공개 문서 보관 사이트의 제조사 작성 PDF를 사용했습니다. 입수처를 제조사와 구분해 표시했으며, 보관본이 항상 최신판인 것은 아닙니다.

- **U1:** 보관본은 [ADI 게시 문서](https://www.analog.com/media/en/technical-documentation/data-sheets/maxm86161.pdf)와 제목·Rev 1·65쪽 구성이 일치합니다. 제조사 서버 파일과 바이트 단위로 비교하지는 못했습니다. `MAXM86161A`가 아닌 설계의 `MAXM86161EFD+`를 다루며, 주문 정보는 PDF 64쪽에 있습니다.
- **U2:** 보관본은 Rev 3입니다. [ST 현재 게시 문서](https://www.st.com/resource/en/datasheet/stm32c011f6.pdf)는 Rev 5, 2026-02, 97쪽으로 확인됐으므로 설계 확정 시 개정 사항을 확인해야 합니다. 입수 URL에 D6 모델이 들어가지만 PDF는 F6를 포함한 공통 제품군 문서이며, UFQFPN20과 `STM32C011F6U6`의 주문 코드 조합은 1·91쪽에서 확인했습니다.
- **D1:** 보관본은 2021년판이며 [Littelfuse 게시 문서](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_array_sphv_datasheet.pdf?assetguid=4bdc7e09-5dd4-4010-a86a-0008bb6e228c)의 확인된 2022년판보다 이전입니다. 5쪽에 정확한 품번이 있고, 6쪽의 권장 패드는 0.325 × 0.650 mm, 중심 간격 0.650 mm로 현재 PCB와 일치합니다. IC-Components는 제3자 입수처로 표시하며 공식 유통사라고 단정하지 않습니다.
- **FB1:** 보관본은 AJ-01입니다. [Murata 제품 페이지](https://www.murata.com/en-us/products/productdetail?partno=BLM15PX601SN1%23)와 [제조사 사양서 경로](https://www.murata.com/products/productdata/8796740059166/ENFA0018.pdf)를 함께 남겼습니다. 제조사 게시본은 더 새로운 AP-01로 확인됐지만 다운로드하지 못했습니다. 정확한 품번과 정격 행은 보관 PDF 3쪽에서 확인했습니다.

U3/U6는 공통 문서 33쪽의 각 DBVR 주문 항목, U4/U5는 35쪽의 전압 및 MC 패키지 주문 코드, D2–D8은 13쪽의 ESD351DPYR 주문 항목으로 대응을 확인했습니다. TI PDF에는 본문 개정일 이후의 패키징 부록이 포함될 수 있습니다.

## 아직 품번이 정해지지 않은 부품

C1, C4, C5, C6, C7, C11, C12, C13, C14, R1, R2는 현재 설계에 값·패키지 조건만 있고 제조사 품번이 없습니다. 임의의 부품 데이터시트를 연결하지 않았으며, 실제 구매 품번이 정해지면 추가합니다. J1–J9는 PCB의 동박 패드이므로 별도의 상용 부품 데이터시트가 없습니다.

파일별 출처, 적용 참조번호, 확인 내용, 쪽수, 파일 크기와 SHA-256은 [sources.json](sources.json)에 기록했습니다. 모든 PDF가 열리고 적용 제품이 포함되는지 확인했습니다. 문서 저작권과 고지는 각 제조사 원문을 따릅니다.
