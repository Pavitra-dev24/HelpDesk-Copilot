import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "graph-api"))

from graph_client import GraphClient


def _client():
    c = GraphClient(tenant_id="t", client_id="c", client_secret="s")
    c.access_token = "tok"
    return c


class TestAuthentication(unittest.TestCase):
    @patch("graph_client.requests.post")
    def test_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"access_token": "tok123"})
        c = GraphClient(tenant_id="t", client_id="c", client_secret="s")
        self.assertTrue(c.authenticate())
        self.assertEqual(c.access_token, "tok123")

    @patch("graph_client.requests.post")
    def test_failure_returns_false(self, mock_post):
        mock_post.return_value = MagicMock(status_code=401, json=lambda: {})
        c = GraphClient(tenant_id="t", client_id="c", client_secret="s")
        self.assertFalse(c.authenticate())
        self.assertIsNone(c.access_token)

    def test_headers_include_bearer(self):
        c = _client()
        self.assertEqual(c._headers()["Authorization"], "Bearer tok")


class TestUserOps(unittest.TestCase):
    @patch("graph_client.requests.get")
    def test_get_user_success(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"displayName": "Jane Doe"})
        self.assertEqual(_client().get_user("jane@co.com")["displayName"], "Jane Doe")

    @patch("graph_client.requests.get")
    def test_get_user_not_found(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404)
        self.assertIsNone(_client().get_user("unknown@co.com"))


class TestTeamsOps(unittest.TestCase):
    @patch("graph_client.requests.post")
    def test_send_message_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201)
        self.assertTrue(_client().send_teams_message("team1", "ch1", "hello"))

    @patch("graph_client.requests.post")
    def test_send_message_failure(self, mock_post):
        mock_post.return_value = MagicMock(status_code=403)
        self.assertFalse(_client().send_teams_message("team1", "ch1", "hello"))


class TestSharePointOps(unittest.TestCase):
    @patch("graph_client.requests.post")
    def test_create_item_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {"id": "item1"})
        result = _client().create_list_item("s", "l", {"Title": "TKT-001"})
        self.assertEqual(result["id"], "item1")

    @patch("graph_client.requests.post")
    def test_create_item_failure(self, mock_post):
        mock_post.return_value = MagicMock(status_code=400, json=lambda: {})
        self.assertIsNone(_client().create_list_item("s", "l", {}))

    @patch("graph_client.requests.get")
    def test_get_items_returns_list(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"value": [{}, {}]})
        self.assertEqual(len(_client().get_list_items("s", "l")), 2)

    @patch("graph_client.requests.get")
    def test_get_items_failure_returns_empty(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500)
        self.assertEqual(_client().get_list_items("s", "l"), [])

    @patch("graph_client.requests.patch")
    def test_update_item_success(self, mock_patch):
        mock_patch.return_value = MagicMock(status_code=200)
        self.assertTrue(_client().update_list_item("s", "l", "i1", {"Status": "resolved"}))

    @patch("graph_client.requests.patch")
    def test_update_item_failure(self, mock_patch):
        mock_patch.return_value = MagicMock(status_code=404)
        self.assertFalse(_client().update_list_item("s", "l", "bad", {}))


if __name__ == "__main__":
    unittest.main()
