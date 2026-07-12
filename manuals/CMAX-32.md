# 10. 線路圖 — 緊急安全及門安全回路（安全回路）

## 控盤

- CB2-17/CN10-5（24V）→ 控盤 BXC：CN3-2
- CB2-7（A1）→ 車廂操作盤1A RUN(CN38-6)、車廂操作盤2A RUN(CN39-6)
- 救出口 MHS
- 煞車器 GLS
- 車廂頂操作：SF1、SF2 → MOP
- 工作平台 CLK

## GOV（調速機）迴路

- CB2-8/CN1（A2/GOV）→ CN1-1、CN1-2（GOV）
- CN10-6（A3）→ 上終點 FLSU、下終點 FLSD、機坑安全開關 PIT_SW

## 門迴路（GS/HDR）

- CB2-5/CN10-12（G1/A4）→ GS1(CN15-2)、GS1(CN15-1)、GS2(CN16-2)、GS2(CN16-2)/CB2-6
- CB2-18/CN10-11（0V）
- SAR、GS、HDR（繼電器）
- SAR/a1、SAR/a2

## HDR 迴路（外門短路）

- CN15-1(R10)、CN15-10(T10) → HDR FU4(1A) → BD2（DC100V Relay）
- H1(CN16-1) → DSn ... DS2、DS1 → H2(CN16-2)

## 頂控基板/主機板插座對應表

| 頂控基板 CB2 | 主機板插座 CN10 |
|---|---|
| 18~17：...A2/A1(6/7)、G2/G1(5/6) | 7~1：0V/24V(6/12)、A4/A3(6/12) |

## 圖面說明

| 修訂 | 111.02.01 配合藍錄版修訂 |
|---|---|
| 圖名 | 安全回路 |
| 圖號 | |
| 繪圖 | LIANG |

---
*2022.02.25-0版 copyright ＠ CHIMAX corporation. all right reserved. — 31*
