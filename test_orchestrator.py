import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agentic"))

from orchestrator import Ticket, HelpdeskOrchestrator, TicketStatus


def _run(title, description):
    t = Ticket(title=title, description=description, submitter_email="u@co.com")
    return HelpdeskOrchestrator().run(t)


class TestClassification(unittest.TestCase):
    def test_network(self):
        self.assertEqual(_run("VPN not working", "Cannot connect to VPN.").category, "network")

    def test_access(self):
        self.assertEqual(_run("Account locked", "My account is locked and I cannot login.").category, "access")

    def test_hardware(self):
        self.assertEqual(_run("Laptop broken", "My laptop keyboard stopped working.").category, "hardware")

    def test_software(self):
        self.assertEqual(_run("App crash", "The application crashes on install.").category, "software")

    def test_email(self):
        self.assertEqual(_run("Outlook issue", "My email mailbox is not syncing in Outlook.").category, "email")

    def test_general_fallback(self):
        self.assertEqual(_run("Office query", "I have a question about room booking.").category, "general")


class TestPriority(unittest.TestCase):
    def test_high_on_urgent_signal(self):
        self.assertEqual(_run("Down", "This is urgent - production is completely blocked.").priority, "High")

    def test_low_on_explicit_signal(self):
        self.assertEqual(_run("Minor", "When possible could you help with this?").priority, "Low")

    def test_medium_by_default(self):
        result = _run(
            "Software install",
            "The setup wizard fails partway through with no error message. I have tried reinstalling twice with consistent results.",
        )
        self.assertEqual(result.priority, "Medium")


class TestRouting(unittest.TestCase):
    def test_network_routes_correctly(self):
        self.assertEqual(_run("VPN", "Cannot connect to VPN or internet.").assignee, "network-team@company.com")

    def test_access_routes_correctly(self):
        self.assertEqual(_run("Locked out", "My account is locked and I cannot login.").assignee, "iam-team@company.com")

    def test_general_routes_to_helpdesk(self):
        self.assertEqual(_run("Office query", "I have a question about room booking.").assignee, "helpdesk@company.com")


class TestAutoResolution(unittest.TestCase):
    def test_access_is_auto_resolved(self):
        result = _run("Account locked", "I cannot login. My account is locked.")
        self.assertEqual(result.status, TicketStatus.RESOLVED)
        self.assertNotEqual(result.resolution, "")

    def test_email_is_auto_resolved(self):
        result = _run("Outlook issue", "My email and mailbox are not loading in Outlook.")
        self.assertEqual(result.status, TicketStatus.RESOLVED)

    def test_hardware_is_escalated(self):
        result = _run("Laptop broken", "My laptop screen is cracked.")
        self.assertEqual(result.status, TicketStatus.ESCALATED)
        self.assertEqual(result.resolution, "")


class TestTicketMetadata(unittest.TestCase):
    def test_ticket_id_format(self):
        result = _run("Test", "A long enough test description to avoid low priority classification here.")
        self.assertTrue(result.ticket_id.startswith("TKT-"))
        self.assertEqual(len(result.ticket_id), 12)

    def test_log_is_populated(self):
        result = _run("VPN", "Cannot connect to the corporate VPN from home.")
        self.assertGreater(len(result.log), 0)

    def test_log_entries_have_step_key(self):
        result = _run("App crash", "The application crashes every time I try to open it.")
        for entry in result.log:
            self.assertIn("step", entry)


if __name__ == "__main__":
    unittest.main()
