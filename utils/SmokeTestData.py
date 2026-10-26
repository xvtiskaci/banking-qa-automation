import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SmokeTestData:
    username: str
    password: str

    @classmethod
    def from_environment(cls):
        username = os.getenv("PARABANK_USERNAME", "").strip()
        password = os.getenv("PARABANK_PASSWORD", "")
        if not username or not password:
            raise ValueError("Missing PARABANK_USERNAME or PARABANK_PASSWORD")
        return cls(username=username, password=password)
