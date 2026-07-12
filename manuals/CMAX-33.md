# 10. 線路圖 — 控盤及車廂手/自動回路

## 車廂內/車廂頂 端子（COP1A CN38, COP2A CN39, 頂控器CB2 CN45）

| COP1A (CN38) | | COP2A (CN39) | | 頂控器 CB2 (CN45) |
|---|---|---|---|---|
| 10 RON/RON 9 | | NOR/NOR | | 18 0V/24V 17 |
| 8 NOR/NOR 7 | | | | 16 NOR/OP 15 |
| DMC/DMC | | | | 14 PE/DZ 13 |
| 4 FAN/FAN 3 | | | | 12 HOD/HOU 11 |
| 2 0V/0V 1 | | | | 10 DO2/DO1 9 |
| | | | | 8 A2/A1 7 |
| | | | | 6 G2/G1 5 |

（控制櫃側 CB2 CN45 端子配置相同，經連控端傳輸）

## 車廂上手/自動控制開關

- 自動：NOR
- 手動：H_UP、H_DN（車廂上手動上升,下降開關）
- MDC、UM、DM

COP1A-2/COP2A-2（NOR）與 COP1A-7/COP2A-7（0V，ON時自動）經 COP手/自動開關 至 CB2-16(NOR) → 主控板MAX81 自動：NOR Relay

## NOR Relay/RY8

- 0V → NOR → C
- C → U/HUP、D/HDN

## 圖面說明

| 修訂 | 111.02.01 配合藍錄版修訂 |
|---|---|
| 圖名 | 手/自動回路 |
| 圖號 | |
| 繪圖 | LIANG |

---
*2022.02.25-0版 copyright ＠ CHIMAX corporation. all right reserved. — 32*
