import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class GraphClient:
    def __init__(self, tenant_id: str = None, client_id: str = None, client_secret: str = None):
        self.tenant_id = tenant_id or os.getenv("TENANT_ID")
        self.client_id = client_id or os.getenv("CLIENT_ID")
        self.client_secret = client_secret or os.getenv("CLIENT_SECRET")
        self.access_token: Optional[str] = None

    def authenticate(self) -> bool:
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }
        response = requests.post(url, data=payload, timeout=15)
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            return True
        return False

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def get_user(self, user_id: str) -> Optional[dict]:
        response = requests.get(f"{GRAPH_BASE_URL}/users/{user_id}", headers=self._headers(), timeout=15)
        return response.json() if response.status_code == 200 else None

    def send_teams_message(self, team_id: str, channel_id: str, content: str) -> bool:
        url = f"{GRAPH_BASE_URL}/teams/{team_id}/channels/{channel_id}/messages"
        payload = {"body": {"contentType": "html", "content": content}}
        response = requests.post(url, json=payload, headers=self._headers(), timeout=15)
        return response.status_code == 201

    def create_list_item(self, site_id: str, list_id: str, fields: dict) -> Optional[dict]:
        url = f"{GRAPH_BASE_URL}/sites/{site_id}/lists/{list_id}/items"
        response = requests.post(url, json={"fields": fields}, headers=self._headers(), timeout=15)
        return response.json() if response.status_code == 201 else None

    def get_list_items(self, site_id: str, list_id: str, filter_query: str = "") -> list:
        url = f"{GRAPH_BASE_URL}/sites/{site_id}/lists/{list_id}/items?expand=fields"
        if filter_query:
            url += f"&$filter={filter_query}"
        response = requests.get(url, headers=self._headers(), timeout=15)
        return response.json().get("value", []) if response.status_code == 200 else []

    def update_list_item(self, site_id: str, list_id: str, item_id: str, fields: dict) -> bool:
        url = f"{GRAPH_BASE_URL}/sites/{site_id}/lists/{list_id}/items/{item_id}/fields"
        response = requests.patch(url, json=fields, headers=self._headers(), timeout=15)
        return response.status_code == 200
