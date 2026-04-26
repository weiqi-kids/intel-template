# intel-template

產業情報追蹤系統模板。新建追蹤 = fork 此 repo。

## 快速開始

### 1. Fork 此 repo

在 GitHub 上 fork `weiqi-kids/intel-template`，命名為 `{industry}-intel`（例如 `cement-intel`）。

### 2. 設定追蹤目標

```bash
# 複製範例設定檔
cp configs/companies.yml.example configs/companies.yml
cp configs/topics.yml.example configs/topics.yml
cp configs/feeds.yml.example configs/feeds.yml
cp configs/site.yml.example configs/site.yml

# 編輯設定
# companies.yml — 填入追蹤公司清單、rss_url、stock_id
# topics.yml — 填入追蹤主題和關鍵字
# feeds.yml — 填入產業媒體 RSS feed
# site.yml — 修改網站標題和網域
```

### 3. 建立爬蟲

每家追蹤公司建立一個 Playwright fetcher：

```python
# fetchers/cemex.py
from .base import CompanyFetcher, CompanyDocument
from datetime import datetime

class CemexFetcher(CompanyFetcher):
    company_id = "cemex"
    company_name = "CEMEX"
    news_url = "https://www.cemex.com/media/press-releases"

    def parse_news(self, html: str) -> list[CompanyDocument]:
        soup = self._parse_html(html)
        docs = []
        for article in soup.select("article"):
            title_el = article.select_one("h2 a, h3 a")
            if not title_el:
                continue
            docs.append(CompanyDocument(
                company_id=self.company_id,
                doc_type="news",
                title=title_el.get_text(strip=True),
                url=title_el.get("href", ""),
                language="en",
                tags=["news"],
            ))
        return docs

    def parse_ir(self, html: str) -> list[CompanyDocument]:
        return []

if __name__ == "__main__":
    fetcher = CemexFetcher()
    result = fetcher.fetch_all()
    for docs in result.values():
        for doc in docs:
            print(doc.to_json())
```

測試：`python -m fetchers.cemex`

### 4. 啟用 GitHub Actions

1. 確認 `.github/workflows/daily-ingest.yml` 的 cron 設定
2. 在 GitHub repo Settings > Pages 啟用 GitHub Pages（source: GitHub Actions）
3. 設定 CNAME（如 `cement.intel.weiqi.kids`）

### 5. 驗證

```bash
# 手動觸發一次
gh workflow run daily-ingest.yml

# 檢查結果
gh run list --limit 3
```

## 目錄結構

```
├── configs/          # 設定檔（.example 為範例，複製後移除 .example）
├── fetchers/         # 公司爬蟲（每家一個 .py）
├── lib/              # 規則引擎（matcher, sentiment, scorer, anomaly）
├── scripts/          # Pipeline 腳本
├── data/             # 資料目錄（自動產生）
├── reports/          # 報告目錄（自動產生）
├── site/             # 前端 Dashboard
└── .github/workflows/  # GitHub Actions
```

## Pipeline

每日 08:00 UTC 自動執行：

```
fetch_stocks → fetch_companies → fetch_rss → normalize →
fetch_financials → generate_cards → enrich_event (x2) →
generate_metrics → generate_daily → generate_7d_report →
generate_report_indexes → generate_config_stats →
sync_to_frontend → update_site_data → commit + push → deploy
```

## 從 upstream 取得更新

如果你的 repo 是從此 template fork 的，可以取得上游修復：

```bash
git fetch upstream
git merge upstream/main
# 或 cherry-pick 特定 commit
git cherry-pick <commit-hash>
```
