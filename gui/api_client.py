import requests


class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.access_token = None

    def _headers(self, extra=None):
        headers = (extra or {}).copy()
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def get(self, endpoint, **kwargs):
        return requests.get(f"{self.base_url}{endpoint}", headers=self._headers(kwargs.pop("headers", None)), **kwargs)

    def post(self, endpoint, **kwargs):
        return requests.post(f"{self.base_url}{endpoint}", headers=self._headers(kwargs.pop("headers", None)), **kwargs)

    def patch(self, endpoint, **kwargs):
        return requests.patch(f"{self.base_url}{endpoint}", headers=self._headers(kwargs.pop("headers", None)), **kwargs)

    def delete(self, endpoint, **kwargs):
        return requests.delete(f"{self.base_url}{endpoint}", headers=self._headers(kwargs.pop("headers", None)), **kwargs)

    def logout(self):
        if self.access_token:
            try:
                self.post("/auth/logout")
            except Exception:
                pass
            self.access_token = None
