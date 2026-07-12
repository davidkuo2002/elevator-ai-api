# 10. 線路圖 — 主電源回路

## 220V 電源輸入

- 三相 220V 電源：R、S、T；單相電源請接於 R、T
- NFB（MAIN PW）→ 變壓器：0/220/380 抽頭
- 輸入電源為 380V 時，變壓器無熔絲開關二次側 T 相接此端子

## SAL 迴路

- CN14-7(DC-)、CN14-8(DC+) — sal/a1、sal/a2
- AC220：CN13-8(R)、CN13-1(T)（說明①，技術通告 CM-003）
- AC110：CN15-1(R10)、CN15-10(T10)
- CN13-9(T22)、CN13-2(R22)
- SW1（5A FU1，操作用保險絲）

## DC24V 電源供應器

- 輸入 L、N（來自 CN13-3(R22)、CN13-10(T22)）
- 輸出 +V、-V、G → +24V(CN13-2)、0V(CN13-1)、FG
- PW：CN12(CB2)-18(0V)、CN12(CB2)-17(24V)
- FU5（3A）保險絲

## BR 迴路（馬達抱閘）

- CN4-1(BKSW)、CN4-2(BKSW)
- BR 三相輸出 R、S、T → BR 線圈
- CN14-15(B-)、CN14-16(B+)

## HITAKE 變頻器接線

- MS(CN14-3) → SAL 線圈
- AC(CN14-11)
- IM(CN14-4) → IML 線圈（PM馬達封星回路）
- AC(CN14-12)
- IML 不使用時需將 IMS(CN14-5) 與 IMSW(CN14-13) 短接
- 變頻器 U/V/W 端子接捲揚機馬達
- N/P/B 端子接煞車電阻器
- IMS：CN14-5、CN14-13
- INVERTER PG-B2：PG(CN22)-2(PA)、-3(PB)、-4(0V) → TA2/TA1
- ENCODER 接於捲揚機馬達軸端

## 圖面說明

| 修訂 | 107.11.5 配合藍.綠版修訂 |
|---|---|
| 圖名 | 主電源回路 |
| 圖號 | |
| 繪圖 | DEAN KUO |

> 裝設 IML 電磁接觸器時,需確認變頻器停止方式功能

---
*2022.02.25-0版 copyright ＠ CHIMAX corporation. all right reserved. — 23*
