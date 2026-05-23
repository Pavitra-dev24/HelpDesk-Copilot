# HelpDesk Copilot

A demo project showing AI-powered IT support automation built on Microsoft Power Platform. Covers the full ticket lifecycle from submission to resolution using Copilot Studio, Power Apps, Power Automate, and Microsoft Graph API.

---

## What It Does

Users submit IT support tickets through a Power Apps canvas app or a Copilot Studio conversational bot in Microsoft Teams. A Power Automate flow picks up each new ticket, looks up the submitter via Graph API, and posts a Teams notification. An Agentic AI orchestrator written in Python classifies the ticket, sets priority, routes it to the right team, and attempts auto-resolution for common issues before falling back to human escalation.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Conversational AI | Microsoft Copilot Studio / Power Virtual Agents |
| Front-End | Microsoft Power Apps (Canvas) |
| Automation | Microsoft Power Automate |
| Messaging + Data | Microsoft Graph API v1.0 |
| Storage | SharePoint Online Lists |
| Notifications | Microsoft Teams |
| Agentic AI Engine | Python 3.11 |
| Auth | Azure AD OAuth 2.0 (client credentials) |
| Testing | pytest |

All Python dependencies are free and open source.

---

## Project Structure

```
helpdesk-copilot/
|-- README.md
|-- requirements.txt
|-- .env.example
|-- graph-api/
|   |-- graph_client.py       # MS Graph API wrapper
|   +-- teams_notifier.py     # Teams message helpers
|-- agentic/
|   +-- orchestrator.py       # Ticket triage pipeline
|-- copilot-studio/
|   +-- bot-schema.json       # Copilot Studio topic definitions
|-- power-automate/
|   +-- ticket-routing-flow.json
|-- power-apps/
|   |-- app-config.json
|   +-- screens/TicketForm.yaml
|-- sharepoint/
|   +-- list-schema.json
+-- tests/
    |-- test_graph_client.py
    +-- test_orchestrator.py
```

---

## Setup

### Prerequisites

- Python 3.11+
- An Azure AD app registration with Graph API permissions: `ChannelMessage.Send`, `Sites.ReadWrite.All`, `User.Read.All`
- A SharePoint site with a Tickets list matching `sharepoint/list-schema.json`
- A Microsoft Teams team and channel for notifications
- A Power Platform environment (Microsoft 365 license)

### Install

```bash
git clone https://github.com/your-username/helpdesk-copilot.git
cd helpdesk-copilot
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your Azure AD and SharePoint/Teams IDs.

### Run the Orchestrator

```bash
python agentic/orchestrator.py
```

### Run Tests

```bash
pytest tests/ -v
```

---

## Power Platform Deployment

**Copilot Studio** - Import `copilot-studio/bot-schema.json` via the Topics page, connect the SharePoint and Power Automate actions, then publish to your Teams team.

**Power Automate** - Import `power-automate/ticket-routing-flow.json`, re-authenticate the SharePoint and Teams connectors, then enable the flow.

**Power Apps** - Connect a new canvas app to the SharePoint Tickets list and apply `power-apps/screens/TicketForm.yaml`.

---

## Environment Variables

| Variable | Description |
|---|---|
| `TENANT_ID` | Azure AD tenant ID |
| `CLIENT_ID` | App registration client ID |
| `CLIENT_SECRET` | App registration client secret |
| `SHAREPOINT_SITE_ID` | SharePoint site ID |
| `SHAREPOINT_LIST_ID` | Tickets list ID |
| `TEAMS_TEAM_ID` | Teams team ID |
| `TEAMS_CHANNEL_ID` | Teams channel ID |

---
