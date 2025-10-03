@echo off
cd /d C:\程式碼練習\面試\Steam 遊戲資料統計與顯示

REM 執行 Python 程式
python findGameData.py

REM Git 上傳流程
git add .
git commit -m "Auto update on %date% %time%"
git push