# 此資料夾放的是做實驗用的檔案

此實驗是用 [SUMO](https://sumo.dlr.de/docs/index.html) 來模擬在two-to-one-road的情境下，使用各種 Lane-Changing 和 Lane-Merging 策略得到的結果，詳情請看 ``\Survey_and_Experiment__Lane_Merging.pdf``

- 記得下載 [SUMO](https://sumo.dlr.de/docs/Downloads.php)
- ``python run.py``
- `-c [lane-changing演算法]`，lane-changing演算法有: no(default), all, nowaiting, random(TODO: still has some bug)
- `-m [lane-merging演算法]`,  lane-merging演算法有: fifo(default), random
- `--step-length [n]` or `--sl [n]`, 數字介於[0.001 and 1.0]，表示一個step代表實際幾秒, default: 0.1
- `--new`, 代表會使用新的input
- `--gui`, 代表會顯示GUI
- `--show`，代表會顯示總花費步數
- input.txt會儲存上一次跑的simulation的input