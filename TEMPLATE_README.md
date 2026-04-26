# 追蹤專案模板

## 使用方法

1. 建立新 repo 目錄: `mkdir repos/{name}`
2. 複製模板: `cp -r templates/* repos/{name}/`
3. 自訂設定:
   - `configs/companies.yml` — 追蹤的公司清單
   - `configs/topics.yml` — 追蹤的主題和關鍵字
4. 建立虛擬環境: `cd repos/{name} && python -m venv .venv && pip install -r requirements.txt`
5. 測試: `python scripts/fetch_stocks.py`
