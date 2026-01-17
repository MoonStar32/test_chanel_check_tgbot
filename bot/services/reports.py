"""Reporting and export service."""

import asyncio
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import gspread
from fpdf import FPDF
from gspread.exceptions import WorksheetNotFound
from loguru import logger

from aiogram.types import BufferedInputFile

from bot.config import settings
from bot.i18n import I18n
from database.models import Channel, MemberEvent
from database.repositories import EventRepository, MemberRepository


@dataclass
class ReportData:
    """Container for report metrics."""

    channel_id: int
    channel_title: str
    period_days: int
    member_counts: dict[str, int]
    stats: dict[str, int]
    events: list[MemberEvent]


class ReportsService:
    """Generate reports in PDF/JSON and sync to Google Sheets."""

    def __init__(
        self,
        event_repo: EventRepository,
        member_repo: MemberRepository,
    ) -> None:
        self.event_repo = event_repo
        self.member_repo = member_repo

    async def collect(self, channel: Channel, days: int = 30) -> ReportData:
        stats = await self.event_repo.get_member_events_stats(channel.id, days)
        member_counts = await self.member_repo.count_by_status(channel.id)
        events = await self.event_repo.get_recent_member_events(
            channel.id,
            limit=500,
        )
        return ReportData(
            channel_id=channel.id,
            channel_title=channel.title,
            period_days=days,
            member_counts=member_counts,
            stats=stats,
            events=events,
        )

    async def export_pdf(
        self,
        channel: Channel,
        days: int = 30,
        i18n: I18n | None = None,
    ) -> BufferedInputFile:
        data = await self.collect(channel, days)
        pdf = FPDF()
        pdf.add_page()
        self._set_unicode_font(pdf, bold=True, size=16)
        pdf.cell(0, 10, txt=f"{data.channel_title} - {days}d report", ln=1)

        self._set_unicode_font(pdf, size=12)
        pdf.cell(0, 10, txt=f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ln=1)
        pdf.cell(0, 10, txt=f"Active members: {data.member_counts.get('member', 0)}", ln=1)
        pdf.cell(0, 10, txt=f"Left: {data.member_counts.get('left', 0)}", ln=1)
        pdf.cell(0, 10, txt=f"Joins: {data.stats.get('join', 0)}", ln=1)
        pdf.cell(0, 10, txt=f"Leaves: {data.stats.get('leave', 0)}", ln=1)
        pdf.cell(0, 10, txt=f"Kicks: {data.stats.get('kick', 0)}", ln=1)
        pdf.cell(0, 10, txt=f"Bans: {data.stats.get('ban', 0)}", ln=1)

        pdf.ln(5)
        self._set_unicode_font(pdf, bold=True, size=12)
        pdf.cell(0, 10, txt="Recent events:", ln=1)
        self._set_unicode_font(pdf, size=10)
        for event in data.events[:50]:
            line = (
                f"{event.created_at.strftime('%Y-%m-%d %H:%M')}: "
                f"{event.event_type} - {event.username or event.full_name} ({event.user_id})"
            )
            pdf.multi_cell(0, 8, txt=line)

        pdf_bytes = pdf.output(dest="S").encode("latin-1", errors="ignore")
        filename = f"report_{channel.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return BufferedInputFile(pdf_bytes, filename=filename)

    async def export_json(
        self,
        channel: Channel,
        days: int = 30,
    ) -> BufferedInputFile:
        data = await self.collect(channel, days)

        payload: dict[str, Any] = {
            "channel_id": data.channel_id,
            "channel_title": data.channel_title,
            "period_days": data.period_days,
            "member_counts": data.member_counts,
            "stats": data.stats,
            "events": [
                {
                    "id": ev.id,
                    "user_id": ev.user_id,
                    "username": ev.username,
                    "first_name": ev.first_name,
                    "last_name": ev.last_name,
                    "event_type": ev.event_type,
                    "old_status": ev.old_status,
                    "new_status": ev.new_status,
                    "inviter_id": ev.inviter_id,
                    "created_at": ev.created_at.isoformat() if ev.created_at else None,
                }
                for ev in data.events
            ],
        }
        json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        filename = f"report_{channel.id}_{datetime.now().strftime('%Y%m%d')}.json"
        return BufferedInputFile(json_bytes, filename=filename)

    async def export_to_sheets(
        self,
        channel: Channel,
        days: int = 30,
        creds_json: str | None = None,
        spreadsheet_id: str | None = None,
    ) -> bool:
        """Sync events to Google Sheets. Prefers user-provided creds; falls back to env."""
        creds_json = creds_json or None
        spreadsheet_id = spreadsheet_id or settings.google_sheets_spreadsheet_id
        cred_path = settings.google_service_account_json

        if not ((creds_json or cred_path) and spreadsheet_id):
            logger.warning("Google Sheets credentials or spreadsheet id not configured")
            return False

        data = await self.collect(channel, days)

        def _sync():
            try:
                if creds_json:
                    gc = gspread.service_account_from_dict(json.loads(creds_json))
                else:
                    gc = gspread.service_account(filename=cred_path)

                sh = gc.open_by_key(spreadsheet_id)
                ws_title = str(channel.id)
                try:
                    ws = sh.worksheet(ws_title)
                    ws.clear()
                except WorksheetNotFound:
                    ws = sh.add_worksheet(title=ws_title, rows=1000, cols=10)

                rows = [
                    [
                        "Date",
                        "Time",
                        "Event Type",
                        "User ID",
                        "Username",
                        "First Name",
                        "Last Name",
                        "Old Status",
                        "New Status",
                    ]
                ]
                for ev in data.events:
                    rows.append(
                        [
                            ev.created_at.strftime("%Y-%m-%d") if ev.created_at else "",
                            ev.created_at.strftime("%H:%M:%S") if ev.created_at else "",
                            ev.event_type,
                            ev.user_id,
                            ev.username or "",
                            ev.first_name or "",
                            ev.last_name or "",
                            ev.old_status or "",
                            ev.new_status,
                        ]
                    )
                ws.update(rows)

                # Summary sheet
                summary_title = "summary"
                try:
                    s_ws = sh.worksheet(summary_title)
                except WorksheetNotFound:
                    s_ws = sh.add_worksheet(title=summary_title, rows=100, cols=10)
                summary_rows = [
                    ["Channel ID", "Channel Title", "Period", "Active", "Left", "Joins", "Leaves", "Kicks", "Bans"],
                    [
                        data.channel_id,
                        data.channel_title,
                        data.period_days,
                        data.member_counts.get("member", 0),
                        data.member_counts.get("left", 0),
                        data.stats.get("join", 0),
                        data.stats.get("leave", 0),
                        data.stats.get("kick", 0),
                        data.stats.get("ban", 0),
                    ],
                ]
                s_ws.update(summary_rows)
                return True
            except Exception as e:  # noqa: BLE001
                logger.error(f"Google Sheets sync failed: {e}")
                return False

        return await asyncio.to_thread(_sync)

    def _set_unicode_font(self, pdf: FPDF, bold: bool = False, size: int = 12) -> None:
        """Set a Unicode-capable font if available, fallback to Helvetica."""
        font_dir = "/usr/share/fonts/truetype/dejavu"
        regular_path = os.path.join(font_dir, "DejaVuSans.ttf")
        bold_path = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
        style = "B" if bold else ""
        if os.path.exists(regular_path) and os.path.exists(bold_path):
            # Register once
            if "DejaVu" not in pdf.fonts:
                pdf.add_font("DejaVu", "", regular_path, uni=True)
                pdf.add_font("DejaVu", "B", bold_path, uni=True)
            pdf.set_font("DejaVu", style=style, size=size)
        else:
            pdf.set_font("Helvetica", style=style, size=size)
