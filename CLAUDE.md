# Templates - 模板維護者指引

你是追蹤系統模板的維護者，負責維護通用骨架供各 repo 複製使用。

## 目錄結構

```
templates/
├── lib/                        # Python 函式庫
│   ├── __init__.py
│   ├── matcher.py              # 關鍵字匹配引擎
│   ├── sentiment.py            # 情緒分析
│   ├── scorer.py               # 重要性評分
│   └── anomaly.py              # 異常偵測
│
├── scripts/                    # 執行腳本
│   ├── enrich_event.py         # 事件標註
│   ├── generate_metrics.py     # 計算每日指標
│   ├── detect_anomalies.py     # 異常偵測
│   ├── generate_daily.py       # 生成每日報告
│   ├── generate_7d_report.py   # 生成 7 日報告
│   └── update_baselines.py     # 更新歷史基準線
│
├── configs/                    # 設定檔範例
│   ├── site.yml.example        # 網站設定（標題、連結）
│   ├── companies.yml.example
│   ├── topics.yml.example
│   ├── sentiment_rules.yml.example
│   ├── importance_rules.yml.example
│   ├── anomaly_rules.yml.example
│   └── 7d_highlights_rules.yml.example
│
├── fetchers/                   # 爬蟲
│   └── base.py                 # 公司官網爬蟲基底類別
│
├── site/                       # 前端 Dashboard
│   └── index.html              # 動態載入設定（從 data/site.json）
│
├── data/                       # 資料目錄
│   ├── events/                 # 事件 (JSONL)
│   ├── metrics/                # 每日指標 (JSON)
│   └── baselines/              # 歷史基準線 (JSON)
│
├── reports/                    # 報告目錄
│   ├── daily/                  # 每日報告
│   └── 7d/                     # 7 日報告
│
├── .github/workflows/
│   └── daily-ingest.yml        # 每日自動抓取流程
│
├── requirements.txt            # Python 依賴
└── .gitignore                  # Git 忽略規則
```

## 標準流程

```
fetch_news → enrich_event → generate_metrics → detect_anomalies →
generate_daily → generate_7d_report → update_baselines → deploy
```

**重要**：`update_baselines` 必須在報告生成之後執行，避免今日資料影響今日的基準線比較。

## 各檔案職責

### lib/matcher.py
- 關鍵字匹配引擎
- 從文字中匹配公司和主題
- 判斷客戶/供應商關係（根據 companies.yml 的 upstream/downstream）

### lib/sentiment.py
- 情緒分析引擎
- 關鍵字匹配 + 否定詞處理
- 輸出 label (positive/neutral/negative) 和 score (-1 ~ 1)

### lib/scorer.py
- 重要性評分引擎
- 根據設定的規則計算分數
- 基礎分數 0.5，上限 1.0

### lib/anomaly.py
- 異常偵測引擎
- 三種異常：volume_spike, sentiment_shift, topic_resurface
- 尊重最小資料量要求

## 可客製化的部分

| 類型 | 檔案 | 說明 |
|------|------|------|
| 設定 | `configs/*.yml` | 不同產業的公司、主題、規則 |
| 邏輯 | `lib/matcher.py` | 可加入產業特有的匹配邏輯 |
| 邏輯 | `lib/sentiment.py` | 可加入產業特有的情緒詞 |
| 爬蟲 | `fetchers/*.py` | 各 repo 自行實作 |

## 新建追蹤的流程

### 快速建立（使用 memory-intel 為範本）

```bash
# 1. 在 repos/ 下建立新目錄
mkdir -p repos/{name}

# 2. 複製通用程式碼
cp -r repos/memory-intel/lib repos/{name}/
cp -r repos/memory-intel/scripts repos/{name}/
cp repos/memory-intel/fetchers/base.py repos/{name}/fetchers/
cp repos/memory-intel/.github/workflows/*.yml repos/{name}/.github/workflows/
cp repos/memory-intel/requirements.txt repos/{name}/
cp repos/memory-intel/.gitignore repos/{name}/

# 3. 複製前端（動態版）
cp -r templates/site repos/{name}/

# 4. 建立目錄結構
mkdir -p repos/{name}/data/{raw,events,metrics,baselines,normalized,cards}
mkdir -p repos/{name}/reports/{daily,7d}
mkdir -p repos/{name}/site/data/{reports/daily,reports/7d,configs}
```

### 設定檔準備

```bash
# 1. 複製範例設定檔
cp templates/configs/site.yml.example repos/{name}/configs/site.yml
cp templates/configs/companies.yml.example repos/{name}/configs/companies.yml
cp templates/configs/topics.yml.example repos/{name}/configs/topics.yml
cp repos/memory-intel/configs/sentiment_rules.yml repos/{name}/configs/
cp repos/memory-intel/configs/importance_rules.yml repos/{name}/configs/
cp repos/memory-intel/configs/anomaly_rules.yml repos/{name}/configs/
cp repos/memory-intel/configs/7d_highlights_rules.yml repos/{name}/configs/

# 2. 編輯設定檔
vim configs/site.yml          # 修改標題、網域、贊助連結
vim configs/companies.yml     # 根據研究結果填入公司清單
vim configs/topics.yml        # 填入追蹤主題和關鍵字

# 3. 轉換 YAML 到 JSON（前端使用）
python -c "import yaml, json; print(json.dumps(yaml.safe_load(open('configs/site.yml'))))" > site/data/site.json
python -c "import yaml, json; print(json.dumps(yaml.safe_load(open('configs/companies.yml'))))" > site/data/companies.json
```

### 建立爬蟲

每家公司需要一個爬蟲（繼承 `fetchers/base.py`）：

```python
# fetchers/{company_id}.py
from .base import CompanyFetcher, CompanyDocument
from datetime import datetime

class CompanyNameFetcher(CompanyFetcher):
    company_id = "company_id"
    company_name = "Company Name"
    news_url = "https://company.com/news"

    def parse_news(self, html: str) -> list[CompanyDocument]:
        soup = self._parse_html(html)
        docs = []
        # 解析邏輯...
        return docs

    def parse_ir(self, html: str) -> list[CompanyDocument]:
        return []  # 如果沒有 IR 頁面

if __name__ == "__main__":
    with CompanyNameFetcher() as fetcher:
        docs = fetcher.fetch_news()
        for doc in docs:
            print(doc.to_json())
```

### 測試

```bash
# 測試爬蟲
python -m fetchers.{company_id}

# 測試標註
python scripts/enrich_event.py --date 2026-03-16 --input data/raw/2026-03-16/test.jsonl

# 啟動本地伺服器
python -m http.server 8000 -d site
```

## 事件結構

```json
{
  "id": "{company}-{date}-{seq}",
  "date": "YYYY-MM-DD",
  "time_tags": {
    "year": 2026,
    "quarter": "Q1",
    "month": 3,
    "week": 11,
    "weekday": "Thu"
  },
  "entities": {
    "companies": ["samsung"],
    "customers": ["nvidia"],
    "suppliers": ["asml"]
  },
  "topics": ["hbm", "capacity"],
  "sentiment": {
    "label": "positive",
    "score": 0.8,
    "keywords": ["擴產", "領先"]
  },
  "importance": {
    "score": 0.85,
    "reasons": ["涉及 HBM", "供應鏈上下游同時提及"]
  },
  "title": "...",
  "content": "...",
  "sources": [
    {"url": "https://...", "type": "company_news", "fetched_at": "..."}
  ]
}
```

## site.yml 設定說明

前端 Dashboard（`site/index.html`）會從 `site/data/site.json` 讀取設定，動態更新標題、導航和連結。

```yaml
# configs/site.yml
site:
  title: "供應鏈情報"               # 網站標題（顯示在 <title> 和 <h1>）
  subtitle: "Supply Chain Intel"   # 副標題（英文，可選）
  description: "追蹤產業動態"        # 網站描述

pages:
  index: "情報總覽"                  # 首頁導航文字
  how_it_works: "運作流程"           # 運作流程頁導航文字

github:
  cname: "example.intel.weiqi.kids" # GitHub Pages 自訂網域
  repo: "weiqi-kids/example-intel"  # GitHub repo

sponsor:
  enabled: true                      # 是否顯示贊助按鈕
  url: "https://ko-fi.com/xxx"       # 贊助連結
  text: "贊助"                       # 按鈕文字

feedback:
  enabled: true                      # 是否啟用意見回饋
  api_url: "https://..."             # Feedback API URL
```

**注意**：修改 `configs/site.yml` 後，需要執行轉換：

```bash
python -c "import yaml, json; print(json.dumps(yaml.safe_load(open('configs/site.yml'))))" > site/data/site.json
```

## 開發注意事項

### 本地 vs 線上

| 環境 | 說明 | 資料來源 |
|------|------|----------|
| **線上版** | GitHub Pages 自動部署 | GitHub Actions 每日更新 |
| **本地版** | `./scripts/serve.sh` | 需要 `git pull` 同步 |

### 開發流程

```bash
# 1. 同步最新資料（重要！）
git pull origin main

# 2. 啟動本地伺服器（會自動 pull）
./scripts/serve.sh

# 3. 開發和測試
# 4. 推送變更
git push
```

### 常見誤判

| 現象 | 原因 | 解決方式 |
|------|------|----------|
| 「沒有資料」 | 看的是本地版，資料落後 | `git pull` |
| 線上正常但本地沒資料 | 本地沒同步遠端 | `git pull` |
| 剛 push 但線上沒更新 | GitHub Actions 還在執行 | 等幾分鐘 |

### 維護腳本

| 腳本 | 用途 | 使用方式 |
|------|------|----------|
| `scripts/serve.sh` | 啟動本地伺服器 | `./scripts/serve.sh` |
| `scripts/health_check.sh` | 系統健康檢查 | `./scripts/health_check.sh` |

#### health_check.sh 說明

一鍵檢查系統狀態，輸出：
- GitHub Actions 最近 5 次執行狀態（✅ 成功 / ❌ 失敗）
- 事件資料筆數和最新日期
- 股價資料公司數和最新日期
- 本地是否落後遠端

```bash
./scripts/health_check.sh

# 輸出範例：
# === GitHub Actions ===
# ✅ success  2026-03-16  Daily Data Ingest
#
# === 事件資料 ===
# ✅ 總筆數: 402
#    最新日期: 2026-03-16
#
# === 股價資料 ===
# ✅ 公司數: 18
#    最新日期: 2026-03-16
#
# === 本地同步狀態 ===
# ✅ 本地與遠端同步
```

**使用前**：修改腳本開頭的 `REPO` 和 `SITE_URL` 變數為你的設定。

## 維護原則

1. **骨架通用**：不要加入特定產業的邏輯
2. **設定驅動**：所有可變的部分都應該透過設定檔控制
3. **向後相容**：修改時要考慮已複製出去的 repo
4. **文件優先**：每次修改都要更新說明

## 參考範例

`repos/memory-intel/` 是第一個完成的追蹤，可作為完整參考：
- 19 家記憶體供應鏈公司
- 14 個追蹤主題
- 20 個爬蟲實作
- 完整的 D3.js Dashboard

---

## 每日例行（進入此 repo 時自動提醒）

當你讀取此 CLAUDE.md 時，主動執行以下檢查並提醒用戶：

### 自動檢查清單

1. **同步最新** — `git pull origin main`
2. **今日 Actions 狀態** — `gh run list --limit 1`
3. **今日事件數** — `wc -l data/events/$(date +%Y-%m-%d).jsonl`
4. **關鍵字審計** — 讀取 `site/data/reports/daily/$(date +%Y-%m-%d).json` 的 `filter_audit` 欄位

### 提醒格式

```
📋 每日狀態
- Actions: ✅/❌
- 今日事件: N 筆
- 關鍵字審計: ✅ 通過 / ⚠️ gate2 擋住率 XX%，建議檢視
```

若 `filter_audit.alert` 為 true 或 `gate2_block_rate > 30%`，提醒用戶：「有關鍵字需要調整，要執行關鍵字審計嗎？」

### 關鍵字審計流程（用戶確認後執行）

1. 檢視 `filter_audit.gate2_samples` 中被擋住的文章標題
2. 判斷每篇是否與本追蹤產業相關
3. 相關的文章 → 找出缺少的關鍵字，建議新增到 `configs/topics.yml`
4. 呈現結果：

```
## 關鍵字審計結果

通過率：XX% | Gate 2 擋住率：XX%

### 被擋住但應通過的文章
| 標題 | 缺少的關鍵字 | 建議加入的主題 |
|------|-------------|--------------|

### 建議新增關鍵字
topics.yml → {topic_id} → keywords 新增：
- keyword1
- keyword2
```

5. 用戶確認後更新 `configs/topics.yml`，commit + push
