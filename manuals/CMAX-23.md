# 10. 線路圖 — 主控制板及系統架構（藍綠版適用）

> 本頁為系統架構方塊圖，顯示 CMX8.1 V.2.1(藍)版電梯主控制板與周邊各模組間的連接關係。以下摘錄圖面標示內容。

## 主控制板端子區塊

- CMX8.1 V.2.1(藍)版 電梯主控制板
- AC220 CN13 / T22・R22
- PW CN7 / 24V CN8 / MDS CN18
- AC110 CN15 / T10・R10 / AC11・AC12・AC21・AC22
- CN26 TEL
- CN14（B+B-区）：ES、UPS、CB1、B+B-、BKSW、對講機(CN23,24)
- CN27：+24、A1、A2、A3、A4、G1、G2
- CN10：H（Hoistway 井道）
- PE CN28（主板接地端）
- LINK CN21 / LAN CN20 / LAN CN19 / PG CN22 / INV CN25 / GOV CN1,CN2 / HDR CN16
- CB3、CB2、CN11、CN12、CN3(BXC)

## 周邊連接模組

| 模組 | 連接關係 |
|---|---|
| POWER & TRANSFORMER | 連接主板 AC220/AC110 輸入 |
| 連控器 | 經 LINK 連接主板 |
| 乘場操作面板（點矩陣顯示板 / LAN 傳輸控制板） | 經 LAN CN20 連接主板 |
| 調速機 | 經 GOV CN1,CN2 連接主板 |
| 外部安全開關 | 經 H（CN10）連接主板 |
| 變頻器(TA1,PG卡,TA2) → 馬達(ENCODER) | 經 INV 連接主板；並經 BR(BREAK)/MS(SAL)/IM(IML)/煞車器 連接 |
| CTBC-2 車廂頂部控制機板 | 經 CB2 連接主板；再連接門控制器/門馬達 |
| UMCA-2 內叫車功能板 ↔ UCDH-1R 車廂點陣顯示機板 | 車廂行動不便操作面板 |
| UCDH-1 車廂點陣顯示機板 ↔ UMCA-2 內叫車功能板 → COP各控制開關 | 車廂操作面板 |

## 圖面說明

| 修訂 | 107.11.5 配合藍.綠版修訂 |
|---|---|
| 圖名 | 系統架構 |
| 圖號 | |
| 繪圖 | DEAN KUO |

---
*2022.02.25-0版 copyright ＠ CHIMAX corporation. all right reserved. — 22*
