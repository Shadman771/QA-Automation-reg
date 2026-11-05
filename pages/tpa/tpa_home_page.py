"""TPA > Home (/tpa/Home) - the Transfer Pricing Analyzer landing/dashboard
view, confirmed live via scratchpad discovery scripts (not part of the
suite). No jurisdiction/category left panel - a dashboard of cards and
feeds:

  - `h1` "Recent News": a real feed of news article cards (title, date,
    excerpt), each a real link.
  - `h3` cards: "My Projects", "My TPA Research", "Use a Virtual Coach".
  - `h4` sections: "Monthly Briefs" (real "Transfer Pricing Brief:
    <Month Year>" entries, the same monthly-brief shape as RegBriefings'
    Archive) and "Quick Access".
  - A snippet of recent real Forms/Regulations entries.
  - "View full tutorial gallery" link.

Supports a direct deep link (`/tpa/Home`, see pages/tpa/tpa_common.py)."""
from playwright.sync_api import Page

from pages.tpa.tpa_common import tpa_goto


class TpaHomePage:
    def __init__(self, page: Page):
        self.page = page
        self.recent_news_heading = page.get_by_role("heading", name="Recent News", exact=True)
        self.my_projects_heading = page.get_by_role("heading", name="My Projects", exact=True)
        self.my_tpa_research_heading = page.get_by_role("heading", name="My TPA Research", exact=True)
        self.virtual_coach_heading = page.get_by_role("heading", name="Use a Virtual Coach", exact=True)
        self.monthly_briefs_heading = page.get_by_role("heading", name="Monthly Briefs", exact=True)
        self.quick_access_heading = page.get_by_role("heading", name="Quick Access", exact=True)
        self.tutorial_gallery_link = page.get_by_role("link", name="View full tutorial gallery")

    def goto(self):
        tpa_goto(self.page, "/tpa/Home")

    def is_loaded(self) -> bool:
        return "/tpa/Home" in self.page.url and self.recent_news_heading.is_visible()

    def news_article_link(self, title_substring: str):
        return self.page.get_by_role("link", name=title_substring).first
