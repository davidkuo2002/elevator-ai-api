# 10. 線路圖 — 照明及風扇／車廂門控制器（風扇照明門電源控制回路）

> 廂上CTBC-2板（）內數字為活纜編號

## 端子對應

| CB1(CN31) | Pin配置 |
|---|---|
| (4)3 AC22 / AC21 1(3) | |
| (2)4 AC12 / AC11 2(1) | |

| CB2(CN45) | Pin配置 |
|---|---|
| (18)8 0V/24V 1(17) | |
| (16)9 NOR/OP 2(15) | |
| PE/DZ | |
| HOD/HOU | |
| DO2/DO1 | |
| (8)15 A2/A1 6(7) | |
| (6)16 G2/G1 7(5) | |

## 車廂通風扇（FAN）

- RY2_RELAY：+24 供電，CPU-FAN 控制
- CB1-2(CN31) AC11、CB1-4(CN31) AC12
- 輸出至 CN14-2/CN15-2、CN14-1/CN15-1 → 車廂通風扇 AC110V OR AC220V
- CN38-4,5（COP1A）連接

## 車廂照明（LIGHT）

- RY1_RELAY：+24 供電，CPU-LT 控制
- CB1-2(CN31) AC11、CB1-4(CN31) AC21
- 輸出至 CN12-2/CN13-2、CN12-1/CN13-1 → 車廂照明 AC110V OR AC220V
- CN38-9,10（COP1A）連接

## 車廂門控制器（DMC）

- LY2_RELAY：+24 供電，CPU-DMC 控制
- CNK2-R10、CNK2-T10
- 輸出至 CN35-1(DMC1)/CN36-1(DMC2)、CN35-4(DMC1)/CN36-4(DMC2) → 車廂門控制器 AC110V OR AC220V
- CN38-3,8（COP1A）連接

> AC11,AC12 = FAN,LIGHT 電源，請依使用電源接線
> AC21,AC22 = DMC(門控制器)電源，請依使用電源接線

## 警鈴(AL)/蜂鳴器(BZ)

- AL：+6V 供電，CPU-AL 控制，CN26-1/CN26-2
- BZ 與 AL 按鈕共用
- AL SW：CN42,CN43,CN44-6(AL),12(ALC)
- BZ：+6V 供電，(CN3) D-B/S T/L R 6G 6V

## 端子明細（CB1/CB2/DMC1/DMC2/COP系列）

| 端子群 | 內容 |
|---|---|
| CB1(CN31) | AC22,AC21,AC12,AC11 |
| CB2(CN45) | 0V,24V,NOR,OP,PE,DZ,HOD,HOU,DO2,DO1,A2,A1,G2,G1 |
| DMC1(CN35) | AC,AC,DMc,DMa,DMc,DMb |
| DMC1(CN36) | AC,AC,DMc,DMa,DMc,DMb |
| COP1A(CN38) | RUN,RUN,NOR,NOR,DMC,DMC,LIGHT,FAN,0V,0V |
| COP2A(CN39) | RUN,RUN,NOR,NOR,DMC,DMC,LIGHT,FAN,0V,0V |
| COP1B,2B,3B(CN42,43,44) | OPL,24V,HOL,OP,0V,CL,0V,HOLD,0V,GK,ALC,AL |

## 圖面說明

| 修訂 | 111.02.01 配合藍綠版修訂 |
|---|---|
| 圖名 | 風扇照明門電源 |
| 圖號 | |
| 繪圖 | LIANG |

---
*2022.02.25-0版 copyright ＠ CHIMAX corporation. all right reserved. — 28*
