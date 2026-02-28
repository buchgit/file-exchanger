from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import requests
from PyQt6.QtCore import QThread, pyqtSignal

from config import BASE_URL, CHUNK_SIZE


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------

class ApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class LoginResult:
    access_token: str
    token_type: str
    force_change_password: bool


@dataclass
class UserOut:
    id: int
    username: str
    is_admin: bool
    force_change_password: bool
    created_at: str


@dataclass
class FileOut:
    id: int
    sender_id: int
    receiver_id: int
    original_filename: str
    stored_filename: str
    part_number: int
    total_parts: int
    comment: str
    status: str
    created_at: str


# ---------------------------------------------------------------------------
# ApiClient
# ---------------------------------------------------------------------------

class ApiClient:
    def __init__(self, base_url: str = BASE_URL):
        self._base_url = base_url

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    def _raise_for_status(self, resp: requests.Response) -> None:
        if resp.ok:
            return
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise ApiError(resp.status_code, str(detail))

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def login(self, username: str, password: str) -> LoginResult:
        try:
            resp = requests.post(
                f"{self._base_url}/auth/login",
                data={"username": username, "password": password},
                timeout=10,
            )
            self._raise_for_status(resp)
            data = resp.json()
            return LoginResult(
                access_token=data["access_token"],
                token_type=data["token_type"],
                force_change_password=data.get("force_change_password", False),
            )
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc

    def change_password(self, token: str, current: str, new: str) -> None:
        try:
            resp = requests.post(
                f"{self._base_url}/auth/change-password",
                json={"current_password": current, "new_password": new},
                headers=self._headers(token),
                timeout=10,
            )
            self._raise_for_status(resp)
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def list_users(self, token: str) -> list[UserOut]:
        try:
            resp = requests.get(
                f"{self._base_url}/users/",
                headers=self._headers(token),
                timeout=10,
            )
            self._raise_for_status(resp)
            return [UserOut(**u) for u in resp.json()]
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc

    def get_user(self, token: str, user_id: int) -> UserOut:
        try:
            resp = requests.get(
                f"{self._base_url}/users/{user_id}",
                headers=self._headers(token),
                timeout=10,
            )
            self._raise_for_status(resp)
            return UserOut(**resp.json())
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc

    def create_user(self, token: str, username: str, password: str, is_admin: bool) -> UserOut:
        try:
            resp = requests.post(
                f"{self._base_url}/users/",
                json={"username": username, "password": password, "is_admin": is_admin},
                headers=self._headers(token),
                timeout=10,
            )
            self._raise_for_status(resp)
            return UserOut(**resp.json())
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc

    def delete_user(self, token: str, user_id: int) -> None:
        try:
            resp = requests.delete(
                f"{self._base_url}/users/{user_id}",
                headers=self._headers(token),
                timeout=10,
            )
            self._raise_for_status(resp)
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc

    # ------------------------------------------------------------------
    # Files
    # ------------------------------------------------------------------

    def list_pending(self, token: str) -> list[FileOut]:
        try:
            resp = requests.get(
                f"{self._base_url}/files/pending",
                headers=self._headers(token),
                timeout=10,
            )
            self._raise_for_status(resp)
            return [FileOut(**f) for f in resp.json()]
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc

    def upload_part(
        self,
        token: str,
        file_path: str,
        receiver_id: int,
        original_filename: str,
        part_number: int,
        total_parts: int,
        comment: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> FileOut:
        try:
            with open(file_path, "rb") as fh:
                resp = requests.post(
                    f"{self._base_url}/files/upload",
                    headers=self._headers(token),
                    data={
                        "receiver_id": str(receiver_id),
                        "original_filename": original_filename,
                        "part_number": str(part_number),
                        "total_parts": str(total_parts),
                        "comment": comment,
                    },
                    files={"file": (original_filename, fh)},
                    timeout=300,
                )
            if progress_callback:
                import os
                progress_callback(os.path.getsize(file_path))
            self._raise_for_status(resp)
            return FileOut(**resp.json())
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc

    def download_part(
        self,
        token: str,
        file_id: int,
        part_n: int,
        dest_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> None:
        try:
            resp = requests.get(
                f"{self._base_url}/files/{file_id}/part/{part_n}",
                headers=self._headers(token),
                stream=True,
                timeout=300,
            )
            self._raise_for_status(resp)
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        if progress_callback:
                            progress_callback(len(chunk))
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc

    def ack_file(self, token: str, file_id: int) -> None:
        try:
            resp = requests.post(
                f"{self._base_url}/files/{file_id}/ack",
                headers=self._headers(token),
                timeout=10,
            )
            self._raise_for_status(resp)
        except ApiError:
            raise
        except requests.RequestException as exc:
            raise ApiError(0, str(exc)) from exc


# ---------------------------------------------------------------------------
# ApiWorker
# ---------------------------------------------------------------------------

class ApiWorker(QThread):
    result = pyqtSignal(object)
    error = pyqtSignal(int, str)

    def __init__(self, fn, *args, parent=None, **kwargs):
        super().__init__(parent)
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            self.result.emit(self._fn(*self._args, **self._kwargs))
        except ApiError as e:
            self.error.emit(e.status_code, e.detail)
        except Exception as e:
            self.error.emit(0, str(e))
