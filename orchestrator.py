import os
import uuid
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "graph-api"))


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


CATEGORY_KEYWORDS = {
    "network":  ["vpn", "wifi", "internet", "network", "connectivity", "dns"],
    "hardware": ["laptop", "monitor", "keyboard", "mouse", "printer", "hardware"],
    "software": ["install", "application", "app", "license", "crash", "software", "error"],
    "access":   ["password", "login", "access", "permission", "account", "locked", "mfa"],
    "email":    ["email", "outlook", "mailbox", "calendar", "teams", "exchange"],
}

ROUTING_TABLE = {
    "network":  "network-team@company.com",
    "hardware": "hardware-team@company.com",
    "software": "software-team@company.com",
    "access":   "iam-team@company.com",
    "email":    "messaging-team@company.com",
    "general":  "helpdesk@company.com",
}

AUTO_RESOLUTIONS = {
    "access": (
        "Visit the self-service portal at portal.company.com to reset your password "
        "or unlock your account."
    ),
    "email": (
        "Restart Outlook and clear the Office cache by running FixMAPI. "
        "If the issue persists it will be escalated."
    ),
}


@dataclass
class Ticket:
    title: str
    description: str
    submitter_email: str
    ticket_id: str = field(default_factory=lambda: f"TKT-{uuid.uuid4().hex[:8].upper()}")
    status: TicketStatus = TicketStatus.OPEN
    priority: str = "Medium"
    category: str = ""
    assignee: str = ""
    resolution: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    log: list = field(default_factory=list)


def _classify(ticket: Ticket) -> str:
    text = f"{ticket.title} {ticket.description}".lower()
    scores = {cat: sum(1 for kw in kws if kw in text) for cat, kws in CATEGORY_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def _resolve_priority(description: str) -> str:
    text = description.lower()
    if any(s in text for s in ["urgent", "critical", "production", "outage", "blocked"]):
        return "High"
    if any(s in text for s in ["when possible", "low priority", "minor"]) or len(description.split()) < 15:
        return "Low"
    return "Medium"


class HelpdeskOrchestrator:
    def __init__(self, notifier=None, graph_client=None):
        self.notifier = notifier
        self.graph_client = graph_client

    def run(self, ticket: Ticket) -> Ticket:
        ticket.category = _classify(ticket)
        ticket.log.append({"step": "classify", "result": ticket.category})

        ticket.priority = _resolve_priority(ticket.description)
        ticket.log.append({"step": "priority", "result": ticket.priority})

        ticket.assignee = ROUTING_TABLE.get(ticket.category, ROUTING_TABLE["general"])
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.log.append({"step": "route", "assignee": ticket.assignee})

        resolution: Optional[str] = AUTO_RESOLUTIONS.get(ticket.category)
        if resolution:
            ticket.resolution = resolution
            ticket.status = TicketStatus.RESOLVED
            ticket.log.append({"step": "resolve", "resolution": resolution})
            if self.notifier:
                self.notifier.notify_ticket_resolved(ticket.ticket_id, ticket.title, resolution)
        else:
            ticket.status = TicketStatus.ESCALATED
            ticket.log.append({"step": "escalate", "reason": "No auto-resolution available"})
            if self.notifier:
                self.notifier.notify_ticket_created(
                    ticket.ticket_id, ticket.title, ticket.priority, ticket.assignee
                )

        if self.graph_client:
            site_id = os.getenv("SHAREPOINT_SITE_ID", "")
            list_id = os.getenv("SHAREPOINT_LIST_ID", "")
            self.graph_client.create_list_item(site_id, list_id, {
                "Title": ticket.ticket_id,
                "TicketTitle": ticket.title,
                "Status": ticket.status.value,
                "Priority": ticket.priority,
                "Category": ticket.category,
                "Assignee": ticket.assignee,
                "Submitter": ticket.submitter_email,
                "Resolution": ticket.resolution,
            })
            ticket.log.append({"step": "persist", "result": "ok"})

        return ticket


if __name__ == "__main__":
    sample = Ticket(
        title="Cannot connect to VPN from home",
        description="Since this morning I cannot establish a VPN connection. Error 789. This is urgent - I cannot access any internal systems.",
        submitter_email="jane.doe@company.com",
    )
    result = HelpdeskOrchestrator().run(sample)
    print(f"Ticket   : {result.ticket_id}")
    print(f"Category : {result.category}")
    print(f"Priority : {result.priority}")
    print(f"Assignee : {result.assignee}")
    print(f"Status   : {result.status.value}")
    print(f"Steps    : {len(result.log)}")
