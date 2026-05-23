import os
from datetime import datetime, timezone
from graph_client import GraphClient


class TeamsNotifier:
    def __init__(self, client: GraphClient):
        self.client = client
        self.team_id = os.getenv("TEAMS_TEAM_ID")
        self.channel_id = os.getenv("TEAMS_CHANNEL_ID")

    def _now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def notify_ticket_created(self, ticket_id: str, title: str, priority: str, assignee: str) -> bool:
        content = (
            f"<b>New Ticket - {ticket_id}</b><br/>"
            f"<b>Title:</b> {title}<br/>"
            f"<b>Priority:</b> {priority}<br/>"
            f"<b>Assigned To:</b> {assignee}<br/>"
            f"<b>Time:</b> {self._now()}"
        )
        return self.client.send_teams_message(self.team_id, self.channel_id, content)

    def notify_ticket_resolved(self, ticket_id: str, title: str, resolution: str) -> bool:
        content = (
            f"<b>Ticket Resolved - {ticket_id}</b><br/>"
            f"<b>Title:</b> {title}<br/>"
            f"<b>Resolution:</b> {resolution}<br/>"
            f"<b>Time:</b> {self._now()}"
        )
        return self.client.send_teams_message(self.team_id, self.channel_id, content)
