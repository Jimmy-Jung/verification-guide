---

excalidraw-plugin: parsed
tags: [excalidraw]

---
Open this file in Excalidraw view using the MORE OPTIONS menu.

## Visual Brief

- 핵심 주장: 같은 입력을 두 구현이 처리해 정규화 결과를 비교하고, 차이는 일치·승인 예외·미해결로 나뉘며 미해결은 고친 뒤 같은 입력으로 다시 돌린다.
- 시작과 끝: 공용 입력 하나에서 판정까지
- 주 흐름: 왼쪽에서 오른쪽, 결함은 아래 파선으로 되돌아감
- 상태 변화: 입력 → 구현별 결과 → 정규화 결과 → 판정
- 등장 주체: 구현 A · 구현 B · 비교
- 상황 Caption: 차등 테스트

## Text Elements

공용 입력
(같은 파일) ^vg-03-differential-text-002
구현 A ^vg-03-differential-text-003
파싱 ^vg-03-differential-text-005
정규화 결과 ^vg-03-differential-text-007
구현 B ^vg-03-differential-text-011
파싱 ^vg-03-differential-text-013
정규화 결과 ^vg-03-differential-text-015
정규화 결과: 비교하기 쉽게 같은 형식(JSON)으로 바꾼 결과 ^vg-03-differential-text-019
비교 ^vg-03-differential-text-021
일치 ^vg-03-differential-text-023
승인 예외
이유를 기록 ^vg-03-differential-text-026
미해결
→ 결함 수정 ^vg-03-differential-text-029
고친 뒤 같은 입력으로 다시 실행 ^vg-03-differential-text-032

%%
## Drawing
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
  "elements": [
    {
      "type": "rectangle",
      "version": 1,
      "versionNonce": 700001,
      "isDeleted": false,
      "id": "vg-03-differential-rectangle-001",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "#ffffff",
      "seed": 800001,
      "groupIds": [
        "nodeinst:vg-03-differential:in"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 40,
      "y": 230,
      "width": 170,
      "height": 90
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700002,
      "isDeleted": false,
      "id": "vg-03-differential-text-002",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800002,
      "groupIds": [
        "nodeinst:vg-03-differential:in"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 85.25,
      "y": 256.25,
      "width": 79.5,
      "height": 37.5,
      "text": "공용 입력\n(같은 파일)",
      "fontSize": 15,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "공용 입력\n(같은 파일)",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 15
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700003,
      "isDeleted": false,
      "id": "vg-03-differential-text-003",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800003,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 260,
      "y": 40,
      "width": 47.84,
      "height": 20.0,
      "text": "구현 A",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "구현 A",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 16
    },
    {
      "type": "rectangle",
      "version": 1,
      "versionNonce": 700004,
      "isDeleted": false,
      "id": "vg-03-differential-rectangle-004",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "#ffffff",
      "seed": 800004,
      "groupIds": [
        "nodeinst:vg-03-differential:p0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 260,
      "y": 70,
      "width": 200,
      "height": 80
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700005,
      "isDeleted": false,
      "id": "vg-03-differential-text-005",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800005,
      "groupIds": [
        "nodeinst:vg-03-differential:p0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 345.0,
      "y": 100.625,
      "width": 30.0,
      "height": 18.75,
      "text": "파싱",
      "fontSize": 15,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "파싱",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 15
    },
    {
      "type": "rectangle",
      "version": 1,
      "versionNonce": 700006,
      "isDeleted": false,
      "id": "vg-03-differential-rectangle-006",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "#ffffff",
      "seed": 800006,
      "groupIds": [
        "nodeinst:vg-03-differential:n0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 510,
      "y": 70,
      "width": 200,
      "height": 80
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700007,
      "isDeleted": false,
      "id": "vg-03-differential-text-007",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800007,
      "groupIds": [
        "nodeinst:vg-03-differential:n0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 569.95,
      "y": 100.625,
      "width": 80.1,
      "height": 18.75,
      "text": "정규화 결과",
      "fontSize": 15,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "정규화 결과",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 15
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700008,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-008",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800008,
      "groupIds": [
        "connector:vg-03-differential:pn0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 460,
      "y": 110,
      "points": [
        [
          0,
          0
        ],
        [
          50,
          0
        ]
      ],
      "width": 50,
      "height": 0,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700009,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-009",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800009,
      "groupIds": [
        "connector:vg-03-differential:in0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 210,
      "y": 275,
      "points": [
        [
          0,
          0
        ],
        [
          25,
          0
        ],
        [
          25,
          -165
        ],
        [
          50,
          -165
        ]
      ],
      "width": 50,
      "height": 165,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700010,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-010",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800010,
      "groupIds": [
        "connector:vg-03-differential:nc0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 710,
      "y": 110,
      "points": [
        [
          0,
          0
        ],
        [
          35,
          0
        ],
        [
          35,
          145
        ],
        [
          70,
          145
        ]
      ],
      "width": 70,
      "height": 145,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700011,
      "isDeleted": false,
      "id": "vg-03-differential-text-011",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800011,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 260,
      "y": 370,
      "width": 47.84,
      "height": 20.0,
      "text": "구현 B",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "구현 B",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 16
    },
    {
      "type": "rectangle",
      "version": 1,
      "versionNonce": 700012,
      "isDeleted": false,
      "id": "vg-03-differential-rectangle-012",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "#ffffff",
      "seed": 800012,
      "groupIds": [
        "nodeinst:vg-03-differential:p1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 260,
      "y": 400,
      "width": 200,
      "height": 80
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700013,
      "isDeleted": false,
      "id": "vg-03-differential-text-013",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800013,
      "groupIds": [
        "nodeinst:vg-03-differential:p1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 345.0,
      "y": 430.625,
      "width": 30.0,
      "height": 18.75,
      "text": "파싱",
      "fontSize": 15,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "파싱",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 15
    },
    {
      "type": "rectangle",
      "version": 1,
      "versionNonce": 700014,
      "isDeleted": false,
      "id": "vg-03-differential-rectangle-014",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "#ffffff",
      "seed": 800014,
      "groupIds": [
        "nodeinst:vg-03-differential:n1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 510,
      "y": 400,
      "width": 200,
      "height": 80
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700015,
      "isDeleted": false,
      "id": "vg-03-differential-text-015",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800015,
      "groupIds": [
        "nodeinst:vg-03-differential:n1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 569.95,
      "y": 430.625,
      "width": 80.1,
      "height": 18.75,
      "text": "정규화 결과",
      "fontSize": 15,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "정규화 결과",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 15
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700016,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-016",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800016,
      "groupIds": [
        "connector:vg-03-differential:pn1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 460,
      "y": 440,
      "points": [
        [
          0,
          0
        ],
        [
          50,
          0
        ]
      ],
      "width": 50,
      "height": 0,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700017,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-017",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800017,
      "groupIds": [
        "connector:vg-03-differential:in1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 210,
      "y": 275,
      "points": [
        [
          0,
          0
        ],
        [
          25,
          0
        ],
        [
          25,
          165
        ],
        [
          50,
          165
        ]
      ],
      "width": 50,
      "height": 165,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700018,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-018",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800018,
      "groupIds": [
        "connector:vg-03-differential:nc1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 710,
      "y": 440,
      "points": [
        [
          0,
          0
        ],
        [
          35,
          0
        ],
        [
          35,
          -145
        ],
        [
          70,
          -145
        ]
      ],
      "width": 70,
      "height": 145,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700019,
      "isDeleted": false,
      "id": "vg-03-differential-text-019",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#555555",
      "backgroundColor": "transparent",
      "seed": 800019,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 260,
      "y": 500,
      "width": 356.46000000000004,
      "height": 16.25,
      "text": "정규화 결과: 비교하기 쉽게 같은 형식(JSON)으로 바꾼 결과",
      "fontSize": 13,
      "fontFamily": 2,
      "textAlign": "left",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "정규화 결과: 비교하기 쉽게 같은 형식(JSON)으로 바꾼 결과",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 13
    },
    {
      "type": "rectangle",
      "version": 1,
      "versionNonce": 700020,
      "isDeleted": false,
      "id": "vg-03-differential-rectangle-020",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#355579",
      "backgroundColor": "#e6ecf3",
      "seed": 800020,
      "groupIds": [
        "nodeinst:vg-03-differential:cmp"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 780,
      "y": 230,
      "width": 160,
      "height": 90
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700021,
      "isDeleted": false,
      "id": "vg-03-differential-text-021",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800021,
      "groupIds": [
        "nodeinst:vg-03-differential:cmp"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 844.0,
      "y": 265.0,
      "width": 32.0,
      "height": 20.0,
      "text": "비교",
      "fontSize": 16,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "비교",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 16
    },
    {
      "type": "rectangle",
      "version": 1,
      "versionNonce": 700022,
      "isDeleted": false,
      "id": "vg-03-differential-rectangle-022",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "#ffffff",
      "seed": 800022,
      "groupIds": [
        "nodeinst:vg-03-differential:r0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 1020,
      "y": 90,
      "width": 190,
      "height": 70
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700023,
      "isDeleted": false,
      "id": "vg-03-differential-text-023",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800023,
      "groupIds": [
        "nodeinst:vg-03-differential:r0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 1100.0,
      "y": 115.625,
      "width": 30.0,
      "height": 18.75,
      "text": "일치",
      "fontSize": 15,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "일치",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 15
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700024,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-024",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800024,
      "groupIds": [
        "connector:vg-03-differential:cr0"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 940,
      "y": 275,
      "points": [
        [
          0,
          0
        ],
        [
          40,
          0
        ],
        [
          40,
          -150
        ],
        [
          80,
          -150
        ]
      ],
      "width": 80,
      "height": 150,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "rectangle",
      "version": 1,
      "versionNonce": 700025,
      "isDeleted": false,
      "id": "vg-03-differential-rectangle-025",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "#ffffff",
      "seed": 800025,
      "groupIds": [
        "nodeinst:vg-03-differential:r1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 1020,
      "y": 240,
      "width": 190,
      "height": 70
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700026,
      "isDeleted": false,
      "id": "vg-03-differential-text-026",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800026,
      "groupIds": [
        "nodeinst:vg-03-differential:r1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 1074.95,
      "y": 256.25,
      "width": 80.1,
      "height": 37.5,
      "text": "승인 예외\n이유를 기록",
      "fontSize": 15,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "승인 예외\n이유를 기록",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 15
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700027,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-027",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800027,
      "groupIds": [
        "connector:vg-03-differential:cr1"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 940,
      "y": 275,
      "points": [
        [
          0,
          0
        ],
        [
          40,
          0
        ],
        [
          40,
          0
        ],
        [
          80,
          0
        ]
      ],
      "width": 80,
      "height": 0,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "rectangle",
      "version": 1,
      "versionNonce": 700028,
      "isDeleted": false,
      "id": "vg-03-differential-rectangle-028",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "#efefef",
      "seed": 800028,
      "groupIds": [
        "nodeinst:vg-03-differential:r2"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 1020,
      "y": 390,
      "width": 190,
      "height": 70
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700029,
      "isDeleted": false,
      "id": "vg-03-differential-text-029",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#1b1b1b",
      "backgroundColor": "transparent",
      "seed": 800029,
      "groupIds": [
        "nodeinst:vg-03-differential:r2"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 1076.3,
      "y": 406.25,
      "width": 77.4,
      "height": 37.5,
      "text": "미해결\n→ 결함 수정",
      "fontSize": 15,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "미해결\n→ 결함 수정",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 15
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700030,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-030",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800030,
      "groupIds": [
        "connector:vg-03-differential:cr2"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 940,
      "y": 275,
      "points": [
        [
          0,
          0
        ],
        [
          40,
          0
        ],
        [
          40,
          150
        ],
        [
          80,
          150
        ]
      ],
      "width": 80,
      "height": 150,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "arrow",
      "version": 1,
      "versionNonce": 700031,
      "isDeleted": false,
      "id": "vg-03-differential-arrow-031",
      "fillStyle": "solid",
      "strokeWidth": 1.2,
      "strokeStyle": "dashed",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#5f5f5f",
      "backgroundColor": "transparent",
      "seed": 800031,
      "groupIds": [
        "connector:vg-03-differential:loop"
      ],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 1115,
      "y": 460,
      "points": [
        [
          0,
          0
        ],
        [
          0,
          100
        ],
        [
          -990,
          100
        ],
        [
          -990,
          -140
        ]
      ],
      "width": 990,
      "height": 240,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "type": "text",
      "version": 1,
      "versionNonce": 700032,
      "isDeleted": false,
      "id": "vg-03-differential-text-032",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "strokeColor": "#555555",
      "backgroundColor": "transparent",
      "seed": 800032,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "boundElements": [],
      "updated": 1788134400000,
      "link": null,
      "locked": false,
      "x": 524.45,
      "y": 568,
      "width": 191.1,
      "height": 16.25,
      "text": "고친 뒤 같은 입력으로 다시 실행",
      "fontSize": 13,
      "fontFamily": 2,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "고친 뒤 같은 입력으로 다시 실행",
      "autoResize": true,
      "lineHeight": 1.25,
      "baseline": 13
    }
  ],
  "appState": {
    "theme": "light",
    "viewBackgroundColor": "transparent",
    "currentItemStrokeColor": "#000000",
    "currentItemFontFamily": 2,
    "gridSize": 10
  },
  "files": {}
}
```
%%
