from typing import Any, Dict

from requests import Response, Session


class HartwareAuthApiSession(Session):
    def __init__(self, auth_url: str):
        super(HartwareAuthApiSession, self).__init__()
        self.auth_url = auth_url

        self.access_token = ""
        self.refresh_token = ""

    def login(self, username: str, password: str) -> str:
        response = self.post(
            f"{self.auth_url}/api/v1/login/",
            data={"username": username, "password": password},
        )
        response.raise_for_status()

        self.access_token = response.json()["access_token"]
        self.refresh_token = response.json()["refresh_token"]

        self.headers["Authorization"] = f"Bearer {self.access_token}"

        return self.access_token

    def refresh(self) -> str:
        response = self.post(
            f"{self.auth_url}/api/v1/login/refresh/",
            headers={"Authorization": f"Bearer {self.refresh_token}"},
        )
        response.raise_for_status()

        self.access_token = response.json()["access_token"]

        self.headers["Authorization"] = f"Bearer {self.access_token}"

        return self.access_token

    def get_user(self) -> Dict[str, Any]:
        response = self.get(f"{self.auth_url}/api/v1/users/me/")
        response.raise_for_status()

        return dict(response.json())


class HartwareApiSession(Session):
    def __init__(self, base_url: str, auth_session: HartwareAuthApiSession):
        super(HartwareApiSession, self).__init__()

        self.base_url = base_url
        self.auth_session = auth_session

    def setup_headers(self) -> None:
        if authorization_header := self.auth_session.headers.get("Authorization"):
            self.headers["Authorization"] = authorization_header

    def request(self, method: str, url: str, **kwargs: Any) -> Response:  # type: ignore
        url = f"{self.base_url}/{url}"

        if not self.headers.get("Authorization"):
            self.setup_headers()

        response = super().request(method, url, **kwargs)

        if response.status_code == 401:
            self.auth_session.access_token = ""
            self.auth_session.refresh()

            self.setup_headers()

            response = super().request(method, url, **kwargs)

        if not response.status_code == 200:
            response.raise_for_status()

        return response
