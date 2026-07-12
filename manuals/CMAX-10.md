# 6.1 故障碼（黑版適用）

**格式：E X.YY.ZZ**　X=0~F 共紀錄 16 組故障紀錄,INS 時,按 CL+HUP OR HDN 可調閱

- YY = 變頻器運轉及 HOU&HOD 狀態，請由 16 進制轉換 2 進制對應 bit 查詢
- ZZ = 故障代碼

## YY 位元定義

| Bit 權值 | 定義 |
|---|---|
| 1 | YY.0 = INV F |
| 2 | YY.1 = INV R |
| 4 | YY.2 = INV MS1 |
| 8 | YY.3 = INV MS2（低位元 H） |
| 1 | YY.4 = INV MS3 |
| 2 | YY.5 = INV RUNNING |
| 4 | YY.6 = HOU 或 HOD ON |
| 8 | YY.7 = BR 動作中（高位元 H） |

## ZZ 故障代碼

| 代碼 | 說明 |
|---|---|
| ZZ=00 | 無故障 |
| ZZ=02 | INV_RUN ERR |
| ZZ=03 | DL OFF |
| ZZ=04 | UL OFF |
| ZZ=05 | BR 不 ON |
| ZZ=06 | BR 不 OFF |
| ZZ=07 | 行進中 GS OFF |
| ZZ=08 | 行進中 HDR OFF |
| ZZ=09 | 超時運轉故障 |
| ZZ=0A | 行進中 INS 回路 OFF |
| ZZ=0B | INVM 不 ON |
| ZZ=12 | 行進中 INV RUN ERR |
| ZZ=14 | 安全回路(SAR)OFF |
| ZZ=16 | DOL SW ON,HDR&GS 沒斷路,INS 及 NOR 切換時門自動開關一次 |
| ZZ=0C | ENCODER 故障 |
| ZZ=D0 | 減速距離錯誤,A5-01,00 > A5-03,02（A2-00=02 時）或 A5-01,00 > A5-03,02 或 A5-03,02 > A5-05,04（A2-00=03 時） |

## 範例：E0 AD 14 EX

- Y 高位元內容 A = INV RUNNING / BR 動作中
- Y 低位元內容 D = INV F / INVMS1 / INV MS2
- ZZ 14 = 安全迴路(SAR)OFF

## 故障調閱

- 控制盤〈C/P〉操作開關切至 INS(手動)位置， CL 按鍵按下時，顯示最後一次故障代碼。
- CL 鍵 + HUP/HDN 按鍵可調閱 16 次內之故障代碼,若故障代碼超過 16 次,則 EF.yyzz 為最後一次故障紀錄。
- CL + OP 同時按鍵 5 SEC 清除所有故障代碼紀錄 (E0.yyzz~EF.yyzz)。
- 要調閱故障碼時車廂之檢點操作不能切入,切入時於主機板將無法調閱故障碼。

---
*2022.02.25-0版 copyright ＠ CHIMAX corporation. all right reserved. — 9*
