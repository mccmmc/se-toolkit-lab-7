"""LMS API client — wraps HTTP calls to the backend."""

import httpx

from config import BotConfig


class APIError(Exception):
    """Raised when the API request fails."""

    def __init__(self, status_code: int | None, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class APIClient:
    """HTTP client for the LMS backend.

    All methods raise APIError on failure — callers must handle this.
    """

    def __init__(self, config: BotConfig | None = None):
        self.config = config or BotConfig()
        self.base_url = self.config.lms_api_base_url.rstrip("/")
        self.api_key = self.config.lms_api_key

    def _headers(self) -> dict[str, str]:
        """Return headers with Bearer auth."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_items(self) -> list[dict]:
        """GET /items/ — returns labs and tasks."""
        return self._request("GET", "/items/")

    def get_pass_rates(self, lab: str) -> list[dict]:
        """GET /analytics/pass-rates?lab=<lab> — per-task pass rates."""
        return self._request("GET", "/analytics/pass-rates", params={"lab": lab})

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
    ) -> list[dict] | dict:
        """Make an HTTP request to the backend.

        Raises APIError with a user-friendly message on failure.
        """
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.request(
                    method, url, headers=self._headers(), params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise APIError(
                None,
                f"connection refused ({self.base_url}). Check that the services are running.",
            ) from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                e.response.status_code,
                f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.",
            ) from e
        except httpx.TimeoutException:
            raise APIError(
                None,
                f"request timed out ({self.base_url}). The backend may be overloaded.",
            ) from e
