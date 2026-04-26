@echo off
echo --- DANG CHAY QUY TRINH TU DONG ---

echo 1. Phan tich AAPL...
python main.py AAPL --clear-checkpoints
timeout /t 120

echo 2. Phan tich NVDA...
python main.py NVDA --clear-checkpoints
timeout /t 120

echo 3. Phan tich MSFT...
python main.py MSFT --clear-checkpoints

echo --- TAT CA DA HOAN THANH ---
pause