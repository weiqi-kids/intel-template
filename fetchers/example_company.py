"""Example fetcher skeleton.

Copy this file as a starting point for each company you want to track.
Rename to {company_id}.py and update the class.

Usage:
    python -m fetchers.example_company
"""

from .base import CompanyFetcher, CompanyDocument
from datetime import datetime


class ExampleCompanyFetcher(CompanyFetcher):
    """Example company fetcher.

    Attributes to configure:
        company_id:  Must match the 'id' in configs/companies.yml
        company_name: Display name
        news_url:    Company newsroom or press release page
        ir_url:      Investor relations page (optional)
        ir_rss_url:  IR RSS feed URL (optional, preferred over HTML scraping)
        fetch_mode:  'rss' | 'http' | 'playwright'
                     - rss: fastest, use when RSS feed available
                     - http: for static HTML pages
                     - playwright: for JS-rendered pages (slowest)
    """

    company_id = "example_company"
    company_name = "Example Company"
    news_url = "https://example.com/news"
    ir_url = "https://example.com/investor-relations"
    # ir_rss_url = "https://example.com/rss/news.xml"  # uncomment if RSS available
    # fetch_mode = "rss"  # uncomment to use RSS mode

    def parse_news(self, html: str) -> list[CompanyDocument]:
        """Parse the news page HTML and extract articles.

        Args:
            html: Raw HTML from news_url

        Returns:
            List of CompanyDocument with title, url, published_at, content
        """
        soup = self._parse_html(html)
        docs = []

        # Example: find all article links
        # Adapt the selectors to match the target website's HTML structure
        #
        # for article in soup.select("div.news-item"):
        #     title = article.select_one("h3").get_text(strip=True)
        #     link = article.select_one("a")["href"]
        #     date_text = article.select_one("span.date").get_text(strip=True)
        #
        #     docs.append(CompanyDocument(
        #         doc_type="news",
        #         title=title,
        #         url=link,
        #         published_at=date_text,
        #         content="",
        #     ))

        return docs

    def parse_ir(self, html: str) -> list[CompanyDocument]:
        """Parse the IR page HTML and extract filings/announcements.

        Return empty list if the company has no IR page or uses RSS instead.
        """
        return []


if __name__ == "__main__":
    with ExampleCompanyFetcher() as fetcher:
        docs = fetcher.fetch_news()
        print(f"Found {len(docs)} news articles")
        for doc in docs[:3]:
            print(f"  - {doc.title}")
