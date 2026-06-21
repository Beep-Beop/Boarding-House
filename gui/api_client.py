import os
import requests


class APIClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "https://BeepBeop-boarding-house-api.hf.space")
        self.access_token = None
        self.default_timeout = 10
        self.on_unauthorized = None

    def _headers(self, extra=None):
        headers = (extra or {}).copy()
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(self, method, endpoint, **kwargs):
        kwargs.setdefault("timeout", self.default_timeout)
        response = method(f"{self.base_url}{endpoint}", headers=self._headers(kwargs.pop("headers", None)), **kwargs)
        if response.status_code == 401 and self.on_unauthorized:
            self.on_unauthorized(response)
        return response

    def get(self, endpoint, **kwargs):
        return self._request(requests.get, endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._request(requests.post, endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self._request(requests.put, endpoint, **kwargs)

    def patch(self, endpoint, **kwargs):
        return self._request(requests.patch, endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request(requests.delete, endpoint, **kwargs)

    def logout(self):
        if self.access_token:
            try:
                self.post("/auth/logout")
            except Exception:
                pass
            self.access_token = None
