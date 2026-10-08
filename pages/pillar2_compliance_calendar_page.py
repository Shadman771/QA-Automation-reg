"""Pillar 2 > Compliance Calendar (/wta/ComplianceCalendar). Confirmed
live: a left "Jurisdictions" panel (no categories); selecting a single
jurisdiction alone renders a "Showing compliance calendar of <Country>"
table with a fixed set of 5 deadline rows (Deadline Type / Due Date):
GIR Filing Deadline, Notification Deadline, Registration Deadline,
Top-Up Tax Payment Deadline, Top-Up Tax Return Filing Deadline."""
from playwright.sync_api import Page

from config.settings import APP_ORIGIN
from pages.wta_common import JurisdictionPanel

DEADLINE_TYPES = [
    "GIR Filing Deadline", "Notification Deadline", "Registration Deadline",
    "Top-Up Tax Payment Deadline", "Top-Up Tax Return Filing Deadline",
]


class ComplianceCalendarPage:
    def __init__(self, page: Page):
        self.page = page
        self.jurisdiction = JurisdictionPanel(page)
        self.placeholder_text = page.get_by_text("Use the left panel to choose jurisdiction.")
        self.showing_text = page.get_by_text("Showing compliance calendar of", exact=False)
        self.table = page.locator("table")
        self.table_header_deadline_type = page.get_by_role("columnheader", name="Deadline Type")
        self.table_header_due_date = page.get_by_role("columnheader", name="Due Date")

    def goto(self):
        self.page.goto(f"{APP_ORIGIN}/wta/ComplianceCalendar", wait_until="networkidle")
