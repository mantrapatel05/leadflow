import httpx
from app.core.config import get_settings


class MetaAPIError(Exception):
    """Raised when Meta Graph API returns an error."""


class MetaClient:
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.meta_page_access_token:
            raise MetaAPIError("Meta Page Access Token is not configured")
        self.base_url = (
            "https://graph.facebook.com/"
            f"{self.settings.meta_graph_api_version}"
        )

    async def get_lead(self, lead_id: str) -> dict:
        url = f"{self.base_url}/{lead_id}"
        params = {
            "fields": (
                "id,created_time,field_data,"
                "form_id,ad_id"
            )
        }
        headers = {
            "Authorization": (
                f"Bearer {self.settings.meta_page_access_token}"
            )
        }
        async with httpx.AsyncClient(
            timeout=self.settings.meta_api_timeout
        ) as client:
            response = await client.get(
                url, params=params, headers=headers
            )
        if response.status_code >= 400:
            raise MetaAPIError(
                f"Meta Graph API error {response.status_code}: {response.text}"
            )
        return response.json()